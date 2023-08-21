from enum import Enum

from services.graph_composer import EdgeType
import config
if config.mini_graph:
    from graphs.minecraft.mini_graph_dict import graph_dict
else:
    from graphs.minecraft.big_graphs import graph_dict

import networkx as nx

class LENSE_TYPES(str, Enum):
    ONLY_INVENTORY_MINING_ITEMS = "only_inventory_mining_items"
    IN_OBSERVATION = "in_observation"
    IN_INVENTORY = "in_inventory"
    ONLY_TRADES = "only_trades"
    ONLY_BID = "only_bid"
    ONLY_ASK = "only_ask"


only_trades = lambda x: True if 'action' in x[0] and 'trade' not in x[0] else False
only_bid = lambda x: True if x[0] == 'trade:ask' else False
only_ask = lambda x: True if x[0] == 'trade:bid' else False

lenses = {
    LENSE_TYPES.ONLY_INVENTORY_MINING_ITEMS: {'source': lambda x: 'items:' in x[0],
                                         'condition': lambda x:
                                         'pickaxe' not in x[1]['props']['name'] or x[1]['props']['name'] in [n[1]['props']['name'] for n in g.inventory_graph.nodes(data=True)]},
    LENSE_TYPES.IN_OBSERVATION: {'source': lambda x: (x[1].get('source') or '') in ['entities', 'items'],
                            'condition': lambda x: x[1]['props']['name'] in [n[1]['props']['name'] for n in g.observations_graph.nodes(data=True)]},
    LENSE_TYPES.IN_INVENTORY: {'source': lambda x: (x[1].get('source') or '') in ['blocks', 'items'],
                          'condition': lambda x: x[1]['props']['name'] in [n[1]['props']['name'] for n in g.inventory_graph.nodes(data=True)]},
    LENSE_TYPES.ONLY_TRADES: {'source': lambda x: x,
                                'condition': only_trades },
    LENSE_TYPES.ONLY_BID: {'source': lambda x: x,
                                'condition': only_bid },
    LENSE_TYPES.ONLY_ASK: {'source': lambda x: x,
                                'condition': only_ask }
    # 'can_obtain': {}
}

linking_instructions = [
    {
        'source': 'blocks',
        'target': 'items',
        'link': lambda s, t: t['props']['name'] in s['props']['drops'],
        'type': EdgeType.PROVIDES
    },
    {
        'source': 'items',
        'target': 'blocks',
        'link': lambda s, t: s['props']['name'] in t['props']['requires'],
        'type': EdgeType.NEEDS
    },
    {
        'source': 'items',
        'target': 'foods',
        'link': lambda s, t: s['props']['name'] == t['props']['name'],
        'type': EdgeType.PROVIDES
    },
    {
        'source': 'agent',
        'target': 'goals',
        'link': lambda s, t: True,  # all goals are linked to all actions
        'type': EdgeType.GOAL
    },
]

joins = {
    "actions": {
        "mine": [{'index': 'items', 'filter': lambda x, y: 'pickaxe' in x.get('name'), 'type': EdgeType.NEEDS, 'join':
                  {'index': 'blocks', 'filter': lambda x, y: x.get('material') == 'mineable/pickaxe', 'type': EdgeType.ACT_UPON}}],
        "collect": [{'index': 'observations', 'filter': lambda x, y: x['type'] in ['item', 'block'], 'type': EdgeType.OBSERVED }],
        "fight": [{'index': 'entities', 'filter': lambda x, y: x['type'] == 'Hostile mobs', 'type': EdgeType.OBSERVED}],
        "hunt": [{'index': 'entities', 'filter': lambda x, y: x['type'] == 'Passive mobs', 'type': EdgeType.OBSERVED}],
        "eat": [{'index': 'foods', 'filter': lambda x, y: x['food_points'] > 0, 'type': EdgeType.NEEDS}],
        "craft": [{'index': 'recipes', 'filter': lambda x, y: x, 'type': EdgeType.ACT_UPON}],
        "trade": [{'index': 'trade', 'filter': lambda x, y: 'bid' in x['name'] or 'ask' in x['name'], 'type': EdgeType.ACT_UPON}]
    },
    "trade": {
        "bid": [{ 'index': 'trade', 'filter': lambda x, y: 'debit' == x['name'], 'type': EdgeType.ACCRUE,
                  'join': {'index': 'items', 'filter': lambda x, y: x, 'type': EdgeType.PROVIDES }  }],
        "ask": [{ 'index': 'inventory', 'filter': lambda x, y: x, 'type': EdgeType.NEEDS,
                   'join': {'index': 'trade', 'filter': lambda x, y: 'credit' == x['name'], 'type': EdgeType.PROVIDES } }],
        "debit": [],
        "credit": [],
        "money": []
    },
    'recipes': {
        'all': [{'index': 'items', 'filter': lambda x, y: x['name'] == y['provides']['name'], 'type': EdgeType.PROVIDES}]
         #   {'index': 'items', 'filter': lambda x, y: x['name'] in [z['name'] for z in y['needs']], 'type': EdgeType.NEEDS,
          #       'join': {'index': 'items', 'filter': lambda x, y: x['name'] == y['provides']['name'], 'type': EdgeType.PROVIDES}}]
    },
    'foods': {
        'all': [{ 'index': 'foods', 'filter': lambda x,y: x['name'] != 'food' and y['name'] == 'food', 'type': EdgeType.PROVIDES }]
    }
}
#x= Joins(**mjoins)
#x.make_strings()
#print(x)

def get_join(graph, action):
    if graph in joins and action in joins[graph]:
        return joins[graph][action]
    print("Invalid Join", action)
    return []


def rjoin(x): return get_join("recipes", x)
def ajoin(x): return get_join("actions", x)
def tjoin(x): return get_join("trade", x)
def fjoin(x): return get_join("foods", x)


def apply_joins(ajoin, graph, all_name=None):
    for a, d in graph.nodes(data=True):
        d['props']['joins'] = ajoin(a if not all_name else all_name)
        for j in d['props']['joins']:
            j['source_name'] = a
        nx.set_node_attributes(graph, {a: d})


#apply_joins(ajoin, graph_dict['actions'])
#apply_joins(tjoin, graph_dict['trade'])

apply_joins(rjoin, graph_dict['recipes'], all_name='all')
apply_joins(fjoin, graph_dict['foods'], all_name='all')

one_to_many_join_graphs = {
    'sources': [
        ('actions',
         graph_dict['actions']),
        ('trade',
         graph_dict['trade']),
        ('inventory',
         graph_dict['inventory']),
        ('observations',
         graph_dict['observations']),
        ('recipes',
         graph_dict['recipes']),
        ('foods',
         graph_dict['foods'])],
    'on': graph_dict}

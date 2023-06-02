from enum import Enum

from services.graph_composer import EdgeType
from services.graph_dict import graph_dict
import networkx as nx

class LENSES(str, Enum):
    ONLY_INVENTORY_MINING_ITEMS = "only_inventory_mining_items"
    IN_OBSERVATION = "in_observation"
    IN_INVENTORY = "in_inventory"
    EXCLUDE_ASK_TRADES = "exclude_ask_trades"

lenses = {
    LENSES.ONLY_INVENTORY_MINING_ITEMS: { 'source': lambda x: 'items:' in x[0],
                                     'condition': lambda x: 
                                         'pickaxe' not in x[1]['props']['name'] or x[1]['props']['name'] in [n[1]['props']['name'] for n in g.inventory_graph.nodes(data=True)] },
    LENSES.IN_OBSERVATION: { 'source': lambda x: (x[1].get('source') or '') in ['entities', 'items'], 
                        'condition': lambda x: x[1]['props']['name'] in [n[1]['props']['name'] for n in g.observations_graph.nodes(data=True)] },
    LENSES.IN_INVENTORY: {'source': lambda x: (x[1].get('source') or '') in ['blocks', 'items'], 
                        'condition': lambda x: x[1]['props']['name'] in [n[1]['props']['name'] for n in g.inventory_graph.nodes(data=True)] },
    LENSES.EXCLUDE_ASK_TRADES: { 'source': lambda x: 'trade:ask' == x[0], 
                                     'condition': lambda x: False }
    #'can_obtain': {}
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
        'target': 'food',
        'link': lambda s, t: s['props']['name'] == t['props']['name'],
        'type': EdgeType.PROVIDES
    },
    {
        'source': 'agent',
        'target': 'goals',
        'link': lambda s, t: True, # all goals are linked to all actions
        'type': EdgeType.GOAL
    },
    {
        'source': 'goals',
        'target': 'actions',
        'link': lambda s, t: True, # all goals are linked to all actions
        'type': EdgeType.ACTION
        # todo get agent actions t['props']['name'] in s['props']['actions']
    },
]

joins = {
  "actions": {
    "mine": [{'index': 'items', 'filter': lambda x,y: 'pickaxe' in x.get('name'), 'type': EdgeType.NEEDS, 'join': 
    { 'index': 'blocks', 'filter': lambda x,y: x.get('material') == 'mineable/pickaxe', 'type': EdgeType.ACT_UPON } }],
    "collect": [{ 'index': 'items', 'filter': lambda x,y: x, 'type': EdgeType.OBSERVED } ],
    "fight": [{'index': 'entities', 'filter': lambda x,y: x['type'] == 'Hostile mobs', 'type': EdgeType.OBSERVED } ],
    "hunt": [{ 'index': 'entities', 'filter': lambda x,y: x['type'] == 'Passive mobs','type': EdgeType.OBSERVED }],
    "eat": [{ 'index': 'foods', 'filter': lambda x,y: x['food_points'] > 0, 'type': EdgeType.NEEDS }],
    "craft":  [{'index': 'recipes', 'filter': lambda x,y: x, 'type': EdgeType.ACT_UPON }],
    "trade": [{ 'index': 'trade', 'filter': lambda x,y: 'bid' in x['name'] or 'ask' in x['name'], 'type': EdgeType.ACT_UPON }]
  },
  "trade": {
    "bid": [{'index': 'trade', 'filter': lambda x,y: 'debit' == x['name'], 'type': EdgeType.ACT_UPON }],
    "ask": [{'index': 'trade', 'filter': lambda x,y: 'credit' == x['name'], 'type': EdgeType.ACT_UPON  }],
    "debit": [{ 'index': 'trade', 'filter': lambda x,y: x['name'] == 'money', 'type': EdgeType.NEEDS } ],
    "credit": [{ 'index': 'inventory', 'filter': lambda x,y: x, 'type': EdgeType.NEEDS },
               { 'index': 'trade', 'filter': lambda x,y: 'money' == x['name'], 'type': EdgeType.PROVIDES  }],
    "money": [{ 'index': 'items', 'filter': lambda x,y: x, 'type': EdgeType.PROVIDES }]
  },
  'recipes': {
      'all': [{ 'index': 'items', 'filter': lambda x,y: x['name'] in [z['name'] for z in y['needs']] , 'type': EdgeType.NEEDS, 
                          'join': {'index': 'items', 'filter': lambda x,y: x['name'] == y['provides']['name'], 'type': EdgeType.PROVIDES } }]
  }
}

def get_join(graph, action):
    if graph in joins and action in joins[graph]:
      return joins[graph][action]
    print("Invalid Join")
    return []

rjoin = lambda x: get_join("recipes", x)
ajoin = lambda x: get_join("actions", x)
tjoin = lambda x: get_join("trade", x)

def apply_joins(ajoin, graph, all_name = None):
    for a, d in graph.nodes(data=True):
        d['props']['joins'] = ajoin(a if not all_name else all_name)
        nx.set_node_attributes(graph, { a: d })

apply_joins(ajoin, graph_dict['actions'])
apply_joins(tjoin, graph_dict['trade'])
apply_joins(rjoin, graph_dict['recipes'], all_name='all')

one_to_many_join_graphs = { 'sources': [('actions', graph_dict['actions']), ('trade', graph_dict['trade']), ('inventory', graph_dict['inventory']), ('recipes', graph_dict['recipes'])], 'on': graph_dict }


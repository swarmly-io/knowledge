from enum import Enum

from sample_graph.graph_composer import EDGE_TYPE
import sample_graph.graphs as g

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
        'type': EDGE_TYPE.PROVIDES
    },
    {
        'source': 'items',
        'target': 'blocks',
        'link': lambda s, t: s['props']['name'] in t['props']['requires'],
        'type': EDGE_TYPE.NEEDS
    },
    {
        'source': 'items',
        'target': 'food',
        'link': lambda s, t: s['props']['name'] == t['props']['name'],
        'type': EDGE_TYPE.PROVIDES
    },
    {
        'source': 'agent',
        'target': 'goals',
        'link': lambda s, t: True, # all goals are linked to all actions
        'type': EDGE_TYPE.GOAL
    },
    {
        'source': 'goals',
        'target': 'actions',
        'link': lambda s, t: True, # all goals are linked to all actions
        'type': EDGE_TYPE.ACTION
        # todo get agent actions t['props']['name'] in s['props']['actions']
    },
]

graph_dict = {'blocks': g.blocks_graph, 
                          'items': g.items_graph, 
                          'food': g.food_graph, 
                          'actions': g.actions_graph, 
                          'agent': g.agent_graph,
                          'inventory': g.inventory_graph,
                          'goals': g.goals_graph,
                          'trade': g.trade_graph,
                          'recipes': g.recipes_graph }

one_to_many_join_graphs = { 'sources': [('actions', g.actions_graph), ('trade', g.trade_graph), ('inventory', g.inventory_graph), ('recipes', g.recipes_graph)], 'on': graph_dict }

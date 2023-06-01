import networkx as nx
from sample_graph.graph_composer import EdgeType
from sample_graph.mini_graphs import inventory_graph, observations_graph

initial_state = {
    'observations': [
        { 'id': 1, 'name': 'zombie', 'position': (0,0,0), 'type': 'Hostile mobs' },  # should resolve these to entities entries - cache
        { 'id': 2, 'name': 'zombie', 'position': (0,0,1), 'type': 'Hostile mobs' },  
    ],
    'inventory': [
        { 'id': 1, 'name': 'plank', 'quantity': 1 },
        { 'id': 1, 'name': 'stick', 'quantity': 1 }
    ],
    'blockNearBy': lambda x: True if x == 'blocks:stone' else False
}

def state_to_graph(state):
    for o in state['observations']:
        key = str(o['id']) + ':' + o['name']
        observations_graph.add_node(key, props=o)
    
    for i in state['inventory']:
        key = str(i['id']) + ':' + i['name']
        joins = [{ 'index': 'items', 'filter': 
            lambda x, y: x['name'] == i['name'], 'type': EdgeType.PROVIDES }]
        inventory_graph.add_node(key, props={ **i, 'joins': joins })
    
state_to_graph(initial_state)
import networkx as nx
from services.graph_composer import EdgeType
from services.mini_graphs import inventory_graph, observations_graph

initial_state = {
    'observations': [
        # should resolve these to entities entries - cache
        {'id': 1, 'name': 'zombie', 'position': (
            0, 0, 0), 'type': 'Hostile mobs'},
        {'id': 2, 'name': 'zombie', 'position': (
            0, 0, 1), 'type': 'Hostile mobs'},
        {'id': 3, 'name': 'wooden_pickaxe', 'position': (
            0, 0, 1), 'type': 'item' },
    ],
    'inventory': [
        {'id': 1, 'name': 'plank', 'quantity': 1},
        {'id': 1, 'name': 'stick', 'quantity': 1},
        {'id': 1, 'name': 'wooden_pickaxe', 'quantity': 1}

    ],
    'blockNearBy': lambda x: True if x == 'blocks:stone' else False
}


def state_to_graph(state):    
    for o in state['observations']:
        key = str(o['id']) + ':' + o['name']
        if o['type'] == "item":
            observations_graph.add_node(key, props={ **o, 'joins': [{ 'index': 'items', 'filter': lambda x,y: x['name'] == o['name'], 'type': EdgeType.PROVIDES }] } )
        else:
            observations_graph.add_node(key, props={ **o, 'joins': [] } )

    for i in state['inventory']:
        key = str(i['id']) + ':' + i['name']
        # todo adaptive edge type, it should be the same as the previous edge
        joins = [{'index': 'items',
                  'filter': lambda x,
                  y: x['name'] == y['name'],
                  'type': EdgeType.PROVIDES }]
        inventory_graph.add_node(key, props={**i, 'joins': joins})


def run_state():
    state_to_graph(initial_state)
    print("Ran State")
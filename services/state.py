import json
import networkx as nx
from models.agent_state import AgentMCState
from services.graph_composer import EdgeType
from services.mini_graphs import inventory_graph, observations_graph

with open("./services/samplestate.json", 'r') as f:
    initial_state = AgentMCState(**json.loads(f.read()))

# todo lookup k in items lookup
items_lookup = {
    "701": "wooden_pickaxe"
}

def inventory_state_runner(state: AgentMCState, inventory_graph):
    inventory_graph.clear()
    
    inv_state = state.inventory.items
    for k, i in inv_state.items():
        name = items_lookup.get(k)
        if not name:
            print(f"Couldn't find item {k}")
            continue
        
        key = f"{k}:{name}"
        joins = [{'index': 'items',
                  'filter': lambda x,
                  y: x['name'] == y['name'],
                  'type': EdgeType.PROVIDES }]
        
        inventory_graph.add_node(key, props={**{ k: i, 'name': name }, 'joins': joins}) 
    
def observation_state_runner(state: AgentMCState, observations_graph):
    # do to this should include items laying on the ground
    obs_state = state.closeEntities
    observations_graph.clear()
    for o in obs_state:
        key = str(o.id) + ':' + o.name
        if o.type == "item":
            # todo join should be defined in agent config
            observations_graph.add_node(key, props={ **o.dict(), 'joins': [{ 'index': 'items', 'filter': lambda x,y: x['name'] == o['name'], 'type': EdgeType.PROVIDES }] } )
        else:
            observations_graph.add_node(key, props={ **o.dict(), 'joins': [], 'type': EdgeType.OBSERVED } )


# todo foods, tools, weapons etc.
def state_to_graph(inventory_graph, observations_graph, state: AgentMCState):
    inventory_state_runner(state, inventory_graph)
    print("ran inventory state")
    observation_state_runner(state, observations_graph)
    print("ran observation state")
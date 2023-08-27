from models.agent_state import AgentMCState
from services.graph_composer import EdgeType
from services.state import StateRunner

import config
if config.mini_graph:
    from graphs.minecraft.mini_indexes import indexes
    
    def get_index(name):
        index = {}
        for k,v in indexes[name].items():
            v = f'{name}:{v}'
            index[k] = v
        return index
else:
    from graphs.minecraft.big_graphs import graph_dict, indexes
    def get_index(name):
        index = {}
        for k,v in indexes[name].items():
            id = v['id']
            vname = v['name']
            v = f'{name}:{vname}'
            index[int(id)] = v
        return index

class MinecraftStateRunner(StateRunner):
    def __init__(self):
        self.items_lookup = { **get_index('items'), **get_index('foods') }
        self.hostiles_lookup = indexes['hostiles']
    
    
    def inventory_state_runner(self, state: AgentMCState, inventory_graph):
        inventory_graph.clear()
        
        #todo fix
        inv_state = state.inventory.items
        for k, i in inv_state.items():
            name = self.items_lookup.get(int(k))
            if not name:
                print(f"Couldn't find item {k}")
                continue
            
            ind, val = name.split(':')
            joins = [{'index': ind,
                    'filter': lambda x,
                    y: x['name'] == y['name'],
                    'type': EdgeType.CONTAINS }]
            
            inventory_graph.add_node(f"{val}", props={**{ 'quantity': i, 'name': val }, 'joins': joins}) 
        
    def observation_state_runner(self, state: AgentMCState, observations_graph):
        # do to this should include items laying on the ground
        obs_state = state.closeEntities
        observations_graph.clear()
        for o in obs_state:
            if o.type == "item":
                name = self.items_lookup.get(int(o.id))
                ind, val = name.split(':')

                joins = [{'index': ind,
                    'filter': lambda x,
                    y: x['name'] == y['name'],
                    'type': EdgeType.PROVIDES }]
                
                # todo join should be defined in agent config
                observations_graph.add_node(f"{val}", props={ **{ 'name': val }, 'joins': joins })
            if o.type == 'mob':
                type = self.hostiles_lookup.get(o.name)
                if not type:
                    print(f"{o.name} entity not found")
                    continue
                
                # todo provides isnt correct word
                joins = [{'index': 'entities',
                    'filter': lambda x,
                    y: x['name'] == y['name'],
                    'type': EdgeType.DETECTS }]
                observations_graph.add_node(f"{o.name}", props={ **{ 'name': o.name, 'type': o.type }, 'joins': joins } )


    # todo foods, tools, weapons etc.
    def state_to_graph(self, inventory_graph, observations_graph, state: AgentMCState):
        self.inventory_state_runner(state, inventory_graph)
        print("ran inventory state")
        self.observation_state_runner(state, observations_graph)
        print("ran observation state")
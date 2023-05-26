from typing import List, Optional
import networkx as nx
import matplotlib.pyplot as plt

from utils import bfs_subgraph, dfs_paths, get_edges_in_order, graph_from_paths, graph_diff

class GraphComposer:
    def __init__(self, graph_dict, linking_instructions, join_graphs, lenses):
        self.graph_dict = graph_dict
        self.linking_instructions = linking_instructions
        self.composed_graph = nx.DiGraph()
        self.join_graphs = join_graphs
        self.lenses = lenses

    def compose_graphs(self):
        for linking_instruction in self.linking_instructions:
            self._link_graphs(linking_instruction)
            
        for source_name, f_graph in self.join_graphs['sources']:
            self.one_to_many_joins(source_name, f_graph)

    def one_to_many_joins(self, source_name, f_graph):
        for n in f_graph.nodes(data=True):
            if not n[1]['props'].get('joins'):
                continue
            
            joins = n[1]['props']['joins']
            for join in joins:
                index, filter_fn, sub_joins, graph = self.get_join_info(join)
                if not graph:
                    continue

                filtered_nodes = [node for node in graph.nodes(data=True) if filter_fn(node[1]['props'])]
                for nt in filtered_nodes:
                    new_source = source_name + ":" + n[0]
                    new_target = index + ":" + nt[0]
                    self.composed_graph.add_edge(new_source, new_target)
                    
                if sub_joins:
                    new_index, filter_fn, _, graph = self.get_join_info(sub_joins)
                    new_filtered_nodes = [node for node in graph.nodes(data=True) if filter_fn(node[1]['props'])]
                    for nt in filtered_nodes:
                        for nft in new_filtered_nodes:
                                new_source = index + ":" + nt[0]
                                new_target = new_index + ":" + nft[0]
                                self.composed_graph.add_edge(new_source, new_target)
                    

    def get_join_info(self, join):
        index = join['index']
        filter_fn = join['filter']
        sub_joins = join.get('join')
        graph = self.join_graphs['on'].get(index)
        return index,filter_fn,sub_joins,graph
                    
                        
                        
    def _link_graphs(self, linking_instruction):
        target = linking_instruction['target']
        source = linking_instruction['source']
        link = linking_instruction['link']
        target_graph = self.graph_dict[target]
        source_graph = self.graph_dict[source]
        
        for source_node in source_graph.nodes(data=True):
            target_nodes = filter(lambda x: x if link(source_node[1], x[1]) else None, target_graph.nodes(data=True))
            for target_node in target_nodes:
                new_source = source + ":" + source_node[0]
                new_target = target + ":" + target_node[0]
                source_data = { **source_node[1], 'source': source }
                target_data = { **target_node[1], 'source': target }
                self.composed_graph.add_node(new_source, **source_data)
                self.composed_graph.add_node(new_target, **target_data)
                
                self.composed_graph.add_edge(new_source, new_target)
                
    def apply_lenses(self, lense_names: List[str], graph: Optional[nx.DiGraph]):
        # create a sub graph based on the lense
        G: nx.DiGraph = graph or self.composed_graph
        nodes = G.nodes(data=True)
        new_nodes = []
        for lense_name in lense_names:
            lense = self.lenses[lense_name]
            for n in nodes:
                if lense['source'](n):
                    if lense['condition'](n):
                        new_nodes.append(n)              
                else:
                    new_nodes.append(n)
        
        T = nx.DiGraph()
        for n in new_nodes:
            T.add_node(n[0], **n[1])
            
        filtered_edges = [(u, v) for (u, v) in G.edges() if u in T.nodes() and v in T.nodes()]
        T.add_edges_from(filtered_edges)
        return T
                
    def get_composed_graph(self):
        return self.composed_graph

blocks_graph = nx.Graph()
blocks_graph.add_node('cobblestone', props={'drops': ['stone'], 'requires': ['wooden_pickaxe', 'stone_pickaxe'], 'material': 'mineable/pickaxe'})
blocks_graph.add_node('dirt', props={'drops': ['dirt'], 'requires':[], 'material': 'mineable/shovel'})
blocks_graph.add_node('wood', props={'drops': ['wood'], 'requires':[], 'material': 'mineable/axe' })
blocks_graph.add_node('carrot', props={'drops': ['carrot'], 'requires':[], 'material': 'mineable/axe' })

items_graph = nx.Graph()
items_graph.add_node('stone', props={'name': 'stone' })
items_graph.add_node('dirt', props={'name': 'dirt' })
items_graph.add_node('wood', props={'name': 'wood' })
items_graph.add_node('carrot', props={'name': 'carrot' })
items_graph.add_node('stone_pickaxe', props={'name': 'stone_pickaxe'})
items_graph.add_node('wooden_pickaxe', props={'name': 'wooden_pickaxe'})
items_graph.add_node('stick', props={'name': 'stick'})
items_graph.add_node('plank', props={'name': 'plank'})

recipes_graph = nx.Graph()
recipes_graph.add_node('wooden_pickaxe', props = { 'provides': { 'quantity': 1, 'name': 'wooden_pickaxe' },'needs': [{ 'name': 'stick', 'quantity': 2 }, { 'name': 'plank', 'quantity': 3 }] })
recipes_graph.add_node('stick', props = { 'provides': { 'quantity': 4, 'name': 'stick' }, 'needs': [{ 'name': 'plank', 'quantity': 2 }] })
recipes_graph.add_node('plank', props = { 'provides': { 'quantity': 4, 'name': 'plank' }, 'needs': [{ 'name': 'wood', 'quantity': 1 }] })

food_graph = nx.Graph()
food_graph.add_node('apple', props={'name': 'apple'})
food_graph.add_node('bread', props={'name': 'bread'})
food_graph.add_node('carrot', props={'name': 'carrot'})


"""yaml
    actions:
     - name: mine
       joins:
         - index: items
           filter:
              when: pickaxe
              in: name
           join:
              index: blocks
              filter:
                 when: material
                 eq: mineable/pickaxe
     - name: collect
       joins:
        - index: items
          filter:
"""

# todo action -> item (pickaxe) -> block
mine_joins = [
    {'index': 'items', 'filter': lambda x: 'pickaxe' in x.get('name'), 
     'join': {'index': 'blocks', 'filter': lambda x: x.get('material') == 'mineable/pickaxe' } }]

actions_graph = nx.Graph()

actions_graph.add_node('mine', props = { 'name': 'mine', 
                                        'joins': mine_joins })
actions_graph.add_node('collect', props = { 'name': 'collect', 'joins': [{ 'index': 'items', 'filter': lambda x: x } ] })
actions_graph.add_node('fight', props = { 'name':'fight', 'joins': [{'index': 'entities', 'filter': lambda x: x['type'] == 'Hostile mobs'} ] })
actions_graph.add_node('hunt', props = { 'name':'hunt', 'joins': [{ 'index': 'entities', 'filter': lambda x: x['type'] == 'Passive mobs' }] })
actions_graph.add_node('eat', props = { 'name':'eat', 'joins': [{ 'index': 'foods', 'filter': lambda x: x['food_points'] > 0 }] })
actions_graph.add_node('craft', props = { 'name':'craft', 'joins': [{'index': 'recipes', 'filter': lambda x: x }] })
actions_graph.add_node('trade', props={ 'name': 'trade', 'joins': [{ 'index': 'trade', 'filter': lambda x: 'bid' in x['name'] or 'ask' in x['name'] }] })
# can only trade things in inventory/storage or that have an ask on them

"""yaml
    agent:
        name: bill
        actions:
         - mine
         - collect
         - fight
         - hunt
         - eat
         - craft
         - smelt
         - trade
        inventory:
         - name: wooden_pickaxe
           quantity: 1
        goals:
          - name: make_money
            objective: money
        
"""
agent_graph = nx.Graph()
agent_graph.add_node('bill', props={ 'actions': ['mine', 'collect', 'fight', 'hunt', 'eat', 'craft', 'smelt', 'trade'] })

inventory_graph = nx.Graph()
#inventory_graph.add_node('wooden_pickaxe', props = { 'name': 'wooden_pickaxe', 'quantity': 1 })

# todo state graph -> inventory, health, observations

# State -> State Graph  

goals_graph = nx.Graph()
goals_graph.add_node('make_money', props={'name': 'make_money', 'objective': ['money'] })

"""yaml
    abstract_actions:
        - trade:
            bid: 
              joins...
            ask:
            debit:
            credit:
            money:
"""



trade_graph = nx.Graph()
trade_graph.add_node('bid', props={ 'name': 'bid', 'joins': [{'index': 'trade', 'filter': lambda x: 'debit' == x['name'] }]  }) # money -> debit -> all items
trade_graph.add_node('ask', props={ 'name': 'ask', 'joins': [{'index': 'trade', 'filter': lambda x: 'credit' == x['name']  }] }) # inventory items -> credit -> money
trade_graph.add_node('debit', props={'name': 'debit', 'joins': [{ 'index': 'items', 'filter': lambda x: x } ] }) 
trade_graph.add_node('credit', props={'name': 'credit', 'joins': [{ 'index': 'inventory', 'filter': lambda x: x } ] }) # could be , { 'index': 'trade', 'filter': lambda x: 'money' in x['name'] }
trade_graph.add_node('money', props={'name': 'money', 'joins': [{ 'index': 'trade', 'filter': lambda x: 'debit' == x['name'] or 'credit' == x['name'] } ] })

def ins(x):
    print('here',x)
    return x

"""
# shortcut to custom lang
# agent_config.py
joins = {
    'bid': [{lambda x: x}],
    '...': []
}
lenses = {
    'only_inventory_mining_items': { 'source': lambda x: 'items' in x[1]['source'], 
                              'condition': lambda x: 'pickaxe' not in x[1]['props']['name'] or x[1]['props']['name'] in [n[1]['props']['name'] for n in inventory_graph.nodes(data=True)] }
}
linking_instructions = []

def parse_agent():
    pass
    
def parse_actions():
    pass
    
def parse_abstract_actions()
    pass
    
def map_agent_to_agent_config_py():
    pass
"""

lenses = {
    'only_inventory_mining_items': { 'source': lambda x: 'items' in x[1]['source'], 
                              'condition': lambda x: 'pickaxe' not in x[1]['props']['name'] or x[1]['props']['name'] in [n[1]['props']['name'] for n in inventory_graph.nodes(data=True)] }
}

linking_instructions = [
    {
        'source': 'blocks',
        'target': 'items',
        'link': lambda s, t: t['props']['name'] in s['props']['drops'],
    },
    {
        'source': 'items',
        'target': 'blocks',
        'link': lambda s, t: s['props']['name'] in t['props']['requires'],
    },
    {
        'source': 'items',
        'target': 'food',
        'link': lambda s, t: s['props']['name'] == t['props']['name'],
    },
    {
        'source': 'agent',
        'target': 'goals',
        'link': lambda s, t: True # all goals are linked to all actions
    },
    {
        'source': 'goals',
        'target': 'actions',
        'link': lambda s, t: True # all goals are linked to all actions
        # todo get agent actions t['props']['name'] in s['props']['actions']
    },
    {
        'source': 'recipes',
        'target': 'items',
        'link': lambda s, t: t['props']['name'] == s['props']['provides']['name']
    },
    {
        'source': 'recipes',
        'target': 'items',
        'link': lambda s, t: t['props']['name'] in [n['name'] for n in s['props']['needs']]
    },
]

graph_dict = {'blocks': blocks_graph, 
                          'items': items_graph, 
                          'food': food_graph, 
                          'actions': actions_graph, 
                          'agent': agent_graph,
                          'inventory': inventory_graph,
                          'goals': goals_graph,
                          'trade': trade_graph,
                          'recipes': recipes_graph }

one_to_many_join_graphs = { 'sources': [('actions', actions_graph), ('trade', trade_graph)], 'on': graph_dict }

# Create an instance of the GraphComposer class
composer = GraphComposer(graph_dict, linking_instructions, one_to_many_join_graphs, lenses)

# Compose the graphs
composer.compose_graphs()

# Get the composed graph
composed_graph = composer.get_composed_graph()

# Print the composed graph
# print("Composed Graph:")
# print(composed_graph.nodes())
# print(composed_graph.edges())

def create_actions_tree(action):
    tree = bfs_subgraph(composed_graph, source=action)
    return tree

def draw_action_tree(action):
    action_tree = create_actions_tree(action)
    pos = nx.spring_layout(action_tree)
    nx.draw_networkx(action_tree, pos, with_labels=True)
    
def draw_action_tree_with_lenses(action):
    action_tree = create_actions_tree(action)
    action_tree = composer.apply_lenses(['only_inventory_mining_items'], action_tree)
    pos = nx.spring_layout(action_tree)
    nx.draw_networkx(action_tree, pos, with_labels=True)
    
def make_path_to_missing_target(nodes):
    # action -> contemplate
    # should take multiple missing nodes and find the shortest path to those nodes
    # if item -> check if craftable -> craft
    # if mineable -> mine
    # etc...
    pass
    
def get_missing_node_workflow(action):
    action_tree = create_actions_tree(action)
    current_tree = composer.apply_lenses(['only_inventory_mining_items'], action_tree)
    try:
        is_path = nx.shortest_path(current_tree, action, 'items:stone')
    except Exception:
        is_path = None
    
    if not is_path:
        # find unfulfilled nodes
        diff = graph_diff(action_tree, current_tree)
        
        for s,t,v in get_edges_in_order(diff, action):
            if v['fulfilled'] == False:
                
                print(s, t, v)
                # find path from agent to unfulfilled
                # if path -> create goal
                # if no path -> attempt to find path to closest node
                # if path -> create goal 
                # ...

    
# this sort of makes sense but should start from agent node
# the goal should be defined sufficiently in the declaration above: ('goals:make_money', 'trade:credit')
def draw_decision(goal):
    paths = dfs_paths(composed_graph, goal)
    paths = [path for path in paths if "trade:credit" in path]
    G = graph_from_paths(paths)
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos, with_labels=True)

def draw_all_graph():
    pos = nx.shell_layout(composed_graph)
    nx.draw_networkx(composed_graph, pos, with_labels=True)
    
def draw():
    draw_action_tree('actions:mine')
    plt.show()
    draw_action_tree_with_lenses('actions:mine')
    plt.show()
    
    get_missing_node_workflow('actions:mine')
    plt.show()
    
    draw_decision('goals:make_money')
    plt.show()

    draw_all_graph()
    plt.show()
    
draw()

# ability to traverse backwards from a desired node
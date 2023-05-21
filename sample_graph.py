import networkx as nx
import matplotlib.pyplot as plt

class GraphComposer:
    def __init__(self, graph_dict, linking_instructions, filter_graphs):
        self.graph_dict = graph_dict
        self.linking_instructions = linking_instructions
        self.composed_graph = nx.DiGraph()
        self.filter_graphs = filter_graphs

    def compose_graphs(self):
        for linking_instruction in self.linking_instructions:
            self._link_graphs(linking_instruction)
            
        for source_name, f_graph in self.filter_graphs['sources']:
            for n in f_graph.nodes(data=True):
                filters = n[1]['props']['filters']
                for filter in filters:
                    index = filter['index']
                    filter = filter['filter']
                    graph = self.filter_graphs['on'].get(index)
                    if not graph:
                        continue

                    filtered_nodes = [node for node in graph.nodes(data=True) if filter(node[1]['props'])]
                    for nt in filtered_nodes:
                        new_source = source_name + ":" + n[0]
                        new_target = index + ":" + nt[0]
                        self.composed_graph.add_edge(new_source, new_target)

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
                self.composed_graph.add_node(new_source, **source_node[1])
                self.composed_graph.add_node(new_target, **target_node[1])
                
                self.composed_graph.add_edge(new_source, new_target)
                

    def get_composed_graph(self):
        return self.composed_graph

blocks_graph = nx.Graph()
blocks_graph.add_node('cobblestone', props={'drops': ['stone'], 'requires': ['wooden_pickaxe', 'stone_pickaxe'], 'material': 'mineable/pickaxe'})
blocks_graph.add_node('dirt', props={'drops': ['dirt'], 'requires':[], 'material': 'mineable/shovel'})
blocks_graph.add_node('wood', props={'drops': ['wood'], 'requires':[], 'material': 'mineable/axe' })
blocks_graph.add_node('carrot', props={'drops': ['carrot'], 'requires':[], 'material': 'mineable/axe' })

items_graph = nx.Graph()
items_graph.add_node('stone', props={'name': 'stone',  })
items_graph.add_node('dirt', props={'name': 'dirt' })
items_graph.add_node('wood', props={'name': 'wood' })
items_graph.add_node('carrot', props={'name': 'carrot' })
items_graph.add_node('stone_pickaxe', props={'name': 'stone_pickaxe'})
items_graph.add_node('wooden_pickaxe', props={'name': 'wooden_pickaxe'})


actions_graph = nx.Graph()
mine_filters = [{'index': 'blocks', 'filter': lambda x: x.get('material') == 'mineable/pickaxe' },
                {'index': 'items', 'filter': lambda x: 'pickaxe' in x.get('name') }]
actions_graph.add_node('mine', props = { 'name': 'mine', 
                                        'filters': mine_filters })
actions_graph.add_node('collect', props = { 'name': 'collect', 'filters': [{ 'index': 'items', 'filter': lambda x: x } ] })
actions_graph.add_node('fight', props = { 'name':'fight', 'filters': [{'index': 'entities', 'filter': lambda x: x['type'] == 'Hostile mobs'} ] })
actions_graph.add_node('hunt', props = { 'name':'hunt', 'filters': [{ 'index': 'entities', 'filter': lambda x: x['type'] == 'Passive mobs' }] })
actions_graph.add_node('eat', props = { 'name':'eat', 'filters': [{ 'index': 'foods', 'filter': lambda x: x['food_points'] > 0 }] })
actions_graph.add_node('craft', props = { 'name':'craft', 'filters': [{'index': 'recipe', 'filter': lambda x: x }] })
actions_graph.add_node('smelt', props = { 'name':'smelt', 'filters': [{ 'index': 'smelting', 'filter': lambda x: x }]})

agent_graph = nx.Graph()
agent_graph.add_node('bill', props={ 'actions': ['mine', 'collect', 'fight', 'hunt', 'eat', 'craft', 'smelt'] })

# todo state graph -> inventory, health, observations


food_graph = nx.Graph()
food_graph.add_node('apple', props={'name': 'apple'})
food_graph.add_node('bread', props={'name': 'bread'})
food_graph.add_node('carrot', props={'name': 'carrot'})

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
        'target': 'actions',
        'link': lambda s, t: t['props']['name'] in s['props']['actions']
    }
]

graph_dict = {'blocks': blocks_graph, 
                          'items': items_graph, 
                          'food': food_graph, 
                          'actions': actions_graph, 
                          'agent': agent_graph }

filter_links = { 'sources': [('actions', actions_graph)], 'on': graph_dict }

# Create an instance of the GraphComposer class
composer = GraphComposer(graph_dict, linking_instructions, filter_links)

# Compose the graphs
composer.compose_graphs()

# Get the composed graph
composed_graph = composer.get_composed_graph()

# Print the composed graph
print("Composed Graph:")
print(composed_graph.nodes())
print(composed_graph.edges())

def create_actions_tree(action):
    dfs_tree = nx.dfs_tree(composed_graph, source=action)
    return dfs_tree

def draw_action_tree(action):
    action_tree = create_actions_tree(action)
    pos = nx.spring_layout(action_tree)
    nx.draw_networkx(action_tree, pos, with_labels=True)

def draw_all_graph():
    pos = nx.spring_layout(composed_graph)
    nx.draw_networkx(composed_graph, pos, with_labels=True)

def draw():
    draw_action_tree('actions:mine')
    plt.show()

    draw_all_graph()
    plt.show()
    
draw()
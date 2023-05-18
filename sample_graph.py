import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

class GraphComposer:
    def __init__(self, graph_dict, linking_instructions):
        self.graph_dict = graph_dict
        self.linking_instructions = linking_instructions
        self.composed_graph = nx.Graph()

    def compose_graphs(self):
        for linking_instruction in self.linking_instructions:
            self._link_graphs(linking_instruction)

    def _link_graphs(self, linking_instruction):
        target = linking_instruction['target']
        source = linking_instruction['source']
        link = linking_instruction['link']
        target_graph = self.graph_dict[target]
        source_graph = self.graph_dict[source]
        
        for source_node in source_graph.nodes(data=True):
            target_node = next(filter(lambda x: x if link(source_node[1], x[1]) else None, target_graph.nodes(data=True)), None)
            if target_node:
                new_source = source + ":" + source_node[0]
                new_target = target + ":" + target_node[0]
                self.composed_graph.add_node(new_source, **source_node[1])
                self.composed_graph.add_node(new_target, **target_node[1])
                
                self.composed_graph.add_edge(new_source, new_target)
                

    def get_composed_graph(self):
        return self.composed_graph

blocks_graph = nx.Graph()
blocks_graph.add_node('cobblestone', props={'drops': ['stone']})
blocks_graph.add_node('dirt', props={'drops': ['dirt']})
blocks_graph.add_node('wood', props={'drops': ['wood']})
blocks_graph.add_node('carrot', props={'drops': ['carrot']})

items_graph = nx.Graph()
items_graph.add_node('stone', props={'name': 'stone'})
items_graph.add_node('dirt', props={'name': 'dirt'})
items_graph.add_node('wood', props={'name': 'wood'})
items_graph.add_node('carrot', props={'name': 'carrot'})

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
        'target': 'food',
        'link': lambda s, t: s['props']['name'] == t['props']['name'],
    }
]

# Create an instance of the GraphComposer class
composer = GraphComposer({'blocks': blocks_graph, 'items': items_graph, 'food': food_graph}, linking_instructions)

# Compose the graphs
composer.compose_graphs()

# Get the composed graph
composed_graph = composer.get_composed_graph()

# Print the composed graph
print("Composed Graph:")
print(composed_graph.nodes())
print(composed_graph.edges())

#pos = graphviz_layout(composed_graph, prog="circo")
pos = nx.spring_layout(composed_graph)

# Draw the graph
nx.draw_networkx(composed_graph, pos, with_labels=True)
plt.show()


import networkx as nx
import matplotlib.pyplot as plt
from sample_graph.experiment_algs import FindSubGoals
from sample_graph.graph_composer import GraphComposer

from utils import dfs_paths, graph_from_paths
from sample_graph.agent_config import LENSES, graph_dict, linking_instructions, one_to_many_join_graphs, lenses

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
# Create an instance of the GraphComposer class
composer = GraphComposer(graph_dict, linking_instructions, one_to_many_join_graphs, lenses)

# Compose the graphs
composer.compose_graphs()

# Get the composed graph
composed_graph = composer.get_composed_graph()
find = FindSubGoals(composer)
# Print the composed graph
# print("Composed Graph:")
# print(composed_graph.nodes())
# print(composed_graph.edges())

def draw_action_tree(action):
    action_tree = find.create_actions_tree(action)
    pos = nx.spring_layout(action_tree)
    nx.draw_networkx(action_tree, pos, with_labels=True)
    
def draw_action_tree_with_lenses(action):
    action_tree = find.create_actions_tree(action)
    action_tree = composer.apply_lenses([LENSES.IN_INVENTORY], action_tree)
    pos = nx.spring_layout(action_tree)
    nx.draw_networkx(action_tree, pos, with_labels=True)

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
    
def draw_graph(G):
    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'type')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx(G, pos, with_labels=True)
    plt.show()
    
def draw():
    draw_action_tree('actions:mine')
    plt.show()
    draw_action_tree_with_lenses('actions:mine')
    plt.show()
    
    G = find.get_feasible_workflows('actions:mine')
    draw_graph(G)
    plt.show()
    
    draw_decision('goals:make_money')
    plt.show()

    draw_all_graph()
    plt.show()

draw_all_graph()
plt.show()

G, goals = find.get_feasible_workflows('actions:mine', 'items:stone')
draw_graph(G)
# for g in goals:
#     print(g)
#     T = find.get_feasible_workflows('actions:craft', g)
#     draw_graph(G)

#draw()

# ability to traverse backwards from a desired node
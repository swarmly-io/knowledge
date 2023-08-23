import networkx as nx
import matplotlib.pyplot as plt
import pytest
from services.graph_composer import GraphComposer
from test.sub_goals import FindSubGoals

from utils import dfs_paths, graph_from_paths
from graphs.minecraft.agent_config import LENSE_TYPES, graph_dict, linking_instructions, one_to_many_join_graphs, lenses

# composer = GraphComposer(
#     graph_dict,
#     linking_instructions,
#     one_to_many_join_graphs,
#     lenses)

# composer.compose_graphs()
# composed_graph = composer.get_composed_graph()
# find = FindSubGoals(composer)

# def draw_action_tree(action):
#     action_tree = find.create_actions_tree(action)
#     pos = nx.spring_layout(action_tree)
#     nx.draw_networkx(action_tree, pos, with_labels=True)


# def draw_action_tree_with_lenses(action):
#     action_tree = find.create_actions_tree(action)
#     action_tree = composer.apply_lenses([LENSE_TYPES.IN_INVENTORY], action_tree)
#     pos = nx.spring_layout(action_tree)
#     nx.draw_networkx(action_tree, pos, with_labels=True)

# # this sort of makes sense but should start from agent node
# # the goal should be defined sufficiently in the declaration above:
# # ('goals:make_money', 'trade:credit')


# def draw_decision(goal):
#     paths = dfs_paths(composed_graph, goal)
#     paths = [path for path in paths if "trade:credit" in path]
#     G = graph_from_paths(paths)
#     pos = nx.spring_layout(G)
#     nx.draw_networkx(G, pos, with_labels=True)


# def draw_all_graph():
#     pos = nx.shell_layout(composed_graph)
#     nx.draw_networkx(composed_graph, pos, with_labels=True)


# def draw_graph(G):
#     pos = nx.spring_layout(G)
#     edge_labels = nx.get_edge_attributes(G, 'type')
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
#     nx.draw_networkx(G, pos, with_labels=True)
#     plt.show()


# def save_image(name):
#     plt.savefig('test/figures/' + name + '.jpg', dpi=80)
#     plt.clf()

# @pytest.mark.skip()
# def test_test_draw_all():
#     draw_action_tree('actions:mine')
#     draw_action_tree_with_lenses('actions:mine')
#     save_image('actions_mine')

#     G = find.get_feasible_workflows('actions:mine', 'items:stone')
#     print(G)
#     draw_graph(G[0])
#     print(G[1])
#     save_image('mine')

#     draw_decision('goals:make_money')
#     save_image('money_goal')

#     draw_all_graph()
#     save_image('all')

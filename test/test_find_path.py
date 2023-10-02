import networkx as nx
from services.feasibility import Feasibility
from services.find_path import find_path_with_feasibility
from services.graph_composer import EdgeType


def add_needs_edges(filtered_graph, needs_edges):
    for edge in needs_edges:
        filtered_graph.add_edge(edge[0], edge[1], type=EdgeType.NEEDS)


# Example usage
# Create the filtered and unfiltered graphs
filtered_graph = nx.DiGraph()
filtered_graph.add_edges_from([('A', 'B', {'type': EdgeType.NEEDS }),
                               ('A', 'C', {'type': EdgeType.NEEDS}),
                               ('B', 'D', {'type': EdgeType.NEEDS}),
                               ('B', 'E', {'type': EdgeType.NEEDS}),
                               ('D', 'G', {'type': EdgeType.NEEDS}),
                               ('E', 'F', {'type': EdgeType.NEEDS}),
                               ('H', 'I', {'type': EdgeType.NEEDS}),
                               ('I', 'J', {'type': EdgeType.NEEDS}),
                               ('J', 'K', {'type': EdgeType.PROVIDES})])

unfiltered_graph = nx.DiGraph()
unfiltered_graph.add_edges_from([('A', 'B', {'type': EdgeType.NEEDS}),
                                 ('A', 'C', {'type': EdgeType.NEEDS}),
                                 ('B', 'D', {'type': EdgeType.NEEDS}),
                                 ('B', 'E', {'type': EdgeType.NEEDS}),
                                 ('C', 'F', {'type': EdgeType.NEEDS}),
                                 ('D', 'G', {'type': EdgeType.NEEDS}),
                                 ('E', 'F', {'type': EdgeType.NEEDS}),
                                 ('F', 'H', {'type': EdgeType.NEEDS}),
                                 ('G', 'H', {'type': EdgeType.NEEDS}),
                                 ('H', 'I', {'type': EdgeType.NEEDS}),
                                 ('I', 'J', {'type': EdgeType.NEEDS}),
                                 ('J', 'K', {'type': EdgeType.PROVIDES})])

start_node = 'A'
target_node = 'K'

nx.set_node_attributes(filtered_graph, Feasibility.FEASIBLE, 'feasibility')
nx.set_node_attributes(unfiltered_graph, Feasibility.FEASIBLE, 'feasibility')

def test_no_path_when_no_connection():
    results = find_path_with_feasibility(
        filtered_graph,
        unfiltered_graph,
        start_node,
        target_node)
    assert results.base_path_infeasible == True
    assert list(map(lambda x: x['node'], results.base_path[0])) == []

def test_finds_path_when_graph_complete():
    # try again
    results = find_path_with_feasibility(
        unfiltered_graph,
        unfiltered_graph,
        start_node,
        target_node)
    assert results.base_path_infeasible == False
    assert list(map(lambda x: x['node'], results.base_path[0])) == ['A', 'C', 'F', 'H', 'I', 'J', 'K']

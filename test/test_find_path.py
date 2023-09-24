import networkx as nx
from services.find_path import find_path_with_feasibility
from services.graph_composer import EdgeType


def add_needs_edges(filtered_graph, needs_edges):
    for edge in needs_edges:
        filtered_graph.add_edge(edge[0], edge[1], type=EdgeType.NEEDS)


# Example usage
# Create the filtered and unfiltered graphs
filtered_graph = nx.DiGraph()
filtered_graph.add_edges_from([('A', 'B', {'type': EdgeType.NEEDS}),
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


def test_finds_missing_node_for_incomplete_graph():
    results = find_path_with_feasibility(
        filtered_graph,
        unfiltered_graph,
        start_node,
        target_node)
    assert results[0] == False
    assert list(map(lambda x: x['node'], results[1][1])) == [
        'A', 'B', 'E', 'F', 'H']


def test_finds_path_when_graph_complete():
    # try again
    results = find_path_with_feasibility(
        unfiltered_graph,
        unfiltered_graph,
        start_node,
        target_node)
    assert results[0]
    assert list(map(lambda x: x['node'], results[1][0])) == [
        'A', 'B', 'D', 'G', 'H', 'I', 'J', 'K']

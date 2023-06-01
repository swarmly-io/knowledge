import networkx as nx
from sample_graph.find_path import find_path


def add_needs_edges(filtered_graph, needs_edges):
    for edge in needs_edges:
        filtered_graph.add_edge(edge[0], edge[1], type='needs')

# Example usage
# Create the filtered and unfiltered graphs
filtered_graph = nx.DiGraph()
filtered_graph.add_edges_from([('A', 'B', {'type': 'provides'}),
                               ('A', 'C', {'type': 'needs'}),
                               ('B', 'D', {'type': 'provides'}),
                               ('B', 'E', {'type': 'needs'}),
                               ('D', 'G', {'type': 'provides'}),
                               ('E', 'F', {'type': 'needs'}),
                               ('H', 'I', {'type': 'needs'}),
                               ('I', 'J', {'type': 'needs'}),
                               ('J', 'K', {'type': 'provides'})])

unfiltered_graph = nx.DiGraph()
unfiltered_graph.add_edges_from([('A', 'B', {'type': 'provides'}),
                                 ('A', 'C', {'type': 'needs'}),
                                 ('B', 'D', {'type': 'provides'}),
                                 ('B', 'E', {'type': 'needs'}),
                                 ('C', 'F', {'type': 'needs'}),
                                 ('D', 'G', {'type': 'provides'}),
                                 ('E', 'F', {'type': 'needs'}),
                                 ('F', 'H', {'type': 'needs'}),
                                 ('G', 'H', {'type': 'needs'}),
                                 ('H', 'I', {'type': 'needs'}),
                                 ('I', 'J', {'type': 'needs'}),
                                 ('J', 'K', {'type': 'provides'})])

start_node = 'A'
target_node = 'K'

def test_finds_missing_node_for_incomplete_graph():
    results = find_path(filtered_graph, unfiltered_graph, start_node, target_node)
    assert results[0] == False
    assert results[1] == [('F', 'H')]
    # simulate achieving sub goal
    if not results[0]:
        add_needs_edges(filtered_graph, results[1])
        
    

def test_finds_path_when_graph_complete():
    # try again
    results = find_path(filtered_graph, unfiltered_graph, start_node, target_node)
    assert results[0] == True
    assert results[1] == ['A', 'B', 'E', 'F', 'H', 'I', 'J', 'K']

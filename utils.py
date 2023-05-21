from collections import deque
import networkx as nx

def bfs(G: nx.Graph, source):
    T = nx.DiGraph()
    for k,v in G.nodes._nodes.items():
        T.add_node(k, **v)

    try:
        path = nx.bfs_edges(G, source, None)
        for e in path:
            T.add_edge(*e, **G.edges[e[0], e[1]])
    except:
        return None
    
    return T

def dfs(G: nx.Graph, source):
    T, _ = dfs_with_edges(G, source)
    return T

def dfs_with_edges(G: nx.Graph, source):
    T = nx.DiGraph()
    for k,v in G.nodes._nodes.items():
        T.add_node(k, **v)
    data_path = []
    try:
        path = nx.dfs_edges(G, source, None)
        for e in path:
            T.add_edge(*e, **G.edges[e[0], e[1]])
            data_path.append((e[0], e[1], G.edges[e[0], e[1]]))
    except:
        return None, None
    return T, data_path
    
def bfs_subgraph(digraph, source):
    visited_nodes = set()
    visited_edges = set()
    queue = deque([(source, None)])

    while queue:
        node, incoming_edge = queue.popleft()
        if node not in visited_nodes:
            visited_nodes.add(node)
            if incoming_edge is not None:
                visited_edges.add(incoming_edge)
            neighbors = digraph.successors(node)
            queue.extend([(neighbor, (node, neighbor)) for neighbor in neighbors])

    subgraph = digraph.subgraph(visited_nodes).copy()
    for edge in visited_edges:
        subgraph.add_edge(*edge)

    return subgraph

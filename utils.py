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
    
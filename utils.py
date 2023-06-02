from collections import deque
import networkx as nx


def bfs(G: nx.Graph, source):
    T = nx.DiGraph()
    for k, v in G.nodes._nodes.items():
        T.add_node(k, **v)

    try:
        path = nx.bfs_edges(G, source, None)
        for e in path:
            T.add_edge(*e, **G.edges[e[0], e[1]])
    except BaseException:
        return None

    return T


def dfs(G: nx.Graph, source):
    T, _ = dfs_with_edges(G, source)
    return T


def dfs_with_edges(G: nx.Graph, source):
    T = nx.DiGraph()
    for k, v in G.nodes._nodes.items():
        T.add_node(k, **v)
    data_path = []
    try:
        path = nx.dfs_edges(G, source, None)
        for e in path:
            T.add_edge(*e, **G.edges[e[0], e[1]])
            data_path.append((e[0], e[1], G.edges[e[0], e[1]]))
    except BaseException:
        return None, None
    return T, data_path


def bfs_subgraph(digraph, source) -> nx.DiGraph:
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
            queue.extend([(neighbor, (node, neighbor))
                         for neighbor in neighbors])

    subgraph = nx.DiGraph()

    for edge in visited_edges:
        subgraph.add_edge(*edge)

    return subgraph


def dfs_paths(graph, start, path=[]):
    path = path + [start]
    paths = []
    for neighbor in graph.neighbors(start):
        if neighbor not in path:
            new_paths = dfs_paths(graph, neighbor, path)
            paths.extend(new_paths)
    if not paths:  # Leaf node, add the path to the result
        paths.append(path)
    return paths


def graph_from_paths(paths):
    subgraph = nx.DiGraph()
    for path in paths:
        subgraph.add_nodes_from(path)
        subgraph.add_edges_from(zip(path[:-1], path[1:]))
    return subgraph


def graph_diff(ideal_graph, real_graph):
    """
    Compute the difference between two graphs based on the presence of edges.

    Args:
        ideal_graph (nx.Graph): The ideal graph representing the expected state.
        real_graph (nx.Graph): The real graph representing the actual state.

    Returns:
        diff_graph (nx.Graph): A new graph with an edge property indicating fulfillment.
    """
    diff_graph = nx.DiGraph()

    # Iterate over the edges in the ideal graph
    for u, v, d in ideal_graph.edges(data=True):
        # Check if the edge exists in the real graph
        if real_graph.has_edge(u, v):
            fulfilled = True
        else:
            fulfilled = False

        # Add the edge to the diff graph with the fulfillment property
        diff_graph.add_edge(u, v, fulfilled=fulfilled, **d)

    return diff_graph


def get_edges_in_order_dfs(diff_graph, root):
    """
    Retrieve the edges in order from the specified root node to the bottom of the tree,
    including the edge data.

    Args:
        diff_graph (nx.Graph): The diff graph representing the tree structure.
        root: The root node of the tree.

    Returns:
        edges (List[Tuple]): List of edges in order from the specified root to the bottom,
            including the edge data.
    """
    edges = []

    def dfs(node, parent):
        for child in diff_graph.neighbors(node):
            if child != parent:
                edge_data = diff_graph.get_edge_data(node, child)
                edges.append((node, child, edge_data))
                dfs(child, node)

    dfs(root, None)

    return edges


def get_edges_in_order(diff_graph, root):
    """
    Retrieve the edges in order from the specified root node to the bottom of the tree,
    including the edge data, using breadth-first search (BFS).

    Args:
        diff_graph (nx.Graph): The diff graph representing the tree structure.
        root: The root node of the tree.

    Returns:
        edges (List[Tuple]): List of edges in order from the specified root to the bottom,
            including the edge data.
    """
    edges = []
    queue = deque([(root, None)])  # Start BFS from the root node

    while queue:
        node, parent = queue.popleft()

        for child in diff_graph.neighbors(node):
            if child != parent:
                edge_data = diff_graph.get_edge_data(node, child)
                edges.append((node, child, edge_data))
                queue.append((child, node))

    return edges


def paths_to_tree(G, paths):
    # Create a new directed graph to store the tree
    tree = nx.DiGraph()

    for path in paths:
        for i in range(len(path) - 1):
            # Copy the node data for both nodes in the edge if they don't exist
            # in the tree yet
            if not tree.has_node(path[i]):
                tree.add_node(path[i], **G.nodes[path[i]])
            if not tree.has_node(path[i + 1]):
                tree.add_node(path[i + 1], **G.nodes[path[i + 1]])

            # Add an edge to the tree if it doesn't exist yet, and copy the
            # edge data from the original graph
            if not tree.has_edge(path[i], path[i + 1]):
                tree.add_edge(path[i], path[i + 1], **G[path[i]][path[i + 1]])

    return tree


def default(x):
    return True


def filtered_bfs(
        G,
        source,
        target,
        edge_condition=default,
        last_edge_condition=default,
        whole_branch_condition=default):
    # Initialize the queue with the source node
    queue = deque([(source, [])])
    visited = {source: []}  # Stores visited nodes and their path

    # Create a graph to store the valid paths
    valid_path_graph = nx.DiGraph()

    while queue:
        node, path = queue.popleft()

        # If we reached the target node and the last edge passes the
        # last_edge_condition, add the path to the graph
        if node == target and (not path or last_edge_condition(
                G[path[-1][0]][path[-1][1]])):
            for i in range(len(path) - 1):
                valid_path_graph.add_edge(
                    path[i][0], path[i + 1][0], **G[path[i][0]][path[i][1]])
            valid_path_graph.add_edge(
                path[-1][0], node, **G[path[-1][0]][node])
            continue

        for neighbor in G[node]:
            edge = G[node][neighbor]
            new_path = path + [(node, neighbor)]

            # If the neighbor is not visited or is visited with a different path, and the edge passes the edge_condition,
            # and the path passes the whole_branch_condition, add it to the
            # queue
            if (neighbor not in visited or visited[neighbor] != new_path) and edge_condition(
                    edge) and whole_branch_condition(new_path):
                queue.append((neighbor, new_path))
                visited[neighbor] = new_path

    return valid_path_graph

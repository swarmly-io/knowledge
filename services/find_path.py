import networkx as nx
from services.graph_composer import EdgeType

def find_all_paths(graph, start, end, target_edge_type):
    # Use recursion to find all paths
    paths = []
    visited = set()  # Track visited nodes within each path
    find_paths_recursive(graph, start, end, target_edge_type, [start], visited, paths)
    return paths

def find_paths_recursive(graph, current_node, end, target_edge_type, path, visited, paths):
    if current_node == end:
        paths.append(path)
        return

    visited.add(current_node)  # Mark current node as visited within the path

    for neighbor in graph.successors(current_node):
        if neighbor not in visited:
            find_paths_recursive(graph, neighbor, end, target_edge_type, path + [neighbor], visited.copy(), paths)
    
    visited.remove(current_node)  # Remove current node from visited set within the path

def path_edges(graph, path):
    edges = []
    if len(path) > 1:
        for u, v in zip(path[:-1], path[1:]):
            edge_type = graph.edges[u, v].get('type')
            edges.append(edge_type)
        return edges
    return []

def find_path(
        filtered_graph,
        unfiltered_graph,
        start_node,
        target_node,
        search_type=EdgeType.PROVIDES):
    try:
        filtered_paths = find_all_paths(
            filtered_graph, start_node, target_node, search_type)
        feasible_paths = []
        for filtered_path in filtered_paths:
            last_edge = (filtered_path[-2], filtered_path[-1])
            if filtered_graph[last_edge[0]
                              ][last_edge[1]]['type'] == search_type:
                
                feasible_paths.append(filtered_path)
        if feasible_paths:
            for f in feasible_paths:
                print(path_edges(filtered_graph, f))
            
            return True, feasible_paths

    except (nx.NetworkXNoPath, StopIteration):
        pass

    try:
        unfiltered_paths = find_all_paths(
            unfiltered_graph, start_node, target_node, search_type)
        paths_with_needs = []
        for path in unfiltered_paths:
            previous_node = start_node
            for p in path:
                if p == start_node or p == target_node:
                    continue
                try:
                    sub_path = nx.shortest_path(filtered_graph, start_node, p)
                except BaseException:
                    sub_path = None

                if not sub_path and unfiltered_graph[previous_node][p]['type'] == EdgeType.NEEDS:
                    if not filtered_graph[previous_node] or not filtered_graph[previous_node][p]:
                        paths_with_needs.append((previous_node, p))

                previous_node = p

        if paths_with_needs:
            return False, paths_with_needs

    except Exception:
        print("No paths found")

    return False, []

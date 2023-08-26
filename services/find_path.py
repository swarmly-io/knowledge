import networkx as nx
from services.graph_composer import EdgeType

def find_all_paths(graph, start, end, target_edge_type):
    # Use recursion to find all paths
    paths = []
    visited = set()  # Track visited nodes within each path
    find_paths_recursive(graph, start, end, target_edge_type, [start], visited, paths)
    return paths

def find_paths_recursive(graph, current_node, end, target_edge_type, path, visited, paths):
    if path[-1] == end and is_valid_path(graph, path, target_edge_type):
        paths.append(path)
        return

    visited.add(current_node)  # Mark current node as visited within the path

    for neighbor in graph.successors(current_node):
        if neighbor not in visited:
            find_paths_recursive(graph, neighbor, end, target_edge_type, path + [neighbor], visited.copy(), paths)
    
    visited.remove(current_node)  # Remove current node from visited set within the path

def is_valid_path(graph, path, target_edge_type):
    if len(path) > 1:
        for u, v in zip(path[:-1], path[1:]):
            edge_type = graph.edges[u, v].get('type')
            if edge_type == target_edge_type and v != path[-1]:
                return False
        return graph.edges[path[-2], path[-1]].get('type') == target_edge_type
    return False

def path_edges(graph, path):
    edges = []
    infeasible_edges = []
    if len(path) > 1:
        for u, v in zip(path[:-1], path[1:]):
            edge_type = graph.edges[u, v].get('type')
            edges.append(edge_type)
            infeasible = graph.nodes[v].get('infeasible')
            infeasible_edges.append(infeasible)
        return edges, infeasible_edges
    return []

def find_path_with_feasibility(
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
            if filtered_graph[last_edge[0]][last_edge[1]]['type'] == search_type:
                
                feasible_paths.append(filtered_path)
        if feasible_paths:
            typed_paths = make_typed_path(filtered_graph, feasible_paths)
            return True, typed_paths
    except (nx.NetworkXNoPath, StopIteration):
        pass

    try:
        unfiltered_paths = find_all_paths(
            unfiltered_graph, start_node, target_node, search_type)
        paths_with_needs = []
        for path in unfiltered_paths:
            new_path = []
            for p in path:
                if p == start_node or p == target_node:
                    continue
                try:
                    sub_path = nx.shortest_path(filtered_graph, start_node, p)
                except BaseException:
                    sub_path = None

                if not sub_path:
                    new_path = path
                    index = path.index(p)
                    new_path = new_path[:index + 1]
                    break
                    
            if len(new_path) > 0:
                paths_with_needs.append(new_path)

        if paths_with_needs:
            typed_paths = make_typed_path(unfiltered_graph, paths_with_needs)

            return False, typed_paths

    except Exception:
        print("No paths found")

    return False, []

def make_typed_path(filtered_graph, feasible_paths):
    typed_paths = []
    for f in feasible_paths:
        types, infeasible = path_edges(filtered_graph, f)
        typed_paths.append(list(map(lambda x: { 'node': x[0], 'type': x[1], 'infeasible': x[2] }, zip(f, [""] + types, [True] + infeasible))))
    return typed_paths


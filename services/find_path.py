import networkx as nx
from services.graph_composer import EdgeType

def find_all_paths(graph, start, end):
    # Use depth-first search to find all paths
    paths = []
    stack = [(start, [start])]
    
    while stack:
        node, path = stack.pop()
        
        if node == end:
            paths.append(path)
        
        for neighbor in graph.successors(node):  # Use successors instead of neighbors
            if neighbor not in path:
                stack.append((neighbor, path + [neighbor]))
    
    return paths


def find_path(
        filtered_graph,
        unfiltered_graph,
        start_node,
        target_node,
        search_type=EdgeType.PROVIDES):
    try:
        filtered_paths = find_all_paths(
            filtered_graph, start_node, target_node)
        feasible_paths = []
        for filtered_path in filtered_paths:
            last_edge = (filtered_path[-2], filtered_path[-1])
            if filtered_graph[last_edge[0]
                              ][last_edge[1]]['type'] == search_type:
                print(last_edge)
                feasible_paths.append(filtered_path)
        if feasible_paths:
            return True, feasible_paths

    except (nx.NetworkXNoPath, StopIteration):
        pass

    try:
        unfiltered_paths = nx.find_all_paths(
            unfiltered_graph, start_node, target_node)
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

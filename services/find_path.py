from collections import deque
import networkx as nx
from services.graph_composer import EdgeType


def find_all_paths(graph, current_node, end, target_edge_type):
    """
    Returns all shortest paths from current_node to end in the graph without traversing edges
    having the specified target_edge_type more than once.
    """
    if current_node == end:
        return [[current_node]]

    visited = {current_node}
    # Initialize with current_node as the start of the path
    queue = deque([([current_node], False)])
    shortest_paths = []

    while queue:
        path, target_type_visited = queue.popleft()
        last_node = path[-1]

        for neighbor, edge_attr in graph[last_node].items():
            if edge_attr.get('type') == target_edge_type:
                if target_type_visited:  # If we've already encountered this edge type in the path, skip it
                    continue
                else:
                    new_target_type_visited = True  # Set the flag since we're now traversing this edge type
            else:
                new_target_type_visited = target_type_visited  # Preserve the current state of the flag

            if neighbor == end:
                shortest_paths.append(path + [neighbor])
            elif neighbor not in visited:
                visited.add(neighbor)
                queue.append((path + [neighbor], new_target_type_visited))

    return shortest_paths


def find_paths_recursive(graph, current_node, end, target_edge_type, path, visited, paths):
    if path[-1] == end and is_valid_path(graph, path, target_edge_type):
        paths.append(path)
        return

    visited.add(current_node)  # Mark current node as visited within the path

    for neighbor in graph.successors(current_node):
        if neighbor not in visited:
            find_paths_recursive(
                graph,
                neighbor,
                end,
                target_edge_type,
                path + [neighbor],
                visited.copy(),
                paths)

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
    props = []
    if len(path) > 1:
        for u, v in zip(path[:-1], path[1:]):
            edge_type = graph.edges[u, v].get('type')
            edges.append(edge_type)
            infeasible = graph.nodes[v].get('infeasible')
            infeasible_edges.append(infeasible)
            prop = {**graph.nodes[v].get('props', {}), 'joins': None}

            props.append(prop)
        return edges, infeasible_edges, props
    return []


def make_typed_path(filtered_graph, feasible_paths, sub_path_fn=lambda x, y: x, acc_sub_paths={}):
    typed_paths = []
    path_infeasible = False
    for f in feasible_paths:
        types, infeasible, props = path_edges(filtered_graph, f)
        path_infeasible = True if infeasible or path_infeasible else False
        path = list(zip(f, [""] + types, [False] + infeasible, [{}] + props))
        typed_path = []
        for x in path:
            if x == path[-1]:
                sub_path_fn(x[0], x[2], acc_sub_paths)
            node = {'node': x[0], 'type': x[1], 'infeasible': x[2], 'data': x[3]}
            typed_path.append(node)
        typed_paths.append(typed_path)

    return path_infeasible, typed_paths, acc_sub_paths


def make_sub_path_traverser(
        filtered_graph,
        unfiltered_graph,
        start_node,
        search_type,
        sub_path_visited=set(), level=0):
    graph = filtered_graph if not sub_path_visited else unfiltered_graph

    def sub_path_traverser(node, infeasible, acc_sub_paths):
        level_one = not sub_path_visited
        if not infeasible and level_one:
            return

        edges = [e[1] for e in graph.edges(data=True) if e[0] ==
                 node and e[2]['type'] == EdgeType.NEEDS]
        sub_paths = []
        for n in edges:
            if n not in sub_path_visited:
                sub_path_visited.add(n)
                result_infeasible, result, _ = find_path_with_feasibility(
                    filtered_graph, unfiltered_graph, start_node, n, search_type, sub_path_visited, acc_sub_paths, level + 1)
                if result:
                    sub_paths.append((node, level, infeasible and result_infeasible, result))
        if sub_paths:
            if level_one:
                acc_sub_paths[node] = (acc_sub_paths.get('tmp', []) + sub_paths)
                acc_sub_paths[node] = sorted(acc_sub_paths[node], key=lambda x: (x[1], x[2]))

                del acc_sub_paths['tmp']
                acc_sub_paths = acc_sub_paths[node]
            else:
                acc_sub_paths['tmp'] = acc_sub_paths.get('tmp', []) + sub_paths

    return sub_path_traverser


def find_path_with_feasibility(
        filtered_graph,
        unfiltered_graph,
        start_node,
        target_node,
        search_type=EdgeType.PROVIDES,
        sub_path_visited=set(), acc_sub_paths={}, level=0):
    try:
        # we want a fully connected graph when trying to find solutions
        graph = filtered_graph if not sub_path_visited else unfiltered_graph

        filtered_paths = find_all_paths(
            graph, start_node, target_node, search_type)
        traversable_paths = []
        for filtered_path in filtered_paths:
            last_edge = (filtered_path[-2], filtered_path[-1])
            if graph[last_edge[0]][last_edge[1]]['type'] == search_type:
                traversable_paths.append(filtered_path)
        if traversable_paths:
            sub_path_traverser = make_sub_path_traverser(
                filtered_graph, unfiltered_graph, start_node, search_type, sub_path_visited, level)
            path_infeasible, typed_paths, acc_sub_paths = make_typed_path(
                graph, traversable_paths, sub_path_traverser)
            return path_infeasible, typed_paths, acc_sub_paths
    except (nx.NetworkXNoPath, StopIteration):
        pass
    except Exception:
        print("No paths found")

    return False, [], acc_sub_paths


def find_backward_paths(graph, node, state_dict):
    satisfied_paths = []

    def dfs(curr_node, visited, current_path):
        if curr_node in visited:
            return

        visited.add(curr_node)
        current_path.append(curr_node)

        # If the node satisfies the condition, add it to the paths and stop further traversal
        if state_dict.get(curr_node, False):
            satisfied_paths.append(current_path.copy())
            return

        # If the node has no predecessors, add it to the paths
        predecessors = list(graph.predecessors(curr_node))
        if not predecessors:
            satisfied_paths.append(current_path.copy())

        for neighbor in predecessors:
            dfs(neighbor, visited.copy(), current_path.copy())

    dfs(node, set(), [])
    return satisfied_paths

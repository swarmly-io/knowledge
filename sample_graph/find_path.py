import networkx as nx

def find_path(filtered_graph, unfiltered_graph, start_node, target_node, search_type = "provides"):
    try:
        filtered_paths = nx.all_shortest_paths(filtered_graph, start_node, target_node)
        for filtered_path in filtered_paths:
            last_edge = (filtered_path[-2], filtered_path[-1])
            if filtered_graph[last_edge[0]][last_edge[1]]['type'] == search_type:
                return True, filtered_path
    except (nx.NetworkXNoPath, StopIteration):
        pass
    
    
    try:
        unfiltered_paths = nx.all_shortest_paths(unfiltered_graph, start_node, target_node)
        paths_with_needs = []
        for path in unfiltered_paths:
            needs_edges = []
            previous_node = start_node
            for p in path:
                if p == start_node or p == target_node:
                    continue
                try:
                    sub_path = nx.shortest_path(filtered_graph, start_node, p)
                except:
                    sub_path = None

                if not sub_path and unfiltered_graph[previous_node][p]['type'] == 'needs':
                    if not filtered_graph[previous_node] or not filtered_graph[previous_node][p]:
                        paths_with_needs.append((previous_node, p))   
                    
                previous_node = p             

        if paths_with_needs:
            return False, paths_with_needs

    except Exception:
        print("No paths found")
    
    return False, []
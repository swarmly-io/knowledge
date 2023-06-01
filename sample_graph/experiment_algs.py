import networkx as nx
from sample_graph.agent_config import LENSES
from sample_graph.graph_composer import EdgeType
from utils import bfs_subgraph, filtered_bfs, get_edges_in_order, graph_diff, paths_to_tree
from sample_graph.graphs import feasible_action_graph

class FindSubGoals:
    def __init__(self, composer):
        self.composer = composer
    
    def create_actions_tree(self, action):
        tree = bfs_subgraph(self.composer.composed_graph, source=action)
        return tree

    def make_path_to_missing_target(self, target_node):
        # action -> contemplate
        # should take multiple missing nodes and find the shortest path to those nodes
        
        # create a graph for each edge type
        # Observed linked to observe_graph
        # Needs linked to inventory_graph
        def shortest_path_conditions(s, t, v):
            if v['type'] in list(feasible_action_graph.nodes()):
                print(s,t,v)
                return True
            return False
        
        trees = nx.DiGraph()
        graph = self.composer.apply_lenses(['exclude_ask_trades'], self.composer.composed_graph)
        for a in self.composer.graph_dict['actions'].nodes():
            try:
                # mapper needs context on how to get a target_node
                # each edge needs a type
                paths = list(nx.all_shortest_paths(graph, 'actions:' + a, target_node))
                tree = paths_to_tree(graph, paths)
            except:
                tree = None
            if tree:
                trees = nx.compose(trees, tree)
                trees.add_edge('actions', 'actions:' + a, type = EdgeType.ACTION)
        
        trees.add_node('actions', source='none')
                
        def trim_to_feasible_paths(trees):
            tree = self.composer.apply_lenses(['in_observation', 'in_inventory'], trees)
            return tree

        # if it's an item, only find nodes
        #new_tree = trim_to_feasible_paths(trees)
        # todo find the most efficient, feasible path
        #draw_graph(trees)
        new_tree = filtered_bfs(trees, 'actions', target_node, last_edge_condition= lambda x: x['type'] == EdgeType.PROVIDES)
        return new_tree
                
        
    def get_feasible_workflows(self, action, target):
        action_tree = self.create_actions_tree(action)
        current_tree = self.composer.apply_lenses([LENSES.IN_INVENTORY, LENSES.IN_OBSERVATION], action_tree)
        try:
            path = nx.shortest_path(current_tree, action, target)
        except Exception:
            path = None
        
        if not path:
            # find unfulfilled nodes
            diff = graph_diff(action_tree, current_tree)
            graphs = nx.DiGraph()
            for s,t,v in get_edges_in_order(diff, action):
                if v['fulfilled'] == False:
                    print(s,t,v)
                    target_graph = self.make_path_to_missing_target(t)
                    if target_graph.number_of_edges() > 0:
                        graphs = nx.compose(graphs, target_graph)
                    
            # todo - create sub goals
            if graphs.number_of_edges() == 0:
                raise Exception("No path to target found after search")
            
            # if action is an observation node -> ensure it's in observation graph
            # if action is an act_upon -> ensure all NEEDS nodes are met
            # if money required -> check if sufficient quantity
            goals = set()
            for s,t,d in graphs.edges(data=True):
                if d['type'] == EdgeType.PROVIDES:
                    goals.add(t)
            
            return graphs, list(goals)

        return current_tree, path
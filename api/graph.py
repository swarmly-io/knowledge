import timeit

from services.mini_graph_dict import graph_dict
from services.agent_config import lenses, linking_instructions, one_to_many_join_graphs
from services.graph_composer import GraphComposer
from services.find_path import find_path_with_feasibility
from services.state import state_to_graph
from models.agent_state import AgentMCState


class Graph:
    def __init__(self) -> None:
        self.composer: GraphComposer = None
        self.state : AgentMCState = None
    
    def set_composer(self, composer):
        self.composer = composer 
        
    def set_state(self, state: AgentMCState):
        self.state = state
        
    def run_state(self):
        state_to_graph(self.state)
        
    def get_graph(self):
        return self
    
    def find_path(self, source_node, target_node, lenses = []):
        # todo validate lenses
        if not lenses:
            filtered_graph = self.composer.get_composed_graph()
        else:
            filtered_graph = self.composer.apply_lenses(lenses)
        
        unfiltered_graph = self.composer.get_composed_graph()
        path = find_path_with_feasibility(filtered_graph, unfiltered_graph, source_node, target_node)
        return path
    
    def build_graph(self):
        if not self.composer:
            self.composer = GraphComposer(graph_dict, linking_instructions, one_to_many_join_graphs, lenses)
            self.set_composer(self.composer)

        t = timeit.timeit(self.composer.compose_graphs, number=1)
        print(f"Built in {t}")

        g = self.composer.get_composed_graph()
        return dict(nodes=len(g.nodes()), edges= len(g.edges()))
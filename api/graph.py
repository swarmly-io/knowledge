import timeit
from typing import List
from api.models import AgentDto
from models.goals import GoalStatement
from services.agent_graph_builder import Agent

from services.mini_graph_dict import graph_dict
from services.agent_config import lenses, linking_instructions, one_to_many_join_graphs
from services.graph_composer import EdgeType, GraphComposer
from services.find_path import find_path_with_feasibility
from models.agent_state import AgentMCState
from services.models import TagLink


class GraphService:
    def __init__(self):
        self.composer: GraphComposer = None
        self.state : AgentMCState = None
        self.goals: List[GoalStatement] = []
        self.agent: Agent = None
        self.graph_dict = graph_dict
        
    def create_agent(self, agent: AgentDto):
        self.agent = Agent(agent.name, agent.goals, agent.actions, agent.tag_list, self.graph_dict, agent.groups)
        
    def add_tag_links(self, links: List[str]):
        tag_links = []
        for link in links:
            tag_links.append(TagLink.from_csv_entry(link))
        self.agent.add_tag_links(tag_links)
    
    def set_composer(self, composer):
        self.composer = composer 
        
    def set_state(self, state: AgentMCState):
        self.state = state
        self.agent.state.mcState = self.state
        
    def add_active_tags(self, tags: List[str]):
        tag_dict = { t.name: t for t in self.agent.all_tags }
        active_tags = [tag_dict.get(t) for t in tags]
        self.agent.state.tags = active_tags
        return self.agent.state.tags
        
    def run_state(self):
        self.agent.make_graph_state()
        
    def get_graph(self):
        return self
    
    def add_goals(self, goals: List[GoalStatement]):
        self.goals = self.goals + goals
    
    def find_path(self, source_node, target_node, lenses = []):
        # todo validate lenses
        if not lenses:
            filtered_graph = self.composer.get_composed_graph()
        else:
            filtered_graph = self.composer.apply_lenses(lenses)
        
        unfiltered_graph = self.composer.get_composed_graph()
        return find_path_with_feasibility(filtered_graph, unfiltered_graph, source_node, target_node)
    
    def build_graph(self):
        if not self.composer:
            self.composer = GraphComposer(self.graph_dict, linking_instructions, one_to_many_join_graphs, lenses)
            self.set_composer(self.composer)

        t = timeit.timeit(self.composer.compose_graphs, number=1)
        print(f"Built in {t}")

        g = self.composer.get_composed_graph()
        return dict(nodes=len(g.nodes()), edges= len(g.edges()))
    
    def run(self):
        if not self.composer:
            self.build_graph()
        
        targets = self.agent.run_graph_and_get_targets(self.composer)
        paths = []
        for target in targets:
            for node in target:
                # todo calculate lenses for each group? goal? tag? etc.
                path = self.find_path(f"agent:{self.agent.name}", node, [])
                paths.append((node, path))
            
        return paths
        
    def make_workflow(self, source_node, target_node, lenses = []):
        # find path
        feasible, path = self.find_path(source_node, target_node, lenses)
        # for each need node find a path
        if not feasible:
            raise Exception(f"Can't make path")
        
        # trim unfeasible paths
        # choose a single path - what goals are satisfied, goal priorities, time estimates of each needs and acts_upon node
        # create a workflow document
        
        # create a workflow document
        # action name
        # goal name
        # requirements: needs
        # actionable nodes acrue, credit, observe
        workflow = {
            'actionable': []
        } 
        needs = []
        for p in path:
            if p['type'] == EdgeType.GOAL: 
                workflow['goal'] = p['node']
            elif p['type'] in [EdgeType.ACCRUE, EdgeType.ACT_UPON, EdgeType.OBSERVED]:
                workflow['actionable'] = p['node']
            elif p['type'] in [EdgeType.NEEDS]:
                # todo no goal needed, go from any action node and find path to needs
                needs.append(p['node'])
            else:
                print('Unknown node' + p)
        print(workflow)
                
             
        
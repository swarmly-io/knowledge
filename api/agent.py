from copy import deepcopy
import timeit
from typing import List
from api.models import AgentDto, NextActionResponse, Path, PathNode
from models.goals import GoalStatement, TagDto
from services.agent_graph_builder import Agent
from services.feasibility import NodeFeasibility

from services.graph_composer import GraphComposer
from services.find_path import find_path_with_feasibility
from models.agent_state import AgentMCState
from services.models import TagLink

import config
from graphs.minecraft.state import MinecraftStateRunner
if config.mini_graph:
    from graphs.minecraft.mini_graph_dict import graph_dict
    from graphs.minecraft.mini_agent_config import lenses, linking_instructions, one_to_many_join_graphs, LENSE_TYPES
else:
    from graphs.minecraft.big_graphs import graph_dict
    from graphs.minecraft.agent_config import lenses, linking_instructions, one_to_many_join_graphs, LENSE_TYPES

class AgentService:
    def __init__(self):
        self.composer: GraphComposer = None
        self.state: AgentMCState = None
        self.goals: List[GoalStatement] = []
        self.agent: Agent = None
        self.graph_dict = deepcopy(graph_dict)
        
    def create_agent(self, agent: AgentDto):
        state_runner = MinecraftStateRunner()
        self.graph_dict['agent'].add_node(agent.name, props={ 'actions': [a.name for a in agent.actions] })
                
        self.agent = Agent(agent.name, agent.goals, agent.actions, agent.tag_list, self.graph_dict, agent.groups, state_runner=state_runner)

    def add_tag_links(self, links: List[str]):
        tag_links = []
        for link in links:
            tag_link = TagLink.from_csv_entry(link)
            tag_links.append(tag_link)
        self.agent.add_tag_links(tag_links)
    
    def set_composer(self, composer):
        self.composer = composer 
        
    def set_state(self, state: AgentMCState):
        self.state = state
        self.agent.state.mcState = self.state
        
    def add_active_tags(self, tags: List[str]) -> List[TagDto]:
        tag_dict = { t.name: t for t in self.agent.all_tags }
        active_tags = [tag_dict.get(t) for t in tags]
        self.agent.state.tags = active_tags
        rankings = self.agent.goal_valuation.group_absolute_rankings
        tags_resp = [TagDto(**t.dict(), group_rank=rankings.get(t.group)) for t in self.agent.state.tags]
        return tags_resp
        
    def run_state(self, run_agent_goals: bool = True):
        if not self.state or not self.agent.state.mcState:
            raise Exception("No state found")
        self.agent.make_graph_state()
        self.composer.update_node_feasibility(NodeFeasibility(self.composer.get_composed_graph(), self.agent.state))
        # note: hack
        new_sources = []
        for x in self.composer.join_graphs['sources']:
            if x[0] == 'inventory':
                new_sources.append((x[0], self.graph_dict['inventory']))
            if x[0] == 'observations':
                new_sources.append((x[0], self.graph_dict['observations']))
            else:
                new_sources.append((x[0], x[1]))
        self.composer.join_graphs['sources'] = new_sources
        
        if run_agent_goals:
            results = self.agent.run_graph_and_get_targets(self.composer)
            print(results)
        
    def get_agent_service(self):
        return self
    
    def add_goals(self, goals: List[GoalStatement]):
        self.goals = self.goals + goals
    
    def find_path(self, source_node, target_node, lenses = []):
        # todo validate lenses
        if not config.mini_graph:
            t = timeit.timeit(lambda: self.composer.compose_graphs(['actions', 'goals', 'agent']), number=1)
            print(t)
        
        if not lenses:
            filtered_graph = self.composer.get_composed_graph()
        else:
            filtered_graph = self.composer.apply_lenses(lenses, flag_infeasible=True)
        
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
    
    def run(self, name) -> NextActionResponse:
        if not self.composer:
            self.build_graph()
        print(f"Finding next path for {name}")
        
        targets, goals, focus_tags = self.agent.run_graph_and_get_targets(self.composer)
        paths = []
        for target in targets:
            for node in target:
                # todo calculate lenses for each group? goal? tag? etc.
                path = self.find_path(f"agent:{self.agent.name}", node, [LENSE_TYPES.IN_OBSERVATION])
                paths.append((node, path))
        
        path_resp = []
        not_feasible_paths = []
        for p in paths:
            goal, (_, path) = p
            nodes_resps = list(map(lambda x: [PathNode(node=p['node'], type=p['type'] or None, infeasible=p['infeasible'], data=p['data']) for p in x], path))
            for nodes_resp in nodes_resps:
                feasible = all([not n.infeasible for n in nodes_resp])
                if feasible:
                    path_resp.append(Path(path=nodes_resp, goal=goal, feasible=feasible))
                else:
                    not_feasible_paths.append(Path(path=nodes_resp, goal=goal, feasible=feasible))
            
        # todo for each non feasible path resolve each feasible node and find a path to each non feasible node
        # only return the shortest non-feasible resolved path
        path_resp.extend(not_feasible_paths)
        
        return NextActionResponse(paths=path_resp, active_goals=goals, focus_tags=focus_tags, targets=targets)
                
             
        
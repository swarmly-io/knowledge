from copy import deepcopy
import timeit
import networkx as nx
from typing import List
from api.models import AgentDto, NextActionResponse, Path, PathNode, SubPath
from domain_models.decisions.goals import TagDto, GoalStatement
from services.agent_graph_builder import Agent
from services.feasibility import Feasibility, NodeFeasibility

from services.graph_composer import GraphComposer
from services.find_path import find_path_with_feasibility
from domain_models.decisions.links import TagLink
from domain_models.workflows.workflows import WorkflowTarget
from domain_models.minecraft.state import AgentMCState

import config
from graphs.minecraft.state import MinecraftStateRunner
from utils import deep_flatten

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
        
        self.filtered_graph = None
        self.unfiltered_graph = None

    def create_agent(self, agent: AgentDto):
        state_runner = MinecraftStateRunner()
        self.graph_dict['agent'].add_node(agent.name,
                                          props={'actions': [a.name for a in agent.actions]})

        self.agent = Agent(
            agent.name,
            agent.goals,
            agent.actions,
            agent.tag_list,
            self.graph_dict,
            agent.groups,
            state_runner=state_runner)

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
        tag_dict = {t.name: t for t in self.agent.all_tags}
        active_tags = [tag_dict.get(t) for t in tags]
        self.agent.state.tags = active_tags
        rankings = self.agent.goal_valuation.group_absolute_rankings
        tags_resp = [TagDto(**t.dict(), group_rank=rankings.get(t.group))
                     for t in self.agent.state.tags]
        return tags_resp

    def run_state(self, run_agent_goals: bool = True):
        if not self.state or not self.agent.state.mcState:
            raise Exception("No state found")
        self.agent.make_graph_state()
        self.composer.update_node_feasibility(
            NodeFeasibility(
                self.composer.get_composed_graph(),
                self.agent.state))
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
        
    def get_feasibility(self, target: WorkflowTarget, lenses=[]):
        if not self.filtered_graph or not self.unfiltered_graph:
            filtered_graph, unfiltered_graph = self.get_graphs(lenses)
        else:
            filtered_graph = self.filtered_graph
            unfiltered_graph = self.unfiltered_graph
            
        is_feasible = filtered_graph.nodes[target.node].get('feasibility', Feasibility.INFEASIBLE) in [Feasibility.FEASIBLE, Feasibility.ATTAINED]
        if not is_feasible:
            return False
        
        try:
            has_path = len(nx.shortest_path(unfiltered_graph, f"agent:{self.agent.name}", target.node)) > 0
        except Exception as e:
            print(e)
            has_path = False
        return has_path
            

    def find_path(self, source_node, lenses=[], save_graph=False):
        filtered_graph, unfiltered_graph = self.get_graphs(lenses)
        
        if save_graph:
            self.filtered_graph = filtered_graph
            self.unfiltered_graph = unfiltered_graph
        
        def run_path_finding(target_node):
            start = timeit.default_timer()
            result = find_path_with_feasibility(
                filtered_graph, unfiltered_graph, source_node, target_node)
            t = timeit.default_timer() - start
            print("find_path: ", t)
            return result
        
        return run_path_finding

    def get_graphs(self, lenses):
        # todo validate lenses
        if not config.mini_graph:
            t = timeit.timeit(lambda: self.composer.compose_graphs(
                ['actions', 'goals', 'agent']), number=1)
            print("Rebuild graph: ", t)
        
        if not lenses:
            filtered_graph = self.composer.get_composed_graph()
        else:
            filtered_graph = self.composer.apply_lenses(lenses, flag_feasibility=True)

        unfiltered_graph = self.agent.get_fully_connected_graph(self.composer, lenses)
        return filtered_graph,unfiltered_graph

    def build_graph(self):
        if not self.composer:
            self.composer = GraphComposer(
                self.graph_dict,
                linking_instructions,
                one_to_many_join_graphs,
                lenses)
            self.set_composer(self.composer)

        t = timeit.timeit(self.composer.compose_graphs, number=1)
        print(f"Built in {t}")

        g = self.composer.get_composed_graph()
        return dict(nodes=len(g.nodes()), edges=len(g.edges()))

    def run(self, name, max_paths = 3, trigger = None) -> NextActionResponse:
        # todo do something with trigger
        if not self.composer:
            self.build_graph()
        print(f"Finding next path for {name}")

        targets, goals, focus_tags, score = self.agent.run_graph_and_get_targets(self.composer)
        paths = []
        
        for target in targets:
            find_path = self.find_path(
                    f"agent:{self.agent.name}", [
                        LENSE_TYPES.IN_OBSERVATION])
            for node in target:
                path = find_path(node)
                paths.append((node, path))
                if len(paths) >= max_paths:
                    break

        def make_path(p):
            if isinstance(p, list):
                return [make_path(x) for x in p]
            return PathNode(node=p['node'],
                            type=p['type'] or None,
                            feasibility=p['feasibility'],
                            data=p['data'])

        path_resp = []
        not_feasible_paths = []
        for p in paths:
            goal = p[0]
            _, path, sub_paths = p[1].get_tuple()
            nodes_resps = [
                        [make_path(p) for p in x]
                    for x in path]
            if sub_paths:
                mapped_sub_paths = [SubPath(parent_node=sp[0], target_node=sp[1], level=sp[2], feasibility=sp[3], paths=[make_path(p) for p in sp[4]]) for sp in sub_paths]
            else:
                mapped_sub_paths = []
                
            for nodes_resp in nodes_resps:
                feasible = all([n.feasibility not in [Feasibility.INFEASIBLE] for n in nodes_resp])
                if feasible:
                    path_resp.append(Path(path=nodes_resp, goal=goal, feasible=feasible, sub_paths=[]))
                else:
                    not_feasible_paths.append(Path(path=nodes_resp, goal=goal, feasible=feasible, sub_paths=mapped_sub_paths))

        # todo for each non feasible path resolve each feasible node and find a path to each non feasible node
        # only return the shortest non-feasible resolved path
        path_resp.extend(not_feasible_paths)
        
        return NextActionResponse(paths=path_resp, active_goals=goals,
                                  focus_tags=focus_tags, targets=deep_flatten(targets), score=score)


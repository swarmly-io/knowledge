import networkx as nx
from config import get_index_data
from enum import Enum
import logging
from typing import Any, List, Tuple
from domain_models.decisions.goals import Action, GoalStatement, Group, Tag
from graph_composition.goal_valuation import GoalValuation
from graph_composition.graph_composer import GraphComposer
from domain_models.decisions.links import TagLink
from domain_models.agent.agent import AgentDecisionState, AgentState
from minecraft_graph.graph import MineCraftGraph
from graph_traversal.feasibility import get_feasibility
from graph_traversal.find_path import find_path_with_feasibility
from domain_models.minecraft.state import AgentMCState
from domain_models.decisions.paths import NextActionResponse, Path, PathNode, SubPath
from domain_models.decisions.feasibility import Feasibility
from domain_models.workflows.workflows import WorkflowTarget
from minecraft_graph.feasibility import NodeFeasibility

from utils import deep_flatten

class AgentGraphs(str, Enum):
    MINECRAFT = 'minecraft'
    
    def make_graph(self):
        if self == AgentGraphs.MINECRAFT:
            graph_dict, _ = get_index_data()
            graph = MineCraftGraph(graph_dict)
            graph.join_graph()
            graph.init_graph_composer()
            graph.composer.compose_graphs()
            return graph

class Agent:
    def __init__(self, name: str, goals: List[GoalStatement], actions: List[Action],
                 all_tags: List[Tag], groups: List[Group]):
        self.name = name
        self.goals = goals
        self.actions = actions
        self.state: AgentState = AgentState(mcState=None, tags=[])
        self.all_tags = all_tags
        self.groups = groups
        self.setup_graphs()
        
        self.tag_links: List[TagLink] = []
        self.goal_valuation: GoalValuation = GoalValuation(self.all_tags, self.groups)

    def setup_graphs(self):
        self.graphs = {}
        for ag in AgentGraphs:
            self.graphs[ag] = ag.make_graph()
            logging.info(f"Graph {ag} initialised")
            
        for graph in self.graphs.values():
            graph.composer.update_decisions_graphs(self.name, self.goals, self.actions, self.all_tags)
    
    def get_state(self) -> AgentDecisionState:
        return AgentDecisionState(**self)

    def add_tag_links(self, links: List[TagLink]):
        tag_links = []
        for link in links:
            if link in self.tag_links:
                continue
            
            tag_link = TagLink.from_csv_entry(link)
            tag_links.append(tag_link)
        self.tag_links.extend(tag_links)
        
    def remove_tag_links(self, links: List[TagLink]):
        for link in links:
            if link in self.tag_links:
                self.tag_links.remove(link)
        
    async def run_state(self, state_update: Any):
        if isinstance(state_update, AgentMCState):
            graph: MineCraftGraph = self.graphs[AgentGraphs.MINECRAFT]
            feasibility = NodeFeasibility(graph.composer.composed_graph, self.state)
            graph.composer.set_node_feasibility(feasibility)
            # lense could be based on the state diff
            G, F = graph.composer.value_graph([], graph.composer.get_composed_graph(), flag_feasibility=True)
            graph.composer.composed_graph = G
            graph.composer.fully_connected_graph = F
    
    # assumes state has been run
    def run(self, max_paths = 3, trigger = None) -> NextActionResponse:
        targets, goals, focus_tags, score = self.run_graph()
        paths = []
        
        path_resp = self.target_to_path(max_paths, targets, paths)
        
        return NextActionResponse(paths=path_resp, active_goals=goals,
                                  focus_tags=focus_tags, targets=deep_flatten(targets), score=score)
        
    def run_graph(self) -> Tuple[List[str], List[GoalStatement], List[Tag], Any]:
        if not self.goals:
            raise Exception("No goals to select from")
        if not self.state.tags:
            raise Exception("No tags to select from")
        
        # select goals to focus on
        goals, focus_tags, scores = self.goal_valuation.select(
            self.goals, self.state.tags, goal_count=1)
        logging.info(f"Prioritising {goals[0].name} with {len(focus_tags)} tags")
        logging.info(f"Scores {scores}")
        
        # select graph based on tags and goals
        # todo graph selection
        graph, feasible_graph, fully_connected_graph = self.get_graph()
        graph.composer.set_node_feasibility(NodeFeasibility(feasible_graph, self.state))

        # updates graph with focused tags 
        resolved_targets, goals, focus_tags = graph.composer.get_path_targets(self.name, feasible_graph, self.goals, self.actions, goals, focus_tags, self.tag_links)

        max_score = max([scores.get(s).get('failure') + scores.get(s).get('success') for s in scores])
        
        return resolved_targets, goals, focus_tags, max_score

    def target_to_path(self, max_paths: int, targets: List[str], paths: list):
        # constrained by feasibility, links and goals
        graph = self.graphs[AgentGraphs.MINECRAFT].composer.get_composed_graph()
        # constrained by links and goals but not feasibility -> allows for searching of whats needed to achieve a target
        # -> sub path traverer handles this scenario - finds all paths recursively.
        # todo a fully connected graph not constrained by goals, links or feasibility -> allows for reflection and goal adjustment
        # todo a fully connected graph constrained by all goals an agent has, work backwards to create tags and tag links
        fully_connected_graph = self.graphs[AgentGraphs.MINECRAFT].composer.get_composed_graph()
        for target in targets:
            agent_node = f'agent:{self.name}' # todo should be first node
            for node in target:
                path = find_path_with_feasibility(graph, fully_connected_graph, agent_node, node)
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
        return path_resp
    
    def get_graph(self):
        graph: MineCraftGraph = self.graphs[AgentGraphs.MINECRAFT]
        feasible_graph = graph.composer.composed_graph
        fully_connected_graph = graph.composer.fully_connected_graph
        return graph,feasible_graph,fully_connected_graph

    # ensure that after the graphs have been run, goals -> domain graphs remain linked
    # needs a connected graph before running
    def get_feasibility(self, target: WorkflowTarget) -> Feasibility:
        _, feasible_graph, fully_connected_graph = self.get_graph()
        return get_feasibility(feasible_graph, fully_connected_graph, self.name, target.node, lenses=[])
    
    def get_priority(self, tags: List[str]):
        current_tags = [tag for tag in self.state.tags if tag.name in tags] or []
        needs_multiplier_dict = self.goal_valuation.calculate_needs_multiplier(self.state.tags)
        score = lambda t: self.goal_valuation.score(t, needs_multiplier_dict)
        highest_score_tag = None
        
        for tag in current_tags:
            if not highest_score_tag or score(tag) > score(highest_score_tag):
                highest_score_tag = tag
        if highest_score_tag:
            for group in self.groups:
                if group.name == highest_score_tag.group:
                    return group.rank
        return 999
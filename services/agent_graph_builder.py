import logging
from typing import List, Optional, Tuple
from pydantic import BaseModel

from models.agent_state import AgentMCState
from models.goals import Action, GoalStatement, Group, Tag
import networkx as nx
from services.goal_valuation import GoalValuation
from services.graph_composer import GraphComposer
from services.graph_scenarios import GraphScenarios
from services.models import TagLink
from domain_models.agent.agent import AgentDecisionState, AgentState
from services.state import StateRunner


class Agent(AgentDecisionState):
    def __init__(self, name: str, goals: List[GoalStatement], actions: List[Action],
                 all_tags: List[Tag], graph_dict, groups: List[Group], state_runner: StateRunner):
        self.name = name
        self.goals = goals
        self.actions = actions
        self.state: AgentState = AgentState(mcState=None, tags=[])
        self.all_tags = all_tags
        self.groups = groups
        self.graph_dict = graph_dict
        self.make_graph()
        self.tag_links: List[TagLink] = []
        self.goal_valuation: GoalValuation = GoalValuation(self.all_tags, self.groups)
        self.state_runner = state_runner

    def run_graph_and_get_targets(self, composer: GraphComposer):
        goals, focus_tags, scores = self.goal_valuation.select(
            self.goals, self.state.tags, goal_count=1)
        logging.info(f"Prioritising {goals[0].name} with {len(focus_tags)} tags")
        logging.info(f"Scores {scores}")
        
        max_score = max([scores.get(s).get('failure') + scores.get(s).get('success') for s in scores])
        
        targets = self.focus_graph_and_get_targets(composer, goals, focus_tags)
        logging.info(f"Targets {targets}")
        self.make_graph()
        self.make_graph_state()

        # get paths to each target
        resolved_targets = []
        for action, index, subindex, node in set(targets):
            resolved_target = self.resolve_target(composer, action, index, subindex, node)
            resolved_targets.append(resolved_target)
        return resolved_targets, goals, focus_tags, max_score

    def resolve_target(self, composer: GraphComposer, action: str, index: str,
                       subindex: Optional[str], node: str) -> List[str]:
        if node == '':
            node = None

        graph = composer.get_composed_graph()
        end_nodes = []
        for n in graph.nodes():
            if subindex:
                neighbours = [nei for nei in nx.neighbors(graph, n) if subindex in nei]
                if not neighbours:
                    continue

            if f"{index}:" in n:
                if node and n == f"{index}:{node}":
                    end_nodes.append(n)
                    # if not graph[f'actions:{action}'][n]:
                    #     # todo the type should be contextual, fight doesn't provide a zombie
                    #     graph.add_edge(f'actions:{action}', n, type=EdgeType.PROVIDES)
                elif not node:
                    end_nodes.append(n)
                    # if not graph[f'actions:{action}'][n]:
                    #     # todo the type should be contextual, fight doesn't provide a zombie
                    #     graph.add_edge(f'actions:{action}', n, type=EdgeType.PROVIDES)
        return end_nodes

    def make_graph(self):
        goals_graph = nx.Graph()
        for goal in self.goals:
            goals_graph.add_node(
                goal.name, **{"props": {"name": goal.name, "tags": goal.get_tags()}})

        actions_graph = nx.Graph()
        for action in self.actions:
            actions_graph.add_node(action.name, **{"props": {"name": action.name}})

        tags_graph = nx.Graph()
        for tag in self.all_tags:
            tags_graph.add_node(action.name, **{"props": {"name": tag.name, "type": tag.type}})

        observations_graph = nx.Graph()
        inventory_graph = nx.Graph()

        self.graph_dict.update({
            'goals': goals_graph,
            'actions': actions_graph,
            'tags': tags_graph,
            'observations': observations_graph,
            'inventory': inventory_graph,
        })

    def add_tag_links(self, links: List[TagLink]):
        self.tag_links.extend(links)

    # need focus tags - focus tags are either active tags or missing tags enabling success or preventing failure
    # if high health, no need to worry, if low health - issue
    # need priority service to limit goals - but priority service also needs to make a focus graph
    def focus_graph_and_get_targets(
            self, composer: GraphComposer, goals: List[GoalStatement], focus_tags: List[Tag]) -> List[Tuple[str, str]]:
        composer.remove_goal_links(self.goals)
        enriched_links = []
        composed_graph = composer.get_composed_graph()
        for el in [t.enrich(composed_graph) for t in self.tag_links]:
            enriched_links.extend(el)

        return composer.link_goals_and_get_targets(goals, focus_tags, enriched_links)

    def make_graph_state(self):
        self.state_runner.state_to_graph(
            self.graph_dict['inventory'],
            self.graph_dict['observations'],
            self.state.mcState)

    def get_fully_connected_graph(self, composer: GraphComposer, lenses=[]):
        tags_dict = {t.name: t for t in self.all_tags}

        scenarios = GraphScenarios(composer, tags_dict)
        return scenarios.get_graph(self.goals, self.tag_links, lenses)

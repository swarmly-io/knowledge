from typing import List, Optional, Tuple
from pydantic import BaseModel

from models.agent_state import AgentMCState
from models.goals import Action, GoalStatement, Group, Tag
import networkx as nx
from services.goal_scoring import GoalValuation
from services.graph_composer import GraphComposer
from services.models import TagLink

from services.state import state_to_graph

class AgentState(BaseModel):
    mcState: Optional[AgentMCState]
    tags: List[Tag]

class Agent:
    def __init__(self, name: str, goals: List[GoalStatement], actions: List[Action], all_tags: List[Tag], graph_dict, groups: List[Group]):
        self.name = name
        self.goals = goals
        self.actions = actions
        self.state : AgentState = AgentState(mcState=None, tags=[])
        self.all_tags = all_tags
        self.groups = groups
        self.graph_dict = graph_dict
        self.make_graph()
        self.tag_links: List[TagLink] = []
        self.goal_valuation: GoalValuation = GoalValuation(self.all_tags, self.groups)

    def run_graph_and_get_targets(self, composer: GraphComposer):
        goals, focus_tags = self.goal_valuation.select(self.goals, self.state.tags, goal_count=1)[0]
        print(f"Prioritising {goals[0].name} with {len(focus_tags)} tags")
        targets = self.focus_graph_and_get_targets(composer, goals, focus_tags)
        print("Targets", targets)
        self.make_graph()
        self.make_graph_state()
        
        # get paths to each target
        resolved_targets = []
        for index, node in targets:
            resolved_target = self.resolve_target(composer, index, node)
            resolved_targets.append(resolved_target)
        return resolved_targets  
            
    def resolve_target(self, composer: GraphComposer, index: str, node: str) -> List[str]:
        graph = composer.get_composed_graph()
        end_nodes = []
        for n in graph.nodes():
            if f"{index}:" in n:
                if node and n == f"{index}:{node}":
                    end_nodes.append(n)
                elif not node:
                    end_nodes.append(n)
        return end_nodes
                        
                    
            
    def make_graph(self):
        goals_graph = nx.Graph()
        for goal in self.goals:
            goals_graph.add_node(goal.name, { "props": { "name": goal.name, "tags": list(map(lambda x: x.name, goal.get_tags())) } })

        actions_graph = nx.Graph()
        for action in self.actions:
            actions_graph.add_node(action.name, { "props": { "name": action.name } })
        
        tags_graph = nx.Graph()
        for tag in self.all_tags:
            tags_graph.add_node(action.name, { "props": { "name": tag.name, "type": tag.type } })
            
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
        self.tag_links = links
        
    # need focus tags - focus tags are either active tags or missing tags enabling success or preventing failure
    # if high health, no need to worry, if low health - issue
    # need priority service to limit goals - but priority service also needs to make a focus graph
    def focus_graph_and_get_targets(self, composer: GraphComposer, goals: List[GoalStatement], focus_tags: List[Tag]) -> List[Tuple[str, str]]:
        # clear goals
        composer.remove_goal_links(self.goals)
        return composer.link_goals_and_get_targets(goals, focus_tags, self.tag_links)
        
        
    def make_graph_state(self):
        state_to_graph(self, self.graph_dict['inventory'], self.graph_dict['observations'])
        
from typing import List, Optional
from pydantic import BaseModel

from models.agent_state import AgentMCState
from models.goals import Action, GoalStatement, Tag
import networkx as nx
from services.models import TagLink

from services.state import state_to_graph

class AgentState(BaseModel):
    mcState: Optional[AgentMCState]
    tags: List[Tag]

class Agent:
    def __init__(self, name: str, goals: List[GoalStatement], actions: List[Action], all_tags: List[Tag], graph_dict):
        self.name = name
        self.goals = goals
        self.actions = actions
        self.state : AgentState = AgentState(mcState=None, tags=[])
        self.all_tags = all_tags
        self.graph_dict = graph_dict
        self.make_graph()
        self.tag_links: List[TagLink] = []
        
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
        
    def make_graph_state(self):
        state_to_graph(self, self.graph_dict['inventory'], self.graph_dict['observations'])
        

from typing import List, Optional
from pydantic import BaseModel

from models.goals import Action, GoalStatement, Group, Tag
from services.graph_composer import EdgeType

class AgentDto(BaseModel):
    name: str
    goals: List[GoalStatement]
    actions: List[Action]
    tag_list: List[Tag]
    groups: List[Group]
    
class PathNode(BaseModel):
    node: str
    type: Optional[EdgeType]
    
class Path(BaseModel):
    path: List[List[PathNode]] = []
    feasible: bool
    goal: str

class NextActionResponse(BaseModel):
    paths: List[Path]
    active_goals: List[GoalStatement]
    focus_tags: List[Tag]
    targets: List
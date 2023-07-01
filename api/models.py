
from typing import List
from pydantic import BaseModel

from models.goals import Action, GoalStatement, Group, Tag

class AgentDto(BaseModel):
    name: str
    goals: List[GoalStatement]
    actions: List[Action]
    tag_list: List[Tag]
    groups: List[Group]
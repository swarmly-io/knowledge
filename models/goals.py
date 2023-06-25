from enum import Enum
from typing import List
from pydantic import BaseModel

class TagType(str, Enum):
    SURVIVAL = "survival"
    GOAL = "goal"
    VALUE = "value"

class Tag(BaseModel):
    name: str
    type: TagType

class GoalSuccess(BaseModel):
    tag: str

class GoalFailure(BaseModel):
    tag: str

class GoalStatement(BaseModel):
    name: str
    type: TagType
    success: List[GoalSuccess] = []
    failure: List[GoalFailure] = []
    
    def get_tags(self):
        return list(map(lambda x: x.tag, self.success + self.failure))
    
class Action(BaseModel):
    name: str
    
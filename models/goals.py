from enum import Enum
from typing import List, Union
from pydantic import BaseModel

# todo extract into config
class TagType(str, Enum):
    THREAT = "threat"
    SURVIVAL = "survival"
    GOAL = "goal"
    VALUE = "value"

class Tag(BaseModel):
    name: str
    group: str
    type: TagType
    value: Union[str, int, bool] = 0
    
class TagDto(Tag):
    group_rank: int

class GoalSuccess(BaseModel):
    tag: str

class GoalFailure(BaseModel):
    tag: str
    
class GroupType(str, Enum):
    ORDERED_RANKED = "ordered_rank"
    BINARY = "binary"
    CUSTOM_FUNCTION = "function"

class Group(BaseModel):
    name: str
    type: GroupType
    rank: int

class GoalStatement(BaseModel):
    name: str
    type: TagType
    success: List[GoalSuccess] = []
    failure: List[GoalFailure] = []
    
    def get_tags(self):
        return list(map(lambda x: x.tag, self.success + self.failure))
    
    def has_tag(self, tag: Tag):
        tags = map(lambda x: x.tag, self.success + self.failure)
        contains_tag = next(filter(lambda x: x == tag.name, tags), None)
        return contains_tag
    
class Action(BaseModel):
    name: str
    
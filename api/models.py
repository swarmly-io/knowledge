from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel

from models.goals import Action, GoalStatement, Group, Tag
from services.feasibility import Feasibility
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
    feasibility: Optional[Feasibility]
    data: Optional[Dict]

class SubPath(BaseModel):
    parent_node: str
    target_node: str
    level: int
    feasibility: Feasibility
    paths: list = []

class Path(BaseModel):
    path: List[PathNode] = []
    feasible: bool
    goal: str
    sub_paths: List[SubPath]

class NextActionResponse(BaseModel):
    paths: List[Path]
    active_goals: List[GoalStatement]
    focus_tags: List[Tag]
    targets: List
    score: float = 999

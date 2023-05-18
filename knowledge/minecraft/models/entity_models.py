from __future__ import annotations
from typing import List, Optional, Union
from pydantic import BaseModel


class DmgStat(BaseModel):
    hp: Optional[int]


class Dmg(BaseModel):
    Min: Optional[DmgStat] = None
    Easy: Optional[DmgStat]
    Normal: Optional[DmgStat] = None
    Hard: Optional[DmgStat] = None


class Damage(BaseModel):
    Melee: Optional[Dmg]
    Ranged: Optional[Dmg]


class HealthStat(BaseModel):
    hp: Optional[int]


class EntityMc(BaseModel):
    id: int
    displayName: str
    name: str
    type: str
    networkId: Optional[int]
    damage: Optional[Damage]
    health: Optional[HealthStat]
    
class EntitiesDmg(BaseModel):
    id: str
    description: List[str]
    figures: List[Union[List[int], int, None]]

class Drop(BaseModel):
    item: str
    dropChance: float
    stackSizeRange: List[Union[int, None]]
    playerKill: Optional[bool] = None


class EntityDrops(BaseModel):
    id: str
    entity: str
    drops: List[Drop]


class BlockDrops(BaseModel):
    id: str
    block: str
    drops: List[Drop]
    
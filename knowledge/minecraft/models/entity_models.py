from __future__ import annotations
from typing import Optional
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
    networkId: int
    damage: Optional[Damage]
    health: Optional[HealthStat]
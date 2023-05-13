from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Position(BaseModel):
    x: float
    y: float
    z: float


class Status(BaseModel):
    health: int
    food: int
    saturation: int
    oxygen: int


class Weather(BaseModel):
    isRaining: bool
    thunderLevel: int


class Velocity(BaseModel):
    x: float
    y: float
    z: float


class Metadatum(BaseModel):
    present: Optional[bool] = None
    itemId: Optional[int] = None
    itemCount: Optional[int] = None
    type: Optional[str] = None
    name: Optional[str] = None
    value: Optional[Dict[str, Any]] = None


class Modifier(BaseModel):
    uuid: str
    amount: float
    operation: int


class MinecraftGenericMovementSpeed(BaseModel):
    value: float
    modifiers: List[Modifier]


class Attributes(BaseModel):
    minecraft_generic_movement_speed: MinecraftGenericMovementSpeed = Field(
        ..., alias='minecraft:generic.movement_speed'
    )


class CloseEntity(BaseModel):
    _events: Dict[str, Any]
    _eventsCount: int
    id: int
    position: Position
    velocity: Velocity
    yaw: float
    pitch: float
    onGround: bool
    height: float
    width: float
    effects: Dict[str, Any]
    equipment: List[Any]
    isValid: bool
    # metadata: List[Union[Optional[Union[bool, float]], Metadatum]]
    type: str
    uuid: Optional[str] = None
    mobType: Optional[str] = None
    objectType: Optional[str] = None
    displayName: Optional[str] = None
    entityType: Optional[int] = None
    name: str
    headPitch: Optional[float] = None
    attributes: Optional[Attributes] = None
    headYaw: Optional[float] = None
    objectData: Optional[int] = None
    heldItem: Optional[Any] = None
    username: Optional[str] = None
    timeSinceOnGround: Optional[int] = None
    isInWater: Optional[bool] = None
    isInLava: Optional[bool] = None
    isCollidedHorizontally: Optional[bool] = None
    isCollidedVertically: Optional[bool] = None


class Inventory(BaseModel):
    items: Dict[str, Any]
    emptySlots: int


class AgentMCState(BaseModel):
    position: Position
    status: Status
    xp: int
    time: int
    weather: Weather
    closeEntities: List[CloseEntity]
    inventory: Inventory
    world: Dict[str, Any]

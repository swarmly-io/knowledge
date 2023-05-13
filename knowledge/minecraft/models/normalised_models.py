

from typing import List, Optional, Union
from pydantic import BaseModel

from knowledge.id_model import IdModel


class BaseItem(BaseModel):
    id: int
    display_name: str
    name: str
    stack_size: int
    max_durability: Optional[int]


class RecipeItem(BaseItem):
    quantity: int


class Recipe(BaseModel):
    needs: List[RecipeItem]
    provides: RecipeItem
    # type: str # todo make enum
    # name: str


class RecipeList(BaseModel):
    id: int
    items: List[Recipe] = []


class Block(BaseModel):
    id: int
    display_name: str
    hardness: Optional[int]
    resistance: Optional[int]
    requires: List[BaseItem]
    drops: List[BaseItem]


class Food(BaseItem):
    food_points: float
    saturation: float
    effective_quality: float
    saturation_ratio: float


class IngredientItem(BaseModel):
    item: Optional[str] = None
    tag: Optional[str] = None


class SmeltingRecipe(IdModel):
    type: str
    ingredient: Union[IngredientItem, List[IngredientItem]]
    result: str
    experience: float
    cookingtime: int
    name: str
    group: Optional[str] = None

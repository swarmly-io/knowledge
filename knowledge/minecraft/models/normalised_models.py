

from typing import List, Optional
from pydantic import BaseModel

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
    
class RecipeList(BaseModel):
    id: int
    items: List[Recipe] = []

class FurnaceRecipe(BaseModel):
    id: int
    input: RecipeItem
    output: RecipeItem
    
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
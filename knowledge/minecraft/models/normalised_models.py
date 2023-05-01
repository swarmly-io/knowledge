

from typing import List, Optional
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    display_name: str
    name: str
    stack_size: int
    quantity: int
    max_durability: Optional[int]

class RecipeItem(BaseModel):
    needs: List[Item]
    provides: Item
    
class Recipe(BaseModel):
    id: int
    items: List[RecipeItem] = []
    
class Block(BaseModel):
    id: int
    display_name: str
    hardness: Optional[int]
    resistance: Optional[int]
    requires: List[Item]
    drops: List[Item]
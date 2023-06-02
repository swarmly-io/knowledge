from typing import Dict
from pydantic import BaseModel


class StoredLootGraph(BaseModel):
    id: str
    graph: Dict

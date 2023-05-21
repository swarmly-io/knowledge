
from typing import Dict
from pydantic import BaseModel


class StoredBlockGraph(BaseModel):
    id: int
    name: str
    graph: Dict

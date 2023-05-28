
from typing import Callable, List, Tuple
from pydantic import BaseModel


class JoinInner(BaseModel):
    index: str
    filter: Callable[[object, object], bool]
    
class Join(JoinInner):
    join: JoinInner
    
class LinkingInstruction(BaseModel):
    source: str
    target: str
    link: Callable[[object, object], bool]
    
class OneToManyJoins(BaseModel):
    sources: List[Tuple[str, object]]
    on: object
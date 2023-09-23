
from typing import Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel

from services.lambda_utils import parse_function
import networkx as nx


class JoinInner(BaseModel):
    index: str
    filter: Callable[[object, object], bool]
    filter_str: str = ""

    def make_str(self):
        self.filter_str = parse_function(self.filter)


class Join(JoinInner):
    join: Optional[JoinInner]


class Joins(Dict[str, Join]):

    def make_strings(self):
        for k, v in self.items():
            for vk, vv in v.items():
                vv.make_str()


class LinkingInstruction(BaseModel):
    source: str
    target: str
    link: Callable[[object, object], bool]


class OneToManyJoins(BaseModel):
    sources: List[Tuple[str, object]]
    on: object


class Node(BaseModel):
    name: str

    def to_node(self):
        return (self.name, self.__dict__)


class TagLink(BaseModel):
    tag: str
    action: str
    index: str
    subindex: Optional[str]
    node: Optional[str]

    def from_csv_entry(entry: str):
        try:
            tag, action, index, node = (
                entry + ",,,,").replace(" ", "").split(",")[0:4]
            if ':' in index:
                index, subindex = index.split(':')
            else:
                subindex = None
            tag_link = TagLink(
                tag=tag,
                action=action,
                index=index,
                node=node,
                subindex=subindex)
            return tag_link
        except Exception as e:
            print("Error in tag link", entry)
            raise Exception(f"Error creating tag link: {entry}")

    def enrich(self, graph: nx.DiGraph):
        # try to find a link between action, index, and node,
        # if there isn't a direct link, try to create a new tag link with

        return [self]

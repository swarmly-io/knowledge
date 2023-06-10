import logging
import timeit
from typing import List
from fastapi import Depends, FastAPI, Response
import dill as pickle
from pydantic import BaseModel
from models.agent_state import AgentMCState
from services.mini_graph_dict import graph_dict
from services.agent_config import lenses, linking_instructions, one_to_many_join_graphs
from services.graph_composer import GraphComposer
from services.find_path import find_path
from fastapi.middleware.cors import CORSMiddleware

from services.state import state_to_graph

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("my_logger")

class Graph:
    def __init__(self) -> None:
        self.composer: GraphComposer = None
        self.state : AgentMCState = None
    
    def set_composer(self, composer):
        self.composer = composer 
        
    def set_state(self, state: AgentMCState):
        self.state = state
        
    def run_state(self):
        state_to_graph(self.state)
        
    def get_graph(self):
        return self
    
    def find_path(self, source_node, target_node, lenses = []):
        # todo validate lenses
        if not lenses:
            filtered_graph = self.composer.get_composed_graph()
        else:
            filtered_graph = self.composer.apply_lenses(lenses)
        
        unfiltered_graph = self.composer.get_composed_graph()
        path = find_path(filtered_graph, unfiltered_graph, source_node, target_node)
        return path
    
    def build_graph(self):
        if not self.composer:
            self.composer = GraphComposer(graph_dict, linking_instructions, one_to_many_join_graphs, lenses)
            self.set_composer(self.composer)

        t = timeit.timeit(self.composer.compose_graphs, number=1)
        print(f"Built in {t}")

        g = self.composer.get_composed_graph()
        return dict(nodes=len(g.nodes()), edges= len(g.edges()))
        

graph = Graph()

# init graph needs to take all info from agent_config
@app.post("/init")
def init_graph(graph: Graph = Depends(graph.get_graph)):
    return graph.build_graph()


@app.get("/graph")
def get_graph(graph: Graph = Depends(graph.get_graph)):
    g = graph.composer.get_composed_graph()
    return dict(nodes=g.nodes(data=True), edges= [e for e in g.edges(data=True)])
 
# get a set of paths to a goal
# params: preapply lenses, looking for needs/provides? Something else? 
# define recursion depth/max time to search?
class FindPathRequest(BaseModel):
    source_node: str
    target_node: str
    lenses: List[str] = []

@app.post("/find_path")
def find_path_to_target(request: FindPathRequest, graph: Graph = Depends(graph.get_graph)):
    return graph.find_path(request.source_node, request.target_node, request.lenses)
    
@app.post("/update_state")
def update_state(state: AgentMCState, graph: Graph = Depends(graph.get_graph)):
    # persist state
    graph.set_state(state)
    # run state_to_graph - clears and updates individual graph
    graph.run_state()
    # rerun graph composer
    return graph.build_graph()

# adding a subgraph should recompute the graph
# needs links, filters and joins
@app.post("/add_sub_graph")
def add_sub_graph():
    return

@app.post("/remove_sub_graph")
def remove_sub_graph():
    return

# never get the whole graph
@app.post("/get_subgraph")
def get_sub_graph():
    return

@app.post("/add_lense")
def add_lense():
    return

@app.post("/remove_lense")
def remove_lense():
    return

@app.get("/hello")
def hello():
    pickled_obj = pickle.dumps(lenses)
    return Response(content=pickled_obj, media_type="application/octet-stream")

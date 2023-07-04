import logging
from typing import List
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from api.graph import GraphService
from api.models import AgentDto
from models.agent_state import AgentMCState
from fastapi.middleware.cors import CORSMiddleware

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

graph = GraphService()

@app.post("/create_agent")
def add_goals(agent: AgentDto, graph: GraphService = Depends(graph.get_graph)):
    graph.create_agent(agent)
    return { 'message': f'agent created: {agent.name}' }
     
@app.post("/{agent}/tag_links")
def add_tag_links(agent:str, links: List[str], graph: GraphService = Depends(graph.get_graph)):
    graph.add_tag_links(links)
    return { 'message': f'added links: {len(links)}' }

@app.post("/agent/{name}/run")
def run(name: str, graph: GraphService = Depends(graph.get_graph)):
    return graph.run()

@app.post("/agent/{name}/active_tags")
def add_active_tags(name: str, tags: List[str], graph: GraphService = Depends(graph.get_graph)):
    return graph.add_active_tags(tags)

# init graph needs to take all info from agent_config
@app.post("/init")
def init_graph(graph: GraphService = Depends(graph.get_graph)):
    return graph.build_graph()

@app.get("/graph")
def get_graph(graph: GraphService = Depends(graph.get_graph)):
    g = graph.composer.get_composed_graph()
    return dict(nodes=g.nodes(data=True), edges= [e for e in g.edges(data=True)])
 
# get a set of paths to a goal
# params: preapply lenses, looking for needs/provides? Something else? 
# define recursion depth/max time to search?
class FindPathRequest(BaseModel):
    source_node: str
    target_node: str
    lenses: List[str] = []
    tags: List[str] = []

@app.post("/find_path")
def find_path_to_target(request: FindPathRequest, graph: GraphService = Depends(graph.get_graph)):
    return graph.find_path(request.source_node, request.target_node, request.lenses)

@app.post("/work_flow")
def make_work_flow(request: FindPathRequest, graph: GraphService = Depends(graph.get_graph)):
    return graph.make_workflow(request.source_node, request.target_node, request.lenses)
    
@app.post("/update_state")
def update_state(state: AgentMCState, graph: GraphService = Depends(graph.get_graph)):
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

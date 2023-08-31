import logging
from typing import Dict, List
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from api.agent import AgentService
from api.models import AgentDto
from models.agent_state import AgentMCState
from fastapi.middleware.cors import CORSMiddleware

from models.goals import TagDto

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

class Agents:
    def __init__(self) -> None:
        self.agents: Dict[str, AgentService] = {}
        
    def get_agents(self):
        return self
        
    def get_agent(self, name: str) -> AgentService:
        if name not in self.agents:
            raise Exception("Agent not found")
        return self.agents.get(name)
    
    def new(self, name) -> AgentService:
        if name in self.agents:
            raise Exception("Agent already exists")
        self.agents[name] = AgentService()
        return self.agents[name]

class FindPathRequest(BaseModel):
    source_node: str
    target_node: str
    lenses: List[str] = []
    tags: List[str] = []

agents = Agents()

# init graph needs to take all info from agent_config
@app.post("/{name}/init")
def init_graph(name:str, agents = Depends(agents.get_agents)):
    agent = agents.new(name)
    return agent.build_graph()

@app.post("/{name}/create_agent")
def add_goals(name: str, agent_dto: AgentDto, agent: Agents = Depends(agents.get_agent)):
    agent.create_agent(agent_dto)
    return { 'message': f'agent created: {agent_dto.name}' }
     
@app.post("/{name}/tag_links")
def add_tag_links(name:str, links: List[str], agent: AgentService = Depends(agents.get_agent)):
    agent.add_tag_links(links)
    return { 'message': f'added links: {len(links)}' }

@app.post("/agent/{name}/active_tags")
def add_active_tags(name: str, tags: List[str], agent: AgentService = Depends(agents.get_agent)) -> List[TagDto]:
    return agent.add_active_tags(tags)

@app.post("/{name}/update_state")
def update_state(name: str, state: AgentMCState, agent: AgentService = Depends(agents.get_agent)):
    # persist state
    agent.set_state(state)
    # run state_to_graph - clears and updates individual graph
    agent.run_state()
    # rerun graph composer
    return agent.build_graph()

@app.post("/agent/{name}/run")
def run(name: str, agent: AgentService = Depends(agents.get_agent)):
    result = agent.run(name)
    return result

@app.get("/{name}/graph")
def get_graph(name: str, agent: AgentService = Depends(agents.get_agent)):
    g = agent.composer.get_composed_graph()
    return dict(nodes=g.nodes(data=True), edges= [e for e in g.edges(data=True)])

@app.post("/{name}/find_path")
def find_path_to_target(name:str, request: FindPathRequest, agent: AgentService = Depends(agents.get_agent)):
    return agent.find_path(request.source_node, request.target_node, request.lenses)

@app.get("/health")
def health():
    return { 'health': 'OK' }

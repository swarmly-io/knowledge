import logging
from typing import Dict, List, Optional, Union
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from api.agent import AgentService
from api.models import AgentDto
from fastapi.middleware.cors import CORSMiddleware

from domain_models.decisions.goals import TagDto
from domain_models.workflows.workflows import WorkflowTarget
from domain_models.decisions_points.events import ScheduledTrigger, AggregateTrigger
from domain_models.minecraft.state import AgentMCState
from domain_models.decisions.feasibility import Feasibility

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

@app.post("/{name}/init")
async def init_graph(name: str, agents=Depends(agents.get_agents)):
    _ = agents.new(name)
    return {'message': f'agent created: {name}'}


@app.post("/{name}/create_agent")
def add_goals(name: str, agent_dto: AgentDto, agent: Agents = Depends(agents.get_agent)):
    agent.create_agent(agent_dto)
    return {'message': f'agent created: {agent_dto.name}'}


@app.post("/{name}/tag_links")
def add_tag_links(name: str, links: List[str], agent: AgentService = Depends(agents.get_agent)):
    agent.add_tag_links(links)
    return {'message': f'added links: {len(links)}'}


@app.post("/agent/{name}/active_tags")
def add_active_tags(name: str, tags: List[str], agent: AgentService = Depends(
        agents.get_agent)) -> List[TagDto]:
    return agent.add_active_tags(tags)


@app.post("/agent/{name}/run")
def run(name: str, agent: AgentService = Depends(agents.get_agent)):
    result = agent.agent.run()
    return result

@app.post("/agent/{name}/decision")
def run(name: str, trigger: Union[ScheduledTrigger, AggregateTrigger], agent: AgentService = Depends(agents.get_agent)):
    if not agent.agent.state.tags:
        raise Exception("No tags found")
    
    result = agent.agent.run(trigger=trigger)
    return result


@app.get("/{name}/graph")
def get_graph(name: str, agent: AgentService = Depends(agents.get_agent)):
    g = agent.composer.get_composed_graph()
    return dict(nodes=g.nodes(data=True), edges=[e for e in g.edges(data=True)])


@app.post("/{name}/find_path")
def find_path_to_target(name: str, request: FindPathRequest,
                        agent: AgentService = Depends(agents.get_agent)):
    return agent.find_path(request.source_node, request.target_node, request.lenses)


class QaRequest(BaseModel):
    action_node: str
    act_upon_node: str
    end_node: str

@app.post("/agent/{name}/priority")
def get_tag_priority(name: str, tags: List[str], agent: AgentService = Depends(agents.get_agent)) -> int:
    return agent.agent.get_priority(tags)

@app.post("/agent/{name}/feasibility")
def get_node_feasibility(name: str, target: WorkflowTarget, agent: AgentService = Depends(agents.get_agent)) -> Feasibility:
    # todo consolodate lenses and added type back in
    return agent.agent.get_feasibility(target)

@app.get("/agent/{name}/state")
def get_state(name: str, agent: AgentService = Depends(agents.get_agent)) -> Optional[AgentMCState]:
    return agent.agent.state.mcState

@app.post("/agent/{name}/state")
async def update_state(name: str, state: AgentMCState, agent: AgentService = Depends(agents.get_agent)):
    # persist state
    agent.set_mc_state(state)
    # run state_to_graph - clears and updates individual graph
    if agent.agent.state.tags:
        await agent.agent.run_state(state) # should be non blocking

@app.get("/health")
def health():
    return {'health': 'OK'}

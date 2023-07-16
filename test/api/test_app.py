import json
from fastapi.testclient import TestClient
import pytest

from api.app import app
from api.models import AgentDto
from models.agent_state import AgentMCState
client = TestClient(app, raise_server_exceptions=False)

def test_init():
    # Test successful user creation
    response = client.post("/init")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] > 0
    assert data["edges"] > 0
   
   
# todo - needs to update state to include inventory item before we can sell it 
def test_find_succesful_path():
    test_init()
    # Test successful user creation
    body = {
        "source_node": "agent:bill",
        "target_node": "trade:credit",
        "lenses": ["only_trades","only_ask"]
    }
    # 280
    with open("./test/api/sampleagent.json", 'r') as f:
      data = AgentDto(**json.load(f))
      agent_response = client.post("/create_agent", json=data.dict())
      assert agent_response.status_code == 200
    with open("./test/api/samplelinks.json", 'r') as f:
      data = json.load(f)
      links_response = client.post("/bill/tag_links", json=data)
      assert links_response.status_code == 200
    active_tags_response = client.post("/agent/bill/active_tags", json=["health_high", "zombie_far", "food_inventory_high", "food_high", "got_shelter", "no_credit"])
    assert active_tags_response.status_code == 200
    with open("./test/api/samplestate.json", 'r') as f:
      data = AgentMCState(**json.load(f))
      state_response = client.post("/bill/update_state", json=data.dict())
      assert state_response.status_code == 200
    
    response = client.post("/find_path", json = body)
    assert response.status_code == 200
    data = response.json()
    assert data[0] == True
    expected_path = [
      {
        "node": "agent:bill",
        "type": ""
      },
      {
        "node": "goals:make money",
        "type": "GOAL"
      },
      {
        "node": "actions:trade",
        "type": None # todo should be ACTION
      },
      {
        "node": "trade:ask",
        "type": "ACT_UPON"
      },
      {
        "node": "inventory:wooden_planks",
        "type": "NEEDS" # todo should be CONTAINS
      },
      {
        "node": "trade:credit",
        "type": "PROVIDES"
      }
    ]
    
    assert expected_path == data[1][1]
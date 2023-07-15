from fastapi.testclient import TestClient
import pytest

from api.app import app
client = TestClient(app, raise_server_exceptions=False)

def test_init():
    # Test successful user creation
    response = client.post("/init")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] > 0
    assert data["edges"] > 0
   
   
@pytest.mark.skip()
# todo - needs to update state to include inventory item before we can sell it 
def test_find_succesful_path():
    test_init()
    # Test successful user creation
    body = {
        "source_node": "agent:bill",
        "target_node": "trade:credit",
        "lenses": ["only_trades","only_ask"]
    }
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
        "node": "goals:make_money",
        "type": "GOAL"
      },
      {
        "node": "actions:trade",
        "type": "ACTION"
      },
      {
        "node": "trade:ask",
        "type": "ACT_UPON"
      },
      {
        "node": "items:stone",
        "type": "NEEDS"
      },
      {
        "node": "trade:credit",
        "type": "PROVIDES"
      }
    ]
    
    assert expected_path in data[1]
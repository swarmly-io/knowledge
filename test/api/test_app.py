import json
from fastapi.testclient import TestClient
import pytest

from api.app import app
from api.models import AgentDto, NextActionResponse
from domain_models.agent.agent import AgentMCState
from domain_models.decisions.feasibility import Feasibility

client = TestClient(app, raise_server_exceptions=True)

names = ['bill', 'steve', 'jim', 'jack', 'jerry', 'jimbo']


def test_init():
    # Test successful user creation
    name = names.pop()
    response = client.post(f"/{name}/init")
    assert response.status_code == 200
    data = response.json()
    return name


def setup_agent():
    name = test_init()
    with open("./test/api/sampleagent.json", 'r') as f:
        data = AgentDto(**json.load(f))
        data.name = name
        agent_response = client.post(f"/{name}/create_agent", json=data.dict())
        assert agent_response.status_code == 200
    with open("./test/api/samplelinks.json", 'r') as f:
        data = json.load(f)
        links_response = client.post(f"/{name}/tag_links", json=data)
        assert links_response.status_code == 200
    active_tags_response = client.post(
        f"/agent/{name}/active_tags",
        json=[
            "health_high",
            "zombie_close",
            "food_inventory_high",
            "food_high",
            "got_shelter",
            "no_credit"])
    assert active_tags_response.status_code == 200
    
    with open("./test/api/samplestate.json", 'r') as f:
        data = AgentMCState(**json.load(f))
        state_response = client.post(f"/agent/{name}/state", json=data.dict())
        assert state_response.status_code == 200
    
    return name


@pytest.mark.skip("Trade currently only defined in mini graph")
# todo - needs to update state to include inventory item before we can sell it
def test_find_succesful_path():
    name = test_init()
    # Test successful user creation
    body = {
        "source_node": "agent:bill",
        "target_node": "trade:credit",
    }
    # 280
    with open("./test/api/sampleagent.json", 'r') as f:
        data = AgentDto(**json.load(f))
        data.name = name
        agent_response = client.post(f"/{name}/create_agent", json=data.dict())
        assert agent_response.status_code == 200
    with open("./test/api/samplelinks.json", 'r') as f:
        data = json.load(f)
        links_response = client.post(f"/{name}/tag_links", json=data)
        assert links_response.status_code == 200
    active_tags_response = client.post(
        f"/agent/{name}/active_tags",
        json=[
            "health_high",
            "zombie_far",
            "food_inventory_high",
            "food_high",
            "got_shelter",
            "no_credit"])
    assert active_tags_response.status_code == 200
    with open("./test/api/samplestate.json", 'r') as f:
        data = AgentMCState(**json.load(f))
        state_response = client.post(f"/agent/{name}/state", json=data.dict())
        assert state_response.status_code == 200

    response = client.post(f"/{name}/find_path", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data[0] == True
    expected_path = [
        {
            "node": f"agent:{name}",
            "type": ""
        },
        {
            "node": "goals:make money",
            "type": "GOAL"
        },
        {
            "node": "actions:trade",
            "type": None  # todo should be ACTION
        },
        {
            "node": "trade:ask",
            "type": "ACT_UPON"
        },
        {
            "node": "inventory:wooden_planks",
            "type": "NEEDS"  # todo should be CONTAINS
        },
        {
            "node": "trade:credit",
            "type": "PROVIDES"
        }
    ]

    assert expected_path == data[1][1]


def test_run_agent_succesfully():
    name = test_init()
    with open("./test/api/sampleagent.json", 'r') as f:
        data = AgentDto(**json.load(f))
        data.name = name
        agent_response = client.post(f"/{name}/create_agent", json=data.dict())
        assert agent_response.status_code == 200
    with open("./test/api/samplelinks.json", 'r') as f:
        data = json.load(f)
        links_response = client.post(f"/{name}/tag_links", json=data)
        assert links_response.status_code == 200
    active_tags_response = client.post(
        f"/agent/{name}/active_tags",
        json=[
            "health_high",
            "zombie_close",
            "food_inventory_high",
            "food_high",
            "got_shelter",
            "no_credit",
            "no_tools"])
    assert active_tags_response.status_code == 200
    with open("./test/api/samplestate.json", 'r') as f:
        data = AgentMCState(**json.load(f))
        state_response = client.post(f"/agent/{name}/state", json=data.dict())
        assert state_response.status_code == 200

    response = client.post(f"/agent/{name}/run")
    assert response.status_code == 200
    data = NextActionResponse(**response.json())

    assert "got_tools" in list(map(lambda x: x.name, data.focus_tags))
    wooden_axe_path = [
        (f"agent:{name}", None),
        ("goals:have defence", "GOAL"),
        ("actions:craft", 'ACTION'),
        ("recipes:701", "ACT_UPON"),
        ("items:wooden_pickaxe", "PROVIDES")]
    assert list(map(lambda x: (x.node, x.type),
                    next(filter(lambda x: x.goal == 'items:wooden_pickaxe', data.paths)).path)) == wooden_axe_path


def test_run_agent_succesfully_multi_runs():
    name = test_init()
    with open("./test/api/sampleagent.json", 'r') as f:
        data = AgentDto(**json.load(f))
        data.name = name
        agent_response = client.post(f"/{name}/create_agent", json=data.dict())
        assert agent_response.status_code == 200
    with open("./test/api/samplelinks.json", 'r') as f:
        data = json.load(f)
        links_response = client.post(f"/{name}/tag_links", json=data)
        assert links_response.status_code == 200
    active_tags_response = client.post(
        f"/agent/{name}/active_tags",
        json=[
            "health_high",
            "zombie_close",
            "food_inventory_high",
            "food_high",
            "got_shelter",
            "no_credit",
            "no_tools"])
    assert active_tags_response.status_code == 200
    with open("./test/api/samplestate.json", 'r') as f:
        data = AgentMCState(**json.load(f))
        state_response = client.post(f"/agent/{name}/state", json=data.dict())
        assert state_response.status_code == 200

    response = client.post(f"/agent/{name}/run")
    assert response.status_code == 200
    data = NextActionResponse(**response.json())
    assert data.score > 0 and data.score < 999
    assert "got_tools" in list(map(lambda x: x.name, data.focus_tags))
    wooden_axe_path = [
        (f"agent:{name}", None, Feasibility.FEASIBLE),
        ("goals:have defence", "GOAL", None), # todo, fix this
        ("actions:craft", "ACTION", Feasibility.FEASIBLE),
        ("recipes:701", "ACT_UPON", Feasibility.FEASIBLE),
        ("items:wooden_pickaxe", "PROVIDES", Feasibility.FEASIBLE)]
    
    assert list(map(lambda x: (x.node, x.type, x.feasibility),
                    next(filter(lambda x: x.goal == 'items:wooden_pickaxe', data.paths)).path)) == wooden_axe_path

    active_tags_response = client.post(
        f"/agent/{name}/active_tags",
        json=[
            "health_low",
            "zombie_close",
            "food_inventory_high",
            "food_high",
            "got_shelter",
            "no_credit",
            "got_tools"])
    assert active_tags_response.status_code == 200
    response = client.post(f"/agent/{name}/run")
    assert response.status_code == 200
    data = NextActionResponse(**response.json())
    path = list(map(lambda x: x.node, next(filter(lambda x: x.goal == 'items:apple', data.paths)).path))
    assert 'items:apple' in path
    assert 'foods:apple' in path

    active_tags_response = client.post(
        f"/agent/{name}/active_tags",
        json=[
            "health_high",
            "zombie_far",
            "food_inventory_high",
            "food_high",
            "got_shelter",
            "no_credit",
            "got_tools"])
    assert active_tags_response.status_code == 200
    response = client.post(f"/agent/{name}/run")
    assert response.status_code == 200
    data = NextActionResponse(**response.json())
    assert not data.paths  # trades not implemented
    assert all(map(lambda x: x.name in ['completed_job',
               'got_credit', 'no_credit'], data.focus_tags))
    assert data.active_goals[0].name == 'make money'

def test_app_returns_priority_for_set_of_tags():
    name = setup_agent()
    
    priority = client.post(
        f"/agent/{name}/priority",
        json=["health_high"])
    assert priority.json() == 2
    
    priority = client.post(
        f"/agent/{name}/priority",
        json=["zombie_close", "health_high"])
    assert priority.json() == 1
    
    priority = client.post(
        f"/agent/{name}/priority",
        json=["no_tools"])
    assert priority.json() == 999

def test_app_returns_feasibility():
    name = setup_agent()
    
    feasibility = client.post(
        f"/agent/{name}/feasibility",
        json={
            "node": "items:wooden_axe",
            "action": "craft",
            "target": {
                "item": 706,
                "quantity": 1
            }
        })
    assert feasibility.json() == Feasibility.FEASIBLE
    
    feasibility = client.post(
        f"/agent/{name}/feasibility",
        json={
            "node": "items:iron_pickaxe",
            "action": "craft",
            "target": {
                "item": 706,
                "quantity": 1
            }
        })
    assert feasibility.json() == Feasibility.INFEASIBLE


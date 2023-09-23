# Sample pytest fixture implementation

from enum import Enum
import pytest
import networkx as nx

from services.find_path import find_backward_paths

# Define the NodeType Enum
class NodeType(Enum):
    GOAL = "Goal"
    ACTION = "Action"
    OBJECT = "Object"

@pytest.fixture
def minecraft_graph_and_states():
    # Graph setup as provided earlier
    G_minecraft = nx.DiGraph()
    nodes = {
        NodeType.GOAL: ['Get a tool'],
        NodeType.ACTION: ['Mine wood', 'Craft wooden pickaxe', 'Mine stone', 'Craft stone pickaxe', 
                          'Mine iron', 'Craft iron pickaxe', 'Smelt iron ore', 'Mine rocks', 'Trade'],
        NodeType.OBJECT: ['Wood', 'Wooden pickaxe', 'Stone', 'Stone pickaxe', 'Iron ore', 'Iron ingots', 'Iron pickaxe']
    }
    for node_type, node_list in nodes.items():
        G_minecraft.add_nodes_from(node_list, type=node_type.value)
    edges = [
        ('Mine wood', 'Wood'), 
        ('Craft wooden pickaxe', 'Wooden pickaxe'),
        ('Mine stone', 'Stone'),
        ('Craft stone pickaxe', 'Stone pickaxe'),
        ('Mine iron', 'Iron ore'),
        ('Craft iron pickaxe', 'Iron pickaxe'),
        ('Smelt iron ore', 'Iron ingots'),
        ('Wood', 'Craft wooden pickaxe'),
        ('Wooden pickaxe', 'Mine stone'),
        ('Stone', 'Craft stone pickaxe'),
        ('Stone pickaxe', 'Mine rocks'),
        ('Stone pickaxe', 'Mine iron'),
        ('Iron ore', 'Smelt iron ore'),
        ('Iron ingots', 'Craft iron pickaxe'),
        ('Trade', 'Iron pickaxe'),
        ('Get a tool', 'Trade'),
    ]
    G_minecraft.add_edges_from(edges)
    
    # State dictionaries
    empty_state_dict = {}
    populated_state_dict = {'Wood': True, 'Stone pickaxe': True, 'Trade': True}
    
    return G_minecraft, empty_state_dict, populated_state_dict

def test_base_case(minecraft_graph_and_states):
    G_minecraft, empty_state_dict, _ = minecraft_graph_and_states
    paths = find_backward_paths(G_minecraft, 'Iron pickaxe', empty_state_dict)
    expected_paths = [
        ['Iron pickaxe', 'Craft iron pickaxe', 'Iron ingots', 'Smelt iron ore', 'Iron ore', 'Mine iron', 'Stone pickaxe', 'Craft stone pickaxe', 'Stone', 'Mine stone', 'Wooden pickaxe', 'Craft wooden pickaxe', 'Wood', 'Mine wood'], 
        ['Iron pickaxe', 'Trade', 'Get a tool']]
    assert paths == expected_paths, f"Expected {expected_paths}, but got {paths}"

def test_state_populated_case(minecraft_graph_and_states):
    G_minecraft, _, populated_state_dict = minecraft_graph_and_states
    paths = find_backward_paths(G_minecraft, 'Iron pickaxe', populated_state_dict)
    expected_paths = [['Iron pickaxe', 'Craft iron pickaxe', 'Iron ingots', 'Smelt iron ore', 'Iron ore', 'Mine iron', 'Stone pickaxe'],
                      ['Iron pickaxe', 'Trade']]
    assert paths == expected_paths, f"Expected {expected_paths}, but got {paths}"
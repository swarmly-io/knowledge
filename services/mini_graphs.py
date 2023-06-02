import networkx as nx
from services.graph_composer import EdgeType

blocks_graph = nx.Graph()
blocks_graph.add_node('cobblestone', props={ 'name': 'cobblestone', 'drops': ['stone'], 'requires': ['wooden_pickaxe', 'stone_pickaxe'], 'material': 'mineable/pickaxe'})
blocks_graph.add_node('dirt', props={ 'name': 'dirt', 'drops': ['dirt'], 'requires':[], 'material': 'mineable/shovel'})
blocks_graph.add_node('wood', props={ 'name': 'wood', 'drops': ['wood'], 'requires':[], 'material': 'mineable/axe' })
blocks_graph.add_node('carrot', props={ 'name': 'carrot', 'drops': ['carrot'], 'requires':[], 'material': 'mineable/axe' })

items_graph = nx.Graph()
items_graph.add_node('stone', props={'name': 'stone' })
items_graph.add_node('dirt', props={'name': 'dirt' })
items_graph.add_node('wood', props={'name': 'wood' })
items_graph.add_node('carrot', props={'name': 'carrot' })
items_graph.add_node('stone_pickaxe', props={'name': 'stone_pickaxe'})
items_graph.add_node('wooden_pickaxe', props={'name': 'wooden_pickaxe'})
items_graph.add_node('stick', props={'name': 'stick'})
items_graph.add_node('plank', props={'name': 'plank'})

recipes_graph = nx.Graph()
recipes_graph.add_node('wooden_pickaxe', props = { 'provides': { 'quantity': 1, 'name': 'wooden_pickaxe' },'needs': [{ 'name': 'stick', 'quantity': 2 }, { 'name': 'plank', 'quantity': 3 }] })
recipes_graph.add_node('stick', props = { 'provides': { 'quantity': 4, 'name': 'stick' }, 'needs': [{ 'name': 'plank', 'quantity': 2 }] })
recipes_graph.add_node('plank', props = { 'provides': { 'quantity': 4, 'name': 'plank' }, 'needs': [{ 'name': 'wood', 'quantity': 1 }] })

food_graph = nx.Graph()
food_graph.add_node('apple', props={'name': 'apple'})
food_graph.add_node('bread', props={'name': 'bread'})
food_graph.add_node('carrot', props={'name': 'carrot'})

feasible_action_graph = nx.Graph()
feasible_action_graph.add_node(EdgeType.OBSERVED)
feasible_action_graph.add_node(EdgeType.ACT_UPON)

"""yaml
    actions:
     - name: mine
       joins:
         - index: items
           filter:
              when: pickaxe
              in: name
           join:
              index: blocks
              filter:
                 when: material
                 eq: mineable/pickaxe
     - name: collect
       joins:
        - index: items
          filter:
"""

# todo tool graph, so pickaxe links to mineable, sword to zombie

actions_graph = nx.Graph()
actions_graph.add_node('mine', props = { 'name': 'mine' })
actions_graph.add_node('collect', props = { 'name': 'collect'  })
actions_graph.add_node('fight', props = { 'name':'fight' })
actions_graph.add_node('hunt', props = { 'name':'hunt'  })
actions_graph.add_node('eat', props = { 'name':'eat'  })
actions_graph.add_node('craft', props = { 'name':'craft' })
actions_graph.add_node('trade', props={ 'name': 'trade' })

"""yaml
    agent:
        name: bill
        actions:
         - mine
         - collect
         - fight
         - hunt
         - eat
         - craft
         - smelt
         - trade
        inventory:
         - name: wooden_pickaxe
           quantity: 1
        goals:
          - name: make_money
            objective: money
        
"""
agent_graph = nx.Graph()
agent_graph.add_node('bill', props={ 'actions': ['mine', 'collect', 'fight', 'hunt', 'eat', 'craft', 'smelt', 'trade'] })

goals_graph = nx.Graph()
goals_graph.add_node('make_money', props={'name': 'make_money', 'objective': ['money'] })

"""yaml
    abstract_actions:
        - trade:
            bid: 
              joins...
            ask:
            debit:
            credit:
            money:
"""


trade_graph = nx.Graph()
trade_graph.add_node('bid', props={ 'name': 'bid'  }) # money -> debit -> all items
trade_graph.add_node('ask', props={ 'name': 'ask' }) # inventory items -> credit -> money
trade_graph.add_node('debit', props={'name': 'debit' }) 
trade_graph.add_node('credit', props={'name': 'credit' }) # could be , { 'index': 'trade', 'filter': lambda x,y: 'money' in x['name'] }
trade_graph.add_node('money', props={'name': 'money' })

inventory_graph = nx.Graph()
#inventory_graph.add_node('wooden_pickaxe', props = { 'name': 'wooden_pickaxe', 'quantity': 1 })
observations_graph = nx.Graph()
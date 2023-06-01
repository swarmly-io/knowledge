import networkx as nx
from sample_graph.graph_composer import EdgeType

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
recipes_provides_join = [{ 'index': 'items', 'filter': lambda x,y: x['name'] in [z['name'] for z in y['needs']] , 'type': EdgeType.NEEDS, 
                          'join': {'index': 'items', 'filter': lambda x,y: x['name'] == y['provides']['name'], 'type': EdgeType.PROVIDES } }]
recipes_graph.add_node('wooden_pickaxe', 
                       props = { 'provides': { 'quantity': 1, 'name': 'wooden_pickaxe' },'needs': [{ 'name': 'stick', 'quantity': 2 }, { 'name': 'plank', 'quantity': 3 }],
                                'joins': recipes_provides_join })
recipes_graph.add_node('stick', 
                       props = { 'provides': { 'quantity': 4, 'name': 'stick' }, 'needs': [{ 'name': 'plank', 'quantity': 2 }],
                                'joins': recipes_provides_join })
recipes_graph.add_node('plank', props = { 'provides': { 'quantity': 4, 'name': 'plank' }, 'needs': [{ 'name': 'wood', 'quantity': 1 }],
                                         'joins': recipes_provides_join })
# # todo action:recipes -> wooden_pickaxe -> needs items -> provides item
# recipes_graph.add_edge('recipes:wooden_pickaxe', 'items:stick')
# recipes_graph.add_edge('recipes:wooden_pickaxe', 'items:plank')
# recipes_graph.add_edge('items:stick', 'items:wooden_pickaxe')
# recipes_graph.add_edge('items:plank', 'items:wooden_pickaxe')



food_graph = nx.Graph()
food_graph.add_node('apple', props={'name': 'apple'})
food_graph.add_node('bread', props={'name': 'bread'})
food_graph.add_node('carrot', props={'name': 'carrot'})

# class EDGE_TYPE(str, Enum):
#     NEEDS = "NEEDS"
#     PROVIDES = "PROVIDES"
#     GOAL = "GOAL"
#     SUB_GOAL = "SUB_GOAL"
#     ACTION = "ACTION"
#     OBSERVED = "OBSERVE"
#     ACT_UPON = "ACT_UPON"


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
mine_joins = [{'index': 'items', 'filter': lambda x,y: 'pickaxe' in x.get('name'), 'type': EdgeType.NEEDS, 'join': 
    { 'index': 'blocks', 'filter': lambda x,y: x.get('material') == 'mineable/pickaxe', 'type': EdgeType.ACT_UPON } }]

actions_graph = nx.Graph()

actions_graph.add_node('mine', props = { 'name': 'mine', 
                                        'joins': mine_joins })
actions_graph.add_node('collect', props = { 'name': 'collect', 'joins': [{ 'index': 'items', 'filter': lambda x,y: x, 'type': EdgeType.OBSERVED } ] })
actions_graph.add_node('fight', props = { 'name':'fight', 'joins': [{'index': 'entities', 'filter': lambda x,y: x['type'] == 'Hostile mobs', 'type': EdgeType.OBSERVED } ] })
actions_graph.add_node('hunt', props = { 'name':'hunt', 'joins': [{ 'index': 'entities', 'filter': lambda x,y: x['type'] == 'Passive mobs','type': EdgeType.OBSERVED }] })
actions_graph.add_node('eat', props = { 'name':'eat', 'joins': [{ 'index': 'foods', 'filter': lambda x,y: x['food_points'] > 0, 'type': EdgeType.NEEDS }] })
actions_graph.add_node('craft', props = { 'name':'craft', 'joins': [{'index': 'recipes', 'filter': lambda x,y: x, 'type': EdgeType.ACT_UPON }] })
actions_graph.add_node('trade', props={ 'name': 'trade', 'joins': [{ 'index': 'trade', 'filter': lambda x,y: 'bid' in x['name'] or 'ask' in x['name'], 'type': EdgeType.ACT_UPON }] })

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

# todo state graph -> inventory, health, observations

# State -> State Graph  

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


money_joins = [{ 'index': 'items', 'filter': lambda x,y: x, 'type': EdgeType.PROVIDES }]
trade_graph = nx.Graph()
trade_graph.add_node('bid', props={ 'name': 'bid', 'joins': [{'index': 'trade', 'filter': lambda x,y: 'debit' == x['name'], 'type': EdgeType.ACT_UPON }]  }) # money -> debit -> all items
trade_graph.add_node('ask', props={ 'name': 'ask', 'joins': [{'index': 'trade', 'filter': lambda x,y: 'credit' == x['name'], 'type': EdgeType.ACT_UPON  }] }) # inventory items -> credit -> money
trade_graph.add_node('debit', props={'name': 'debit', 'joins': [{ 'index': 'trade', 'filter': lambda x,y: x['name'] == 'money', 'type': EdgeType.NEEDS } ] }) 
trade_graph.add_node('credit', props={'name': 'credit', 'joins': [{ 'index': 'inventory', 'filter': lambda x,y: x, 'type': EdgeType.NEEDS },
                                                                  { 'index': 'trade', 'filter': lambda x,y: 'money' == x['name'], 'type': EdgeType.PROVIDES  }] }) # could be , { 'index': 'trade', 'filter': lambda x,y: 'money' in x['name'] }
trade_graph.add_node('money', props={'name': 'money', 'joins': money_joins })

inventory_graph = nx.Graph()
#inventory_graph.add_node('wooden_pickaxe', props = { 'name': 'wooden_pickaxe', 'quantity': 1 })
observations_graph = nx.Graph()

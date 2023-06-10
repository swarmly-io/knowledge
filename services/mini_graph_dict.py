from services.mini_graphs import blocks_graph, items_graph, food_graph, actions_graph, agent_graph, inventory_graph, goals_graph, observations_graph, trade_graph, recipes_graph, entities_graph

graph_dict = {'blocks': blocks_graph,
              'items': items_graph,
              'foods': food_graph,
              'actions': actions_graph,
              'agent': agent_graph,
              'inventory': inventory_graph,
              'observations': observations_graph,
              'goals': goals_graph,
              'trade': trade_graph,
              'recipes': recipes_graph, 
              'entities': entities_graph}

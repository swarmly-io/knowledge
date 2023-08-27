

class NodeFeasibility:
    
    def __init__(self, graph, state: 'AgentState'):
        self.graph = graph
        self.state = state
        
    def evaluate_node(self, node):
        node_name, data = node
        index, name = node_name.split(':')        
        if index == 'recipes':
            needs = [i['needs'] for i in data['props']['items']]
            feasible = True
            for need_items in needs:
                for need in need_items:
                    id = need['id']
                    quantity = need['quantity']
                    feasible = self.state.check_inventory(id, quantity)
                if feasible:
                    return True
            return False
        # if item crafted by recipe (predecessor is recipe), lookup whether recipe feasible
        # if entity, look if it's observed
        # if hostile or huntable, calculate whether defeatable 
        # if collectable - see if near by?
        # if trade - see bidable, askable based on inventory and money
        
        # todo goals, agent, actions are all relative to down stream action nodes
        if index == 'goals':
            return True
        if index == 'agent':
            return True
        if index == 'actions':
            return True
        return None
        
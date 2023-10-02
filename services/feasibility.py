from enum import Enum
import networkx as nx

# todo this is all minecraft specific, needs to be extracted
class Feasibility(str, Enum):
    FEASIBLE = 'feasible'
    ATTAINED = 'attained'
    INFEASIBLE = 'infeasible'
    
    def compare(self, infeasible):
        if self in [Feasibility.ATTAINED, Feasibility.FEASIBLE] and not infeasible:
            return self
        return Feasibility.INFEASIBLE

class NodeFeasibility:

    def __init__(self, graph, state: 'AgentState'):
        self.graph = graph
        self.state = state

    def evaluate_node(self, node) -> Feasibility:
        node_name, data = node
        index, name = node_name.split(':')
        
        id = data.get('props', {}).get('id', None)
        if index in ['items', 'blocks'] and self.state.check_inventory(id):
            return Feasibility.ATTAINED
            
        if index == 'recipes':
            needs = [i['needs'] for i in data['props']['items']]
            feasible = True
            for need_items in needs:
                for need in need_items:
                    id = need['id']
                    quantity = need['quantity']
                    feasible = feasible and self.state.check_inventory(id, quantity)
                if feasible:
                    return Feasibility.FEASIBLE
            return Feasibility.INFEASIBLE
        if index == 'items':
            # held in inventory - a double check
            in_inventory = self.state.check_inventory(data['props']['id'])
            is_mineable = False
            blocks = list(filter(lambda x: 'blocks:' in x, self.graph.predecessors(node_name)))
            if blocks:
                for b in blocks:
                    block = self.graph.nodes[b]
                    tools = block['props']['requires']
                    if not tools:
                        is_mineable = True
                        break
                    for tool in tools:
                        item = self.graph.nodes[f"items:{tool.get('name')}"]
                        if not item:
                            break
                        got_tool = self.state.check_inventory(item['props'].get('id'))
                        if got_tool:
                            is_mineable = True
                            break

            recipes = list(filter(lambda x: 'recipes:' in x, self.graph.predecessors(node_name)))
            is_craftable = False
            for r in recipes:
                recipe = self.graph.nodes[r]
                creates_item = [r for r in recipe['props']
                                ['items'] if r['provides'].get('name') == name]
                if creates_item:
                    is_craftable = self.evaluate_node((r, self.graph.nodes[r])) in [Feasibility.FEASIBLE, Feasibility.ATTAINED]
                    if is_craftable:
                        break
                    
            is_droppable = not recipes and not blocks
            
            feasible = in_inventory or is_mineable or is_craftable or is_droppable
            return Feasibility.FEASIBLE if feasible else Feasibility.INFEASIBLE
        if index == 'blocks':
            is_breakable = False
            tools = data['props']['requires']
            diggable = data['props']['diggable']
            if not diggable:
                return Feasibility.INFEASIBLE
            if not tools:
                is_breakable = True
            else:
                for tool in tools:
                    item = self.graph.nodes[f"items:{tool.get('name')}"]
                    if not item:
                        break
                    got_tool = self.state.check_inventory(item['props'].get('id'))
                if got_tool:
                    is_breakable = True
            return Feasibility.FEASIBLE if is_breakable else Feasibility.INFEASIBLE

        # if entity, look if it's observed
        # if hostile or huntable, calculate whether defeatable
        # if collectable - see if near by?
        # if trade - see bidable, askable based on inventory and money

        # todo goals, agent, actions are all relative to down stream action nodes
        if index == 'goals':
            return Feasibility.FEASIBLE
        if index == 'agent':
            return Feasibility.FEASIBLE
        if index == 'actions':
            return Feasibility.FEASIBLE
        return None

from typing import List, Optional
import networkx as nx
from enum import Enum
from pydantic import BaseModel


class EdgeType(str, Enum):
    NEEDS = "NEEDS"
    PROVIDES = "PROVIDES"
    GOAL = "GOAL"
    SUB_GOAL = "SUB_GOAL"
    ACTION = "ACTION"
    OBSERVED = "OBSERVE"
    ACT_UPON = "ACT_UPON"

class GraphComposer:
    def __init__(self, graph_dict, linking_instructions, join_graphs, lenses):
        self.graph_dict = graph_dict
        self.linking_instructions = linking_instructions
        self.composed_graph = nx.DiGraph()
        for g in graph_dict:
            for n in graph_dict[g].nodes(data=True):
                self.composed_graph.add_node(g + ":" + n[0], **{ **n[1], 'source': g })
        self.join_graphs = join_graphs
        self.lenses = lenses

    def compose_graphs(self):
        for linking_instruction in self.linking_instructions:
            self._link_graphs(linking_instruction)
            
        for source_name, f_graph in self.join_graphs['sources']:
            self.one_to_many_joins(source_name, f_graph)

    def one_to_many_joins(self, source_name, f_graph):
        for n in f_graph.nodes(data=True):
            if not n[1]['props'].get('joins'):
                continue
                        
            joins = n[1]['props']['joins']
            for join in joins:
                index, filter_fn, sub_joins, graph = self.get_join_info(join)
                e_type = join['type']
                if not graph:
                    continue

                filtered_nodes = [node for node in graph.nodes(data=True) if filter_fn(node[1]['props'], n[1]['props'])]
                for nt in filtered_nodes:
                    new_source = source_name + ":" + n[0]
                    new_target = index + ":" + nt[0]
                    self.composed_graph.add_edge(new_source, new_target, **{ 'type': e_type, 'source': new_source })
                    
                    
                if sub_joins:
                    new_index, filter_fn, _, graph = self.get_join_info(sub_joins)
                    new_filtered_nodes = [node for node in graph.nodes(data=True) if filter_fn(node[1]['props'], n[1]['props'])]
                    for nt in filtered_nodes:
                        for nft in new_filtered_nodes:
                                e_type = join['type']
                                new_source = index + ":" + nt[0]
                                new_target = new_index + ":" + nft[0]
                                self.composed_graph.add_edge(new_source, new_target, **{ 'type': e_type, 'source': new_source })
                    

    def get_join_info(self, join):
        index = join['index']
        filter_fn = join['filter']
        sub_joins = join.get('join')
        graph = self.join_graphs['on'].get(index)
        return index,filter_fn,sub_joins,graph
                    
                    
    def _link_graphs(self, linking_instruction):
        target = linking_instruction['target']
        source = linking_instruction['source']
        link = linking_instruction['link']
        e_type = linking_instruction['type']

        target_graph = self.graph_dict[target]
        source_graph = self.graph_dict[source]
        
        for source_node in source_graph.nodes(data=True):
            target_nodes = filter(lambda x: x if link(source_node[1], x[1]) else None, target_graph.nodes(data=True))
            for target_node in target_nodes:
                new_source = source + ":" + source_node[0]
                new_target = target + ":" + target_node[0]
                source_data = { **source_node[1], 'source': source }
                target_data = { **target_node[1], 'source': target }
                self.composed_graph.add_node(new_source, **source_data)
                self.composed_graph.add_node(new_target, **target_data)
                
                self.composed_graph.add_edge(new_source, new_target, **{ 'type': e_type })
                
    def apply_lenses(self, lense_names: List[str], graph: Optional[nx.DiGraph]):
        # create a sub graph based on the lense
        G: nx.DiGraph = graph or self.composed_graph
        nodes = G.nodes(data=True)
        new_nodes = []
        for lense_name in lense_names:
            lense = self.lenses[lense_name]
            for n in nodes:
                if lense['source'](n):
                    if lense['condition'](n):
                        new_nodes.append(n)              
                else:
                    new_nodes.append(n)
        
        T = nx.DiGraph()
        for n in new_nodes:
            T.add_node(n[0], **n[1])
            
        filtered_edges = [(u, v, s) for (u, v, s) in G.edges(data=True) if u in T.nodes() and v in T.nodes()]
        T.add_edges_from(filtered_edges)
        return T
                
    def get_composed_graph(self):
        return self.composed_graph
    
class Node(BaseModel):
    name: str
    
    def to_node(self):
        return (self.name, self.__dict__)
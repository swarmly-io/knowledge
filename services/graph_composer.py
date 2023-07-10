from typing import List, Optional
import networkx as nx
from enum import Enum
from pydantic import BaseModel
from models.goals import GoalStatement, Tag

from services.models import TagLink

class EdgeType(str, Enum):
    NEEDS = "NEEDS"
    PROVIDES = "PROVIDES"
    GOAL = "GOAL"
    SUB_GOAL = "SUB_GOAL"
    ACTION = "ACTION"
    OBSERVED = "OBSERVE"
    ACT_UPON = "ACT_UPON"
    ACCRUE = "accrue"

MAX_JOIN_DEPTH = 50

class GraphComposer:
    def __init__(self, graph_dict, linking_instructions, join_graphs, lenses):
        self.graph_dict = graph_dict
        self.linking_instructions = linking_instructions
        self.composed_graph = nx.DiGraph()
        for g in graph_dict:
            for n in graph_dict[g].nodes(data=True):
                self.composed_graph.add_node(
                    g + ":" + n[0], **{**n[1], 'source': g})
        self.join_graphs = join_graphs
        self.lenses = lenses

    def compose_graphs(self):
        for linking_instruction in self.linking_instructions:
            self._link_graphs(linking_instruction)

        for source_name, f_graph in self.join_graphs['sources']:
            self.one_to_many_joins(source_name, f_graph)

    def one_to_many_joins(self, source_name, f_graph):
        nodes = [n for n in f_graph.nodes(data=True)]
        for n in nodes:
            if not n[1]['props'].get('joins'):
                continue

            joins = n[1]['props']['joins']
            for join in joins:
                print(join)
                self.create_join(join, source_name, n)

    def create_join(self, join, source_name, n, rec_count = 0):
        if rec_count > MAX_JOIN_DEPTH:
            raise Exception("Max join depth has been reacted, please simplify your joins")
            
        index, filter_fn, sub_joins, graph = self.get_join_info(join)
        e_type = join['type']
        if graph == None:
            raise Exception(f"A graph is missing to perform join {index} {sub_joins}")
        elif not graph:
            print(f"Empty join graph {index}")
            return
        else: 
            filtered_nodes = [
                        node for node in graph.nodes(
                            data=True) if filter_fn(node[1]['props'], n[1]['props'])]
            for nt in filtered_nodes:
                new_source = source_name + ":" + n[0]
                new_target = index + ":" + nt[0]
                self.add_edge(
                            new_source, new_target, **{'type': e_type, 'esource': new_source, 'etarget': index, 'source_name': join.get('source_name') or source_name })

                if sub_joins:
                    print('here', rec_count)
                    self.create_join(sub_joins, index, nt, rec_count=rec_count+1)


    def get_join_info(self, join):
        index = join['index']
        filter_fn = join['filter']
        sub_joins = join.get('join')
        graph = self.join_graphs['on'].get(index)
        return index, filter_fn, sub_joins, graph

    def _link_graphs(self, linking_instruction):
        target = linking_instruction['target']
        source = linking_instruction['source']
        link = linking_instruction['link']
        e_type = linking_instruction['type']

        target_graph = self.graph_dict[target]
        source_graph = self.graph_dict[source]

        for source_node in source_graph.nodes(data=True):
            target_nodes = filter(
                lambda x: x if link(
                    source_node[1],
                    x[1]) else None,
                target_graph.nodes(
                    data=True))
            for target_node in target_nodes:
                new_source = source + ":" + source_node[0]
                new_target = target + ":" + target_node[0]
                source_data = {**source_node[1], 'source': source}
                target_data = {**target_node[1], 'source': target}
                self.composed_graph.add_node(new_source, **source_data)
                self.composed_graph.add_node(new_target, **target_data)

                self.add_edge(
                    new_source, new_target, **{'type': e_type, 'esource': source, 'etarget': target })

    def apply_lenses(self,
                     lense_names: List[str],
                     graph: Optional[nx.DiGraph] = None):
        # create a sub graph based on the lense
        G: nx.DiGraph = graph or self.composed_graph
        nodes = G.nodes(data=True)
        remove_nodes = []
        for lense_name in lense_names:
            lense = self.lenses[lense_name]
            for n in nodes:
                if lense['source'](n):
                    if lense['condition'](n):
                        remove_nodes.append(n)

        T = nx.DiGraph()
        T.add_nodes_from(nodes)
        for n in remove_nodes:
            T.remove_node(n[0])

        filtered_edges = [
            (u, v, s) for (
                u, v, s) in G.edges(
                data=True) if u in T.nodes() and v in T.nodes()]
        T.add_edges_from(filtered_edges)
        return T
    
    def remove_goal_links(self, goals: List[GoalStatement]):
        for goal in goals:
            try:
                self.composed_graph.remove_edges_from(list(self.composed_graph.edges(f"goals:{goal.name}")))
            except:
                print(f"couldn't remove goal edge {goal.name}")
        print("Removed all goal edges")
    
    def link_goals_and_get_targets(self, goals: List[GoalStatement], focus_tags: List[Tag], tag_links: List[TagLink]):
        tag_link_dict = { t.tag: t for t in tag_links }
        targets = []
        for tag in focus_tags:
            for goal in goals:
                if goal.has_tag(tag):
                    link = tag_link_dict.get(tag.name)
                    if not link:
                        missing = [t.name for t in focus_tags if tag_link_dict.get(t.name) is None]
                        print("missing links", missing)
                        print(f"Error link wasn't found for: {tag.name}")
                        continue
                    
                    self.add_edge(f"goals:{goal.name}", f"actions:{link.action}")
                    targets.append((link.index, link.node))
        
        return targets

    def get_composed_graph(self):
        return self.composed_graph
    
    def add_edge(self, source, target, **attr):
        # if self.composed_graph.has_edge(source, target):
        #     old_edge = self.composed_graph[source][target]
        #     self.composed_graph.remove_edge(source, target)
        #     self.composed_graph.add_edge(source, old_edge['etarget'], **old_edge)
        #     self.composed_graph.add_edge(source, attr['etarget'], **attr)
        #     print('here', source, target)
        # else:
        self.composed_graph.add_edge(source, target, **attr)

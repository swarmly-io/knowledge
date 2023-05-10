
from collections.abc import Mapping
from copy import deepcopy
from typing import List
from more_itertools import flatten
from networkx import Graph
import networkx as nx


def first(l):
    return next((n for n in l), None)   

def merge(dict1, dict2):
    result = deepcopy(dict1)
    for key, value in dict2.items():
        if isinstance(value, Mapping):
            result[key] = merge(result.get(key, {}), value)
        else:
            result[key] = deepcopy(dict2[key])

    return result

def get_nested_value(d, selector):
    keys = selector.split('.')
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return None
    return d

def generate_selector_combinations(d, parent_key=None):
    combinations = {}
    for key, value in d.items():
        current_key = parent_key + '.' + key if parent_key else key
        if isinstance(value, dict):
            combinations.update({current_key: value})
            combinations.update(generate_selector_combinations(value, current_key))
        else:
            combinations[current_key] = value
    return combinations

def reverse_selector_combinations(combinations):
    d = {}
    for key, value in combinations.items():
        keys = key.split('.')
        current_dict = d
        for i, k in enumerate(keys):
            if i < len(keys) - 1:
                if k not in current_dict:
                    current_dict[k] = {}
                current_dict = current_dict[k]
            else:
                current_dict[k] = value
    return d

def update_nested_dict(d, obj):
    for key, value in obj.items():
        if isinstance(value, dict):
            d[key] = update_nested_dict(d.get(key, {}), value)
        else:
            d[key] = value
    return d

def rec_flatten(lst):
    if not any(isinstance(i, list) for i in lst):
        return lst
    results = []
    for l in lst:
        if isinstance(l, List):
            if not any(isinstance(i, list) for i in l):
                results = results + l
            else:
                results = results + list(flatten(l))
        else:
            results.append(l)
    return rec_flatten(results)

def to_network_x(graph: Graph, digraph = True):
    nxgraph = nx.DiGraph() if digraph else nx.Graph()
    for e in graph.edges:
        nxgraph.add_edge(e.source.name, e.target.name, weight=abs(e.target.cost), source_type=e.source.type, target_type=e.target.type, type = e.target.type)
    for n in graph.nodes:
        nxgraph.add_node(n.name, weight=n.cost, type=n.type, active=n.is_active)
    return nxgraph

if __name__ == "__main__":
    # a = {'x.y':1}
    # b = {'x': {'y':2, 'z':5} }   
    # b= merge(b, unflatten.unflatten(a))
    # assert b == {'x': {'y': 1, 'z': 5}}, b
    x = [[['sword'], ['axe'], ['pickaxe'], ['shovel'], ['hoe']], ['select_weapon'], 'x']
    print(list(rec_flatten(x)))

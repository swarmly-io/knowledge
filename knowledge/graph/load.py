from knowledge.elastic_client import ElasticConfig
import networkx as nx

def map_by_key(d, key):
    by_name = {}
    for item in d:
        by_name[item[key]] = item
    return by_name

def build_graph(esc, index_key):
    elements = map_by_key(esc.get_all(), index_key)
    graph = nx.DiGraph()

    for item in elements.items():
        graph.add_node(str(item[0]), props=item[1])
    
    return graph

def get_graph_dict(esc: ElasticConfig):
    return {
        'blocks': build_graph(esc.get_elastic_client('blocks'), 'name'), 
        'items': build_graph(esc.get_elastic_client('items'), 'name'), 
        'foods': build_graph(esc.get_elastic_client('foods'), 'name'),
        'entities': build_graph(esc.get_elastic_client('entities'), 'name'),
        'entity_loot': build_graph(esc.get_elastic_client('entitylood'), 'id'),
        'smelting': build_graph(esc.get_elastic_client('smelting'), 'id'),
        'recipes': build_graph(esc.get_elastic_client('recipe'), 'id')
    }
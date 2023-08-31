from knowledge.elastic_client import ElasticConfig
import networkx as nx


def map_by_key(d, key):
    by_name = {}
    for item in d:
        by_name[item[key]] = item
    return by_name


def build_graph(elements):
    graph = nx.DiGraph()

    for item in elements.items():
        graph.add_node(str(item[0]), props=item[1])

    return graph

# todo graph dict needs to be dynamic to handle integrations of services
# like trading


def get_graph_dict(esc: ElasticConfig):
    def elements(name, index_key): return map_by_key(
        esc.get_elastic_client(name).get_all(), index_key)

    indexes = {
        # static minecraft related
        'blocks': elements('blocks', 'name'),
        'items': elements('items', 'name'),
        'foods': elements('foods', 'name'),
        'entities': elements('entities', 'name'),
        'entityloot': elements('entityloot', 'id'),
        'smelting': elements('smelting', 'id'),
        'recipes': elements('recipes', 'id'),
        'hostiles': elements('hostiles', 'id'),
        # dynamic, agent specific
        'agent': nx.DiGraph(),
        'goals': nx.DiGraph(),
        'actions': nx.DiGraph(),
        'trade': nx.DiGraph(),
        'inventory': nx.DiGraph(),
        'observations': nx.DiGraph(),
    }

    graph_dict = {
        # static minecraft related
        'blocks': build_graph(indexes['blocks']),
        'items': build_graph(indexes['items']),
        'foods': build_graph(indexes['foods']),
        'entities': build_graph(indexes['entities']),
        'entityloot': build_graph(indexes['entityloot']),
        'smelting': build_graph(indexes['smelting']),
        'recipes': build_graph(indexes['recipes']),
        'hostiles': build_graph(indexes['hostiles']),
        # dynamic, agent specific
        'agent': nx.DiGraph(),
        'goals': nx.DiGraph(),
        'actions': nx.DiGraph(),
        'trade': nx.DiGraph(),
        'inventory': nx.DiGraph(),
        'observations': nx.DiGraph(),
    }
    return graph_dict, indexes

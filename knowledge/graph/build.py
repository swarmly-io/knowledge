
from knowledge.elastic_client import ElasticConfig
import networkx as nx

from knowledge.minecraft.models.normalised_models import Block

def build_block_graph(es_config: ElasticConfig):
    blocks = es_config.get_elastic_client("blocks").get_all()
    graphs = {}
    for block in blocks:
        block = Block(**block)
        G=nx.Graph()
        G.add_node(block.name)
        for d in block.drops:
            G.add_node(d.name)
            G.add_edge(block.name, d.name)
            
        for r in block.requires:
            G.add_node(r.name)
            G.add_edge(block.name, r.name, material = block.material)
            
        graph_dict = nx.node_link_data(G)
        graphs[block.name] = graph_dict
        
    print(graphs)

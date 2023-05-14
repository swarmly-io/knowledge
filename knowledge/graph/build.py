
from typing import Dict

from knowledge.elastic_client import ElasticConfig
import networkx as nx
from knowledge.graph.models import StoredBlockGraph

from knowledge.minecraft.models.normalised_models import Block

def build_block_graph(es_config: ElasticConfig):
    blocks = es_config.get_elastic_client("blocks").get_all()
    graphs = []
    for block in blocks:
        block = Block(**block)
        G=nx.DiGraph()
        G.add_node(block.name)
        
        for d in block.drops:
            G.add_node(d.name)
            G.add_edge(block.name, d.name)
            
        for r in block.requires:
            G.add_node(r.name)
            G.add_edge(r.name, block.name, material = block.material)
            
        graph_dict = nx.node_link_data(G)
        graphs.append(StoredBlockGraph(id = block.id, name = block.name, graph = graph_dict))
       
    esg = es_config.get_elastic_client("blocks_graph")
    esg.bulk_load(graphs)
        
def reload_graph(graph: Dict):
    return nx.node_link_data(graph)


from config import elastic_config
from knowledge.graph.load import get_graph_dict

graph_dict, indexes = get_graph_dict(elastic_config)

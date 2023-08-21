
from config import elastic_config
from knowledge.graph.load import get_graph_dict


graph_dict = get_graph_dict(elastic_config)
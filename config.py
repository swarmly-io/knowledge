import os
from dotenv import load_dotenv
from integrations.elastic import ElasticConfig
import argparse


class Args:
    dev_mini_graph = False
    local = True


args = Args()


def parse_args():
    parser = argparse.ArgumentParser(prog='Knowledge app')
    parser.add_argument('-d', '--dev_mini_graph', default=False)
    parser.add_argument('-l', '--local', default=True)
    args = parser.parse_args()
    return args


mini_graph = True
if not args.dev_mini_graph:
    mini_graph = False

current_env = 'remote' if not args.local and os.path.exists('.env') else 'local'

if current_env == 'local':
    dotenv_path = '.env.local'
else:
    dotenv_path = '.env'

load_dotenv(dotenv_path)

elastic_config = ElasticConfig(
    https=current_env != 'local',
    username=os.getenv('ELASTIC_USERNAME'),
    password=os.getenv('ELASTIC_PASSWORD'),
    url=os.getenv('ELASTIC_URL'),
    port=os.getenv('ELASTIC_PORT'))

print("Done loading client", current_env, mini_graph)

def get_index_data():
    from minecraft_graph.loader import get_graph_dict
    graph_dict, indexes = get_graph_dict(elastic_config)
    return graph_dict, indexes

import os
from dotenv import load_dotenv
from knowledge.elastic_client import ElasticConfig
from knowledge.graph.load import get_graph_dict
from knowledge.minecraft.build import create_minecraft_indexes

current_env = 'remote' if os.path.exists('.env') else 'local'

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

create_minecraft_indexes(elastic_config)
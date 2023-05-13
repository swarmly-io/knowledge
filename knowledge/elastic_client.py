from typing import List
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch.helpers import bulk


class ElasticClient:
    def __init__(self, url, index: str):
        self.index = index
        self.es = Elasticsearch([url])

        if not self.es.indices.exists(index=self.index):
            self.es.indices.create(index=self.index)

    def put(self, model: BaseModel):
        doc_id = model.id
        self.es.index(index=self.index, id=doc_id, body=model.dict())

    def bulk_load(self, models: List[BaseModel]):
        actions = [{"_index": self.index, "_id": model.id,
                    "_source": model.dict()} for model in models]
        success, _ = bulk(client=self.es, actions=actions)
        return success

    def get(self, doc_id: str):
        result = self.es.get(index=self.index, id=doc_id)
        return result['_source']

    def search_all(self, query: str = None):
        s = Search(using=self.es, index=self.index)

        if query:
            q = Q("multi_match", query=query, fields=['*'])
            s = s.query(q)

        response = s.execute()
        return [hit.to_dict() for hit in response]


class ElasticConfig:

    def __init__(
            self,
            https=False,
            username="elastic",
            password="changeme",
            url="localhost",
            port="9200") -> None:
        self.connection_string = self.get_connection_string(
            https, username, password, url, port)

    def get_connection_string(self, https, username, password, url, port):
        prefix = "http://" if not https else "https://"
        return prefix + username + ":" + password + "@" + url + ":" + port

    def get_elastic_client(self, index_name):
        return ElasticClient(self.connection_string, index_name)

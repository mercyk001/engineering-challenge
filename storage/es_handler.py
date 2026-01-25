

from typing import Dict, Any, Optional
try:
    from elasticsearch import Elasticsearch
except Exception:  # pragma: no cover
    Elasticsearch = None  # type: ignore

class ElasticsearchHandler:
    def __init__(self, hosts=None):
        if Elasticsearch is None:
            raise RuntimeError("elasticsearch library not installed")
        self.client = Elasticsearch(hosts or ["http://localhost:9200"])

    def index_document(self, index: str, doc_id: str, body: Dict[str, Any]):
        return self.client.index(index=index, id=doc_id, document=body)

    def create_index(self, index: str, mapping: Dict[str, Any]):
        if not self.client.indices.exists(index=index):
            return self.client.indices.create(index=index, body=mapping)
        return None
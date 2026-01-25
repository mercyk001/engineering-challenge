from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any
from elasticsearch import Elasticsearch, helpers

@dataclass
class ElasticIndexer:
    es_url: str
    index_name: str = "kenyalaw_docs"

    def __post_init__(self) -> None:
        self.es = Elasticsearch(self.es_url)

    def ensure_index(self) -> None:
        if self.es.indices.exists(index=self.index_name):
            return
        self.es.indices.create(
            index=self.index_name,
            mappings={
                "properties": {
                    "doc_id": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "url": {"type": "keyword"},
                    "raw_text": {"type": "text"},
                    "parties": {"type": "keyword"},
                    "metadata": {"type": "object", "enabled": True},
                    "pdf_path": {"type": "keyword"},
                    "pdf_url": {"type": "keyword"},
                    "docx_url": {"type": "keyword"},
                    "fetched_at": {"type": "date"},
                    "checksum": {"type": "keyword"},
                }
            },
        )

    def bulk_upsert(self, records: Iterable[Dict[str, Any]]) -> None:
        actions = []
        for r in records:
            actions.append({
                "_op_type": "index",
                "_index": self.index_name,
                "_id": r["doc_id"],
                "_source": r,
            })
        helpers.bulk(self.es, actions, request_timeout=120)

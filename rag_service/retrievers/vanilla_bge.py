from __future__ import annotations

import time

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class QdrantBGERetriever:
    def __init__(
        self,
        collection_name: str,
        model_name: str = "BAAI/bge-small-en-v1.5",
        url: str = "http://qdrant:6333",
    ) -> None:
        self.client = QdrantClient(url=url)
        self.model = SentenceTransformer(model_name)
        self.collection_name = collection_name
        self.label = f"Vanilla-{model_name.split('/')[-1]}-K5"

    def _search_qdrant(self, query_vector: list[float], limit: int):
        if hasattr(self.client, "search"):
            try:
                return self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    with_payload=True,
                )
            except TypeError:
                pass

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )
        return getattr(response, "points", response)

    def search(self, query: str, limit: int = 5):
        start_time = time.perf_counter()
        query_vector = self.model.encode(query).tolist()
        results = self._search_qdrant(query_vector, limit)
        latency_ms = (time.perf_counter() - start_time) * 1000
        contexts = [
            {
                "text": result.payload["text"],
                "source_ref": result.payload.get("source_ref", ""),
                "score": float(result.score) if result.score is not None else None,
            }
            for result in results
        ]
        return contexts, latency_ms

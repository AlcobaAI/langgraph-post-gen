from __future__ import annotations

import time

from qdrant_client import QdrantClient
from sentence_transformers import CrossEncoder, SentenceTransformer


class RerankedBGERetriever:
    def __init__(
        self,
        collection_name: str,
        bi_encoder_name: str = "BAAI/bge-small-en-v1.5",
        reranker_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        url: str = "http://qdrant:6333",
    ) -> None:
        self.client = QdrantClient(url=url)
        self.bi_encoder = SentenceTransformer(bi_encoder_name)
        self.reranker = CrossEncoder(reranker_name)
        self.collection_name = collection_name
        self.label = f"Reranked-{bi_encoder_name.split('/')[-1]}-MiniLM-K5"

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

    def search(self, query: str, limit: int = 15):
        start_time = time.perf_counter()

        query_vector = self.bi_encoder.encode(query).tolist()
        initial_results = self._search_qdrant(query_vector, limit)

        passages = [result.payload["text"] for result in initial_results]
        if not passages:
            return [], (time.perf_counter() - start_time) * 1000

        ranks = self.reranker.rank(query, passages)
        top_indices = [rank["corpus_id"] for rank in ranks[:5]]
        contexts = [
            {
                "text": initial_results[index].payload["text"],
                "source_ref": initial_results[index].payload.get("source_ref", ""),
                "score": float(ranks[position]["score"]),
            }
            for position, index in enumerate(top_indices)
        ]

        latency_ms = (time.perf_counter() - start_time) * 1000
        return contexts, latency_ms

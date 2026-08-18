from __future__ import annotations

import json
import time

import Stemmer
import bm25s
from sentence_transformers import CrossEncoder


def _to_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "text" in value and isinstance(value["text"], str):
            return value["text"]
        if "content" in value and isinstance(value["content"], str):
            return value["content"]
        return json.dumps(value, ensure_ascii=True)
    if isinstance(value, list):
        return "\n".join(_to_text(item) for item in value)
    return str(value)


class HybridBM25RerankRetriever:
    def __init__(
        self,
        collection_name: str,
        index_dir: str = "indices",
        reranker_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ) -> None:
        self.path = f"{index_dir}/bm25_{collection_name}"
        self.label = "Hybrid-BM25-MiniLM-Rerank-K5"
        self.stemmer = Stemmer.Stemmer("english")
        self.retriever = bm25s.BM25.load(self.path, load_corpus=True)
        self.reranker = CrossEncoder(reranker_name)

    def search(self, query: str, limit: int = 5):
        start_time = time.perf_counter()

        query_tokens = bm25s.tokenize(query, stemmer=self.stemmer)
        results, _ = self.retriever.retrieve(query_tokens, k=20)
        passages = results[0].tolist() if results.shape[0] > 0 else []

        normalized = []
        for passage in passages:
            if isinstance(passage, dict):
                normalized.append(
                    {
                        "text": _to_text(passage),
                        "source_ref": passage.get("source_ref", ""),
                    }
                )
            else:
                normalized.append({"text": _to_text(passage), "source_ref": ""})

        if not normalized:
            return [], (time.perf_counter() - start_time) * 1000

        ranks = self.reranker.rank(query, [item["text"] for item in normalized])
        top_indices = [rank["corpus_id"] for rank in ranks[:limit]]
        contexts = [
            {
                "text": normalized[index]["text"],
                "source_ref": normalized[index]["source_ref"],
                "score": ranks[position]["score"],
            }
            for position, index in enumerate(top_indices)
        ]

        latency_ms = (time.perf_counter() - start_time) * 1000
        return contexts, latency_ms

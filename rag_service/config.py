from __future__ import annotations

import os
from dataclasses import dataclass


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


@dataclass(frozen=True)
class RagSettings:
    retriever: str
    collection_name: str
    qdrant_url: str
    documents_dir: str
    index_dir: str
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    reranker_model: str


settings = RagSettings(
    retriever=os.getenv("RAG_RETRIEVER", "vanilla_bge"),
    collection_name=os.getenv("RAG_COLLECTION_NAME", "demo_documents"),
    qdrant_url=os.getenv("RAG_QDRANT_URL", "http://qdrant:6333"),
    documents_dir=os.getenv("RAG_DOCUMENTS_DIR", "/app/documents"),
    index_dir=os.getenv("RAG_INDEX_DIR", "/app/indices"),
    chunk_size=_get_int("RAG_CHUNK_SIZE", 1200),
    chunk_overlap=_get_int("RAG_CHUNK_OVERLAP", 200),
    embedding_model=os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
    reranker_model=os.getenv(
        "RAG_RERANKER_MODEL",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ),
)

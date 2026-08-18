from __future__ import annotations

from rag_service.config import settings
from rag_service.retrievers.hybrid_bm25_rerank import HybridBM25RerankRetriever
from rag_service.retrievers.noop import NoOpRetriever
from rag_service.retrievers.reranked_bge import RerankedBGERetriever
from rag_service.retrievers.vanilla_bge import QdrantBGERetriever


def build_retriever(has_documents: bool = True):
    if not has_documents:
        return NoOpRetriever(label=f"Empty-{settings.retriever}")

    if settings.retriever == "vanilla_bge":
        return QdrantBGERetriever(
            collection_name=settings.collection_name,
            model_name=settings.embedding_model,
            url=settings.qdrant_url,
        )

    if settings.retriever == "reranked_bge":
        return RerankedBGERetriever(
            collection_name=settings.collection_name,
            bi_encoder_name=settings.embedding_model,
            reranker_name=settings.reranker_model,
            url=settings.qdrant_url,
        )

    if settings.retriever == "hybrid_bm25_rerank":
        return HybridBM25RerankRetriever(
            collection_name=settings.collection_name,
            index_dir=settings.index_dir,
            reranker_name=settings.reranker_model,
        )

    raise ValueError(f"Unsupported retriever: {settings.retriever}")

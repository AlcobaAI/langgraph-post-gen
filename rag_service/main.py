from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from rag_service.config import settings
from rag_service.document_store import load_documents
from rag_service.factory import build_retriever
from rag_service.indexing import build_bm25_index, build_qdrant_index
from rag_service.schemas import SearchRequest, SearchResponse, SearchResult


@asynccontextmanager
async def lifespan(app: FastAPI):
    documents = load_documents(
        settings.documents_dir,
        settings.chunk_size,
        settings.chunk_overlap,
    )
    app.state.documents = documents

    if documents:
        embedding_model = SentenceTransformer(settings.embedding_model)
        qdrant_client = QdrantClient(url=settings.qdrant_url)
        build_qdrant_index(
            client=qdrant_client,
            collection_name=settings.collection_name,
            model=embedding_model,
            documents=documents,
        )
        build_bm25_index(
            collection_name=settings.collection_name,
            index_dir=settings.index_dir,
            documents=documents,
        )

    app.state.retriever = build_retriever(has_documents=bool(documents))
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "retriever": settings.retriever,
        "documents_loaded": len(getattr(app.state, "documents", [])),
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    try:
        results, latency_ms = app.state.retriever.search(request.query, request.limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return SearchResponse(
        retriever=settings.retriever,
        collection_name=settings.collection_name,
        results=[
            SearchResult(
                text=result["text"],
                source_ref=result.get("source_ref", ""),
                score=result.get("score"),
            )
            for result in results
        ],
        latency_ms=float(latency_ms),
    )

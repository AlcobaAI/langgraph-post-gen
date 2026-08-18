from __future__ import annotations

from pathlib import Path

import bm25s
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer


def build_qdrant_index(
    *,
    client: QdrantClient,
    collection_name: str,
    model: SentenceTransformer,
    documents: list[dict],
) -> None:
    vector_size = model.get_sentence_embedding_dimension()

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    points = []
    for index, document in enumerate(documents):
        vector = model.encode(document["text"]).tolist()
        points.append(
            PointStruct(
                id=index,
                vector=vector,
                payload={
                    "text": document["text"],
                    "source_ref": document["source_ref"],
                },
            )
        )

    if points:
        client.upsert(collection_name=collection_name, points=points)


def build_bm25_index(
    *,
    collection_name: str,
    index_dir: str,
    documents: list[dict],
) -> str:
    Path(index_dir).mkdir(parents=True, exist_ok=True)
    path = f"{index_dir}/bm25_{collection_name}"

    corpus = [
        {
            "text": document["text"],
            "source_ref": document["source_ref"],
        }
        for document in documents
    ]
    retriever = bm25s.BM25(corpus=corpus)
    retriever.index(bm25s.tokenize([document["text"] for document in documents]))
    retriever.save(path)
    return path

Place source documents for the RAG service in this folder.

Supported text-like inputs currently include:
- `.txt`
- `.md`
- `.json`
- `.pdf`

The RAG service ingests these files on startup and exposes three retriever modes:
- `vanilla_bge`
- `reranked_bge`
- `hybrid_bm25_rerank`

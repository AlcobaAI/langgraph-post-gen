from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    tenant_id: str = ""
    project_id: str = ""
    limit: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    text: str
    source_ref: str
    score: float | None = None


class SearchResponse(BaseModel):
    retriever: str
    collection_name: str
    results: List[SearchResult]
    latency_ms: float

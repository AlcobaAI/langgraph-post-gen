from __future__ import annotations

import json
import os
from urllib import error, request

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.schemas.rag import RagSearchRequest, RagSearchResponse


class RAGInput(BaseModel):
    query: str = Field(description="Query for knowledge base")
    tenant_id: str = Field(default="", description="Tenant identifier")
    project_id: str = Field(default="", description="Project identifier")
    limit: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")


def _search_rag_service(payload: RagSearchRequest) -> RagSearchResponse:
    base_url = os.getenv("RAG_SERVICE_URL", "http://localhost:8100").rstrip("/")
    body = json.dumps(payload.model_dump()).encode("utf-8")
    req = request.Request(
        url=f"{base_url}/search",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=10.0) as response:
            raw = response.read().decode("utf-8")
    except error.URLError as exc:
        raise RuntimeError(f"RAG service request failed: {exc}") from exc

    return RagSearchResponse.model_validate_json(raw)


def search_rag(query: str, tenant_id: str = "", project_id: str = "", limit: int = 5) -> RagSearchResponse:
    return _search_rag_service(
        RagSearchRequest(
            query=query,
            tenant_id=tenant_id,
            project_id=project_id,
            limit=limit,
        ),
    )


@tool("invoke_rag_search", args_schema=RAGInput)
def invoke_rag_search(query: str, tenant_id: str = "", project_id: str = "", limit: int = 5):
    """Searches the external RAG service for grounding context."""
    response = search_rag(query=query, tenant_id=tenant_id, project_id=project_id, limit=limit)
    return response.model_dump()

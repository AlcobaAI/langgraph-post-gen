from __future__ import annotations

import json
import os
import sys
from urllib import request


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _read_json(url: str, method: str = "GET", payload: dict | None = None) -> dict:
    body = None
    headers = {}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url=url, data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=15.0) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    base_url = _get_env("RAG_TEST_BASE_URL", "http://localhost:8100").rstrip("/")
    query = _get_env("RAG_TEST_QUERY", "What information is available in the indexed documents?")
    tenant_id = _get_env("RAG_TEST_TENANT_ID", "test-tenant")
    project_id = _get_env("RAG_TEST_PROJECT_ID", "test-project")
    limit = int(_get_env("RAG_TEST_LIMIT", "5"))

    health = _read_json(f"{base_url}/health")
    print("Health:", json.dumps(health, indent=2))

    search_payload = {
        "query": query,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "limit": limit,
    }
    result = _read_json(f"{base_url}/search", method="POST", payload=search_payload)
    print("Search:", json.dumps(result, indent=2))

    if "results" not in result:
        print("Search response is missing 'results'.", file=sys.stderr)
        return 1

    if not isinstance(result["results"], list):
        print("Search response 'results' is not a list.", file=sys.stderr)
        return 1

    print(f"Retrieval smoke test passed with {len(result['results'])} result(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

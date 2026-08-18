This folder contains simple retrieval smoke tests for the standalone RAG service.

Run the stack first:

```powershell
docker compose up --build
```

Then run the retrieval smoke test from the project root:

```powershell
docker compose exec rag-service python -m rag_service.tests.test_retrieval
```

Optional environment variables:
- `RAG_TEST_BASE_URL`
- `RAG_TEST_QUERY`
- `RAG_TEST_TENANT_ID`
- `RAG_TEST_PROJECT_ID`
- `RAG_TEST_LIMIT`

The test checks:
- the RAG service health endpoint responds
- the search endpoint returns a valid retrieval payload

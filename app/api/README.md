# API Layer Details

This folder contains the HTTP-facing layer of the service.

Its purpose is to expose application capabilities over FastAPI while keeping route handlers thin.

## Current Structure

```text
api/
  routes/
    generate.py
```

## Responsibilities

The API layer is responsible for:

- defining endpoints
- validating request payloads
- validating response payloads
- accessing shared application services through `app.state`
- translating application errors into HTTP responses

It is not responsible for:

- direct model orchestration
- prompt construction
- business workflow design
- artifact formatting

Those concerns live in the service, graph, prompt, and builder layers.

## Current Endpoint

### `POST /generate`

This endpoint accepts an `AiGenerateInput` payload and returns an `AiGenerateOutput` payload.

At a high level it:

1. reads the shared `GenerateContentService` from FastAPI application state
2. passes the validated request model into the service
3. returns the service result
4. maps runtime readiness failures to HTTP `503`

## Why The Route Layer Is Thin

Keeping route handlers thin makes it easier to:

- add additional endpoints
- keep API behavior easy to test
- change workflow logic without rewriting the transport layer
- reuse the same service objects across multiple routes

High-level examples of adjacent endpoints that could follow the same pattern:

- `POST /review`
- `POST /rewrite`
- `POST /generate-grounded`

Each of those could have:

- its own request/response schema
- its own service class
- its own workflow graph

while still fitting into the same FastAPI application layout.

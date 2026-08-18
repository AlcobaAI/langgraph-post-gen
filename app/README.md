# Application Architecture

This folder contains the core application layers that make up the current service.

At a high level, the repository separates:

- HTTP transport
- application service orchestration
- workflow definition
- domain contracts
- concrete model-backed implementations
- prompt composition
- typed schemas
- artifact assembly

That separation keeps the current content-generation flow understandable while also making it possible to add other service flows with the same overall structure.

## High-Level Flow

The current request flow is:

```text
HTTP request
  -> API route
  -> GenerateContentService
  -> LangGraph workflow
  -> planner
  -> writer
  -> judge
  -> editor
  -> artifact assembly
  -> HTTP response
```

For multi-angle requests, the graph fans out one branch per angle. For editor adaptation, the workflow now fans out across explicit editor targets, where each target contains a platform plus the persona instructions that should shape the final output.

## Main Modules

### `main.py`

FastAPI entrypoint.

Responsibilities:

- create the app
- initialize the service
- run startup behavior
- register routes

### `api/`

HTTP layer.

Responsibilities:

- define routes
- validate requests and responses
- translate failures into HTTP errors

More detail: [API layer details](api/README.md)

### `services/`

Application service layer.

Responsibilities:

- normalize request inputs
- prepare initial workflow state
- compile and hold shared runtime resources
- invoke the workflow
- shape the returned response

This is also where request-level platform/persona routing is normalized into editor targets before the graph runs.

This is where application-level orchestration belongs, rather than inside route handlers or model-specific classes.

### `graph.py`

Workflow orchestration layer built with LangGraph.

Responsibilities:

- define nodes
- define state transitions
- fan out work across angles
- fan out editor work across explicit platform/persona targets
- aggregate final posts

Conceptually:

```text
Request state
  -> planner
  -> one branch per angle
  -> writer -> judge -> one editor run per editor target
  -> collected artifacts
```

### `domain/protocols/`

Behavior contracts for core workflow components.

Responsibilities:

- define planner interface
- define writer interface
- define judge interface
- define editor interface

This allows the workflow to depend on abstract behavior instead of one concrete implementation.

### `infrastructure/agents/`

Concrete OpenAI-backed agent implementations.

Responsibilities:

- call the configured models
- enforce structured outputs
- implement the planner, writer, judge, and editor behaviors

More detail: [Agent layer details](infrastructure/agents/README.md)

### `prompts/`

Prompt-building layer.

Responsibilities:

- shared system context
- agent-specific instructions
- platform-specific tone and output guidance
- persona-specific voice guidance

More detail: [Prompt and platform behavior](prompts/README.md)

### `schemas/`

Typed data-contract layer.

Responsibilities:

- API request and response models
- workflow input and output models
- structured LLM output models
- artifact models

This keeps each stage explicit and reduces reliance on unstructured dictionaries.

### `post_builders.py`

Artifact assembly helpers.

Responsibilities:

- build completed artifacts
- build skipped artifacts
- attach consistent metadata

### `config.py`

Configuration layer.

Responsibilities:

- load `.env`
- expose per-stage model and temperature settings

## How The Structure Supports Additional Services

The current content generator is one workflow built on a broader service pattern.

Other services could follow the same shape:

- define new API schemas
- add a new route
- add a new service class
- define a new graph or reuse parts of the existing one
- implement or reuse protocols, prompts, and builders

High-level examples:

- content review
- content rewriting
- retrieval-grounded generation
- campaign brief expansion
- copy transformation

Because the transport, service, workflow, prompts, and agent implementations are already separated, those additions can be introduced without turning the codebase into one large intertwined module.

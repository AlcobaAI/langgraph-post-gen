
# langgraph-post-generator

A modular AI content-generation backend built with FastAPI, LangGraph, OpenAI, and a Dockerized RAG sidecar.

Takes a prompt, generates multiple content angles, writes drafts for each, judges quality, and adapts them for different platforms (LinkedIn, Instagram, X, etc.). All with optional document grounding via RAG.

---

## Quick Start (5 minutes)

```bash
# Clone
git clone https://github.com/yourusername/langgraph-post-generator.git
cd langgraph-post-generator

# Setup
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Run
docker compose up --build -d

# Test (wait 15 seconds for startup)
sleep 15
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "artifactId": "test-001",
    "tenantId": "demo",
    "userId": "user-123",
    "userPrompt": "Generate a LinkedIn post about effective team collaboration.",
    "platforms": ["linkedin"],
    "angleCount": 1
  }' > output.json

cat output.json
```

Done! Your API is running and generated content.

---

## What It Does

1. **Planner** — Creates distinct content angles from your prompt
2. **Writer** — Writes a source draft for each angle
3. **Judge** — Evaluates if the draft is relevant
4. **Editor** — Adapts approved drafts for each target platform

All grounded in your documents (optional RAG).

---

## How to Use

### Interactive API Docs

Open `http://localhost:8000/docs` and try the `/generate` endpoint.

### API Request Format

```json
{
  "artifactId": "unique-id-123",
  "tenantId": "your-org",
  "userId": "user-456",
  "userPrompt": "Your content request here",
  "platforms": ["linkedin", "instagram", "x"],
  "angleCount": 2,
  "persona": "professional"
}
```

**Required fields:**
- `artifactId` — unique ID for this request
- `tenantId` — your organization/tenant name
- `userId` — user making the request
- `userPrompt` — what content to create

**Optional fields:**
- `platforms` — target platforms (default: `["linkedin"]`)
- `angleCount` — how many angles to generate (default: `1`)
- `persona` — voice/tone (e.g., `professional`, `casual`, `educational`)
- `platformPersonaPairs` — different personas per platform
- `projectId` — campaign/project name (default: `"default"`)

### Supported Platforms

`linkedin` • `instagram` • `facebook` • `x` • `tiktok` • `blog` • `newsletter` • `speech` • `copy`

### Request Examples

**Simple single post:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "artifactId": "post-001",
    "tenantId": "demo",
    "userId": "user-123",
    "userPrompt": "Write about AI in business."
  }'
```

**Multiple angles & platforms:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "artifactId": "campaign-001",
    "tenantId": "demo",
    "userId": "user-123",
    "userPrompt": "Create content about remote work.",
    "platforms": ["linkedin", "instagram", "x"],
    "angleCount": 2
  }'
```

**Different personas per platform:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "artifactId": "personas-001",
    "tenantId": "demo",
    "userId": "user-123",
    "userPrompt": "Content about team collaboration.",
    "platformPersonaPairs": [
      {"platform": "linkedin", "persona": "professional"},
      {"platform": "instagram", "persona": "casual"},
      {"platform": "x", "persona": "sharp"}
    ],
    "angleCount": 1
  }'
```

---

## Response Format

```json
{
  "result": "Success",
  "generationId": "uuid-here",
  "durationMs": 2150.25,
  "artifacts": [
    {
      "angle": "Strategic angle for this content",
      "content": "# Final Platform-Ready Content\n\nMarkdown formatted...",
      "graphics_prompt": "Prompt for image generation (DALL-E, etc.)",
      "video_script": "Script for video content",
      "status": "completed",
      "metadata": {
        "platform": "linkedin",
        "judge": {
          "is_relevant": true,
          "reasoning": "..."
        },
        "retrieval": {
          "writer": {
            "retrieved_docs": []
          }
        }
      }
    }
  ]
}
```

Each artifact is ready to post on its platform.

---

## Prerequisites

- Docker & Docker Compose
- OpenAI API key
- (Optional) Python 3.12+ if running locally without Docker

---

## Setup

### 1. Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

Optional: Customize models per stage:
```env
PLANNER_MODEL=gpt-4o
WRITER_MODEL=gpt-4o
JUDGE_MODEL=gpt-4o-mini
EDITOR_MODEL=gpt-4o
```

### 2. Start Services

```bash
docker compose up --build -d
```

Starts three services:
- `app` → `http://localhost:8000`
- `rag-service` → `http://localhost:8100`
- `qdrant` → `http://localhost:6333`

### 3. Verify

```bash
# Check API is running
curl http://localhost:8000/docs

# Check RAG is healthy
curl http://localhost:8100/health
```

---

## Adding Documents (Optional)

Place `.txt`, `.md`, `.json`, or `.pdf` files in `documents/`:

```bash
cp your-document.txt documents/
docker compose restart rag-service
```

The system will ground content generation in these documents via RAG.

---

## Running Workflow Tests

The repo includes tests for different scenarios:

**Single persona across multiple platforms & angles:**
```bash
docker compose exec app python workflow_tests/run_workflow_tests.py
```

Runs 6 scenarios:
- 1 angle × 1 platform
- 1 angle × 3 platforms
- 3 angles × 1 platform
- 3 angles × 3 platforms
- 3 angles × all 9 platforms
- 10 angles × all 9 platforms

Results saved to `workflow_tests/outputs/single_persona/{timestamp}/`

**Multi-persona scenarios:**
```bash
docker compose exec app python workflow_tests/run_workflow_tests_multi_persona.py
```

Tests 7 personas:
- `sharp_operator` — direct, action-oriented
- `practical_strategist` — business-focused
- `clear_educator` — educational, explanatory
- `calm_expert` — measured, authoritative
- `bold_creator` — confident, energetic
- `warm_guide` — empathetic, supportive
- Platform-persona pairs (different voice per platform)

Results saved to `workflow_tests/outputs/multi_persona/{timestamp}/`

---

## Common Commands

### View logs

```bash
docker compose logs -f app
docker compose logs -f rag-service
```

### Stop all services

```bash
docker compose down
```

### Restart a service

```bash
docker compose restart app
docker compose restart rag-service
```

### Test RAG directly

```bash
docker compose exec rag-service python -m rag_service.tests.test_retrieval
```

---

## Development

### Code Structure

```
app/
  ├── main.py              # FastAPI entry point
  ├── config.py            # Model settings from .env
  ├── graph.py             # LangGraph workflow definition
  ├── api/                 # HTTP routes
  ├── services/            # Service orchestration
  ├── infrastructure/      # Agent implementations
  └── prompts/             # Prompt strategies
```

### Local Python Development

```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Note: RAG requires Docker or manual setup.

---

## Troubleshooting

### API won't start
```bash
docker compose logs app
# Check: .env exists, OPENAI_API_KEY is set
```

### Connection refused
```bash
# Wait for startup
sleep 15
curl http://localhost:8000/docs
```

### RAG not working
```bash
docker compose restart rag-service
sleep 10  # Wait for re-indexing
```

### Port already in use
Edit `docker-compose.yml` and change port mappings.

---

## Architecture

**API Layer** → receives requests  
**Service Layer** → orchestration  
**Graph Layer** → LangGraph workflow (planner → writer → judge → editor)  
**Agent Layer** → OpenAI implementations  
**RAG Layer** → optional document retrieval  

See `app/README.md` for detailed architecture.

---

## Key Design Decisions

✅ **Protocol-based agents** — easy to swap implementations  
✅ **Separate RAG service** — flexible, scalable retrieval  
✅ **LangGraph orchestration** — clean multi-angle, multi-platform handling  
✅ **Type-safe throughout** — clear contracts  
✅ **Environment-driven config** — tune behavior without code changes  

---

## Deployment

### Docker Image

```bash
docker build -t langgraph-post-generator:latest .
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e RAG_SERVICE_URL=http://your-rag-service:8100 \
  langgraph-post-generator:latest
```

### Running Without RAG

Comment out RAG calls in `app/tools/rag_tools.py` and run the app container standalone.

---

## Documentation

- `app/README.md` — architecture details
- `app/api/README.md` — API layer
- `app/infrastructure/agents/README.md` — agent implementations
- `app/prompts/README.md` — prompt strategies

---

That's it! You're ready to generate platform-ready content.
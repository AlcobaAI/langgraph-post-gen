FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

FROM python:3.12-alpine
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv

# Copy all files (including the 'app' directory) into the container's /app folder
COPY . . 

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Since main.py is inside the 'app' folder, use 'app.main:app'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
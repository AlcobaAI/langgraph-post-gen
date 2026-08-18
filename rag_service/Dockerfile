FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY rag_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY rag_service /app/rag_service

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "rag_service.main:app", "--host", "0.0.0.0", "--port", "8100"]

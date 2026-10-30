# StoreGuard API image. Build context is the repo root.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install the shared contracts first, then the services and the API.
COPY packages/contracts/python ./packages/contracts/python
COPY services/integrations ./services/integrations
COPY services/vision ./services/vision
COPY apps/api ./apps/api

RUN pip install --no-cache-dir \
    ./packages/contracts/python \
    ./services/integrations \
    ./services/vision \
    ./apps/api

EXPOSE 8000

# Phase 0 serves in-memory SIMULATED data; no DB connection is required.
CMD ["uvicorn", "storeguard_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

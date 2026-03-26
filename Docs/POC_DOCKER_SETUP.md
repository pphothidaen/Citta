# Citta PoC Docker Setup

This document turns the architecture plan into a runnable proof of concept.

## Goal

Run each logical Citta node as a separate Docker Compose project so you can validate:

- Node 1 can serve local and upstream model traffic.
- Node 2 can provide Redis, Qdrant, and watchdog services.
- Node 3 can host orchestration-side cache and memory services.
- Node 4 can generate ingest events and forward them into Node 3.

## Files

- `docker-compose.yml`: single-host quick start for local Node 1.
- `docker/node1-neural-core.yml`: Node 1 compose stack.
- `docker/node2-vector-fabric.yml`: Node 2 compose stack.
- `docker/node3-orchestrator.yml`: Node 3 compose stack.
- `docker/node4-ingress-swarm.yml`: Node 4 compose stack.

## 1. Prepare Environment

1. Copy `.env.example` to `.env`.
2. Set real API keys for any upstream model providers you want to test.
3. Set `REDIS_AUTH` to a non-default password.
4. Replace `NODE1_URL`, `QDRANT_URL`, `NODE2_REDIS_URL`, and `NODE3_INGEST_URL` with real IPs or DNS names if the nodes run on different machines.

## 2. Quick Single-Host PoC

If you only want to validate the gateway and local Ollama routing first:

```bash
docker compose up -d --build
curl http://localhost:8000/health
```

That starts:

- Ollama on port `11434`
- Citta gateway on port `8000`

## 3. Multi-Node PoC Bring-Up Order

Bring the projects up in this order so dependencies exist before downstream services start.

### Node 2

```bash
docker compose -f docker/node2-vector-fabric.yml --env-file .env up -d
```

Expected services:

- Redis broker on `6379`
- Qdrant on `6333` and `6334`
- Uptime Kuma on `3001`

### Node 1

```bash
docker compose -f docker/node1-neural-core.yml --env-file .env up -d --build
```

Expected services:

- Ollama on `11434`
- Gateway proxy on `8000`

Verify:

```bash
curl http://localhost:8000/health
```

### Node 3

```bash
docker compose -f docker/node3-orchestrator.yml --env-file .env up -d --build
```

Expected services:

- Redis Stack on `6380`
- RedisInsight on `8443`
- Chroma on `8100`
- Orchestrator API on `8001`

Verify:

```bash
curl http://localhost:8001/health
curl -X POST http://localhost:8001/v1/ingest -H 'Content-Type: application/json' -d '{"items":[{"source":"manual-test"}]}'
```

### Node 4

```bash
docker compose -f docker/node4-ingress-swarm.yml --env-file .env up -d --build
```

Expected services:

- Two edge workers that fetch `EDGE_SOURCE_URL` on an interval and enqueue ingest payloads
- One queue consumer that forwards payloads to `NODE3_INGEST_URL`

Verify Node 4 indirectly by checking Node 3 logs or calling Node 3 ingest manually.

## 4. What This PoC Covers

- Container packaging for all four planned nodes
- Real network boundaries between node roles
- Queue-based ingest flow from Node 4 to Node 3
- Vector and cache services ready for later application integration

## 5. What This PoC Does Not Cover Yet

- Production-grade service discovery
- TLS termination and certificate automation
- Actual semantic retrieval logic inside the orchestrator
- Full persistence pipeline into Qdrant and Chroma from application code
- Scrapy-based or headless-browser scraping logic on Node 4

## 6. Shutdown

```bash
docker compose -f docker/node4-ingress-swarm.yml down
docker compose -f docker/node3-orchestrator.yml down
docker compose -f docker/node1-neural-core.yml down
docker compose -f docker/node2-vector-fabric.yml down
```
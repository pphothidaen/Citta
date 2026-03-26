# Citta Production Deployment Plan

This plan maps the PoC Docker assets onto the intended real infrastructure.

## Target Layout

### Node 1: Dedicated Neural Core

- Hardware: Mac M4 Pro
- Purpose: local model inference and the primary OpenAI-compatible gateway
- Services: Ollama, Citta gateway
- Storage target: fast SSD for model weights and logs

### Node 2: Persistent Vector Fabric

- Hardware: Synology NAS or Linux storage host
- Purpose: durable broker, vector store, and observability anchor
- Services: Redis, Qdrant, Uptime Kuma
- Storage target: mirrored or backup-backed HDD/SSD volumes

### Node 3: Active Orchestrator

- Hardware: second Mac, mini PC, or Linux VM
- Purpose: cache, memory layer, orchestration API, ingestion endpoint
- Services: Redis Stack, Chroma, Citta orchestrator
- Storage target: local SSD with persistent Docker volumes

### Node 4: Adaptive Ingress Swarm

- Hardware: low-power VPS, Raspberry Pi, or Alpine/Ubuntu edge boxes
- Purpose: fetch, normalize, and enqueue external web intelligence
- Services: edge workers, queue consumer
- Storage target: minimal local state only

## Deployment Sequence

1. Deploy Node 2 first.
2. Deploy Node 1 so the gateway URL is stable.
3. Deploy Node 3 and point it to Node 1 and Node 2.
4. Deploy Node 4 last and point it to Node 2 Redis and Node 3 ingest.

## Production Preparation

### Networking

- Give each node a fixed private IP or stable internal DNS name.
- Open only required ports between nodes.
- Do not publish Redis publicly.
- Put Node 1 and Node 3 behind a reverse proxy if external clients must reach them.

Recommended internal addressing:

- `node1.internal:8000`
- `node2.internal:6379`, `6333`, `3001`
- `node3.internal:8001`, `6380`, `8100`
- `node4.internal` outbound only

### Secrets

- Store `.env` values in the host secret manager where possible.
- At minimum, keep `.env` outside source control and restrict file permissions.
- Rotate `REDIS_AUTH` and provider API keys before going live.

### Storage

- Replace PoC named volumes with bind mounts to real disks.
- Keep Qdrant and Redis append-only data on persistent disks.
- Keep Ollama model files on the fastest available SSD.
- Snapshot Node 2 volumes regularly.

Suggested bind mounts:

- Node 1: `/srv/citta/ollama`, `/srv/citta/proxy-logs`
- Node 2: `/srv/citta/redis`, `/srv/citta/qdrant`, `/srv/citta/watchdog`
- Node 3: `/srv/citta/semantic-cache`, `/srv/citta/chroma`
- Node 4: optional only, usually not required beyond logs

## Host-by-Host Deployment

### Node 1

1. Install Docker Engine or Docker Desktop.
2. Copy the repository or the relevant deployment files onto the host.
3. Put the production `.env` on the host.
4. Replace named volumes in `docker/node1-neural-core.yml` with SSD-backed bind mounts.
5. Start the stack:

```bash
docker compose -f docker/node1-neural-core.yml --env-file .env up -d --build
```

6. Pull the models you need into Ollama.
7. Test `GET /health` and one real completion request.

### Node 2

1. Ensure the storage path is on persistent disks.
2. Replace named volumes in `docker/node2-vector-fabric.yml` with real storage mounts.
3. Start the stack:

```bash
docker compose -f docker/node2-vector-fabric.yml --env-file .env up -d
```

4. Confirm Redis authentication works.
5. Confirm Qdrant collections can be created.
6. Add Uptime Kuma monitors for Node 1 and Node 3.

### Node 3

1. Set `NODE1_URL` and `QDRANT_URL` to the real internal addresses.
2. Replace named volumes in `docker/node3-orchestrator.yml` with SSD-backed mounts.
3. Start the stack:

```bash
docker compose -f docker/node3-orchestrator.yml --env-file .env up -d --build
```

4. Verify `GET /health`.
5. Verify `POST /v1/ingest`.
6. Only after that, integrate real cache lookup and vector-write logic into the application layer.

### Node 4

1. Set `NODE2_REDIS_URL` and `NODE3_INGEST_URL` to the real internal addresses.
2. Tune `POLL_INTERVAL_SECONDS` and `EDGE_SOURCE_URL` for the first production feeds.
3. Start the stack:

```bash
docker compose -f docker/node4-ingress-swarm.yml --env-file .env up -d --build
```

4. Confirm the consumer can reach Node 3.
5. Scale worker count gradually.

## Hardening Before Real Traffic

- Add a reverse proxy with TLS for Node 1 and Node 3.
- Put firewall rules around Node 2 so only internal hosts can reach Redis and Qdrant.
- Add container restart alerts and disk-usage alerts in Uptime Kuma.
- Pin image tags instead of using `latest` once the PoC is stable.
- Add backups for Node 2 and Node 3 persistent volumes.
- Add authentication in front of the public gateway if the endpoint will be internet-exposed.

## Cutover Plan

1. Validate each node separately.
2. Validate Node 4 to Node 3 ingest flow.
3. Validate Node 3 to Node 1 request flow.
4. Point one client to Node 1 and run real prompts.
5. Enable monitoring and backup jobs.
6. Only then move external clients or IDEs onto the production endpoint.

## Recommended Next Engineering Step

After infrastructure bring-up, the next code task should be implementing the real Node 3 orchestration path:

- semantic cache lookup
- vector writes to Qdrant
- memory persistence to Chroma
- queue-driven ingest normalization
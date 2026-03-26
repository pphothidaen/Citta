# Citta

A Zero-Waste Agentic AI Distributed Architecture. Orchestrating Local LLMs (Mac M4), Enterprise Data Lakes (DS224+), and Legacy Edge Scrapers (ARM) into a unified "Stream of Consciousness." Decoupled, token-efficient, and privacy-first.

> "Knowledge is not a static state, but a continuous process of arising and ceasing."

---

## Architecture Overview

```
Node 4 (Huawei Y9 / ARM Scraper)
    │  scrapes raw data
    ▼
Node 2 (Ingestion Relay)
    │  buffers & forwards
    ▼
Node 1 – Mac M4 (Orchestrator / Brain) ◄─── THIS REPO
    │  Local LLM (Ollama) + RAG
    ├──► MinIO  (S3 Object Storage)
    ├──► ChromaDB (Vector DB / Perception)
    └──► Node 3 – J1900 (n8n Action Dispatcher)
```

| Node | Hardware | Role |
|------|----------|------|
| Node 1 | Mac M4 | Orchestrator, Local LLM (Ollama), Docker host |
| Node 2 | Ingestion relay | Buffers scraper output from Node 4 |
| Node 3 | J1900 | Edge action dispatcher (n8n webhooks) |
| Node 4 | Huawei Y9 (Android ARM) | Web scraper / data collector |

---

## Repository Layout

```
Citta/
├── docker/
│   └── docker-compose.yml        # MinIO + ChromaDB (Apple Silicon M4)
├── config/
│   └── .env.example              # All environment variables with comments
├── orchestrator/
│   ├── main.py                   # Entry point – the "Thinking Loop"
│   ├── connectors/
│   │   ├── node4_connector.py    # Pull scrape items from Node 2 (Huawei Y9 relay)
│   │   └── node3_connector.py    # Dispatch actions to Node 3 (J1900 / n8n)
│   ├── storage/
│   │   ├── minio_client.py       # Object storage (raw data lake)
│   │   └── chroma_client.py      # Vector database (long-term memory / RAG)
│   ├── llm/
│   │   └── local_llm.py          # Ollama HTTP client (generate + embed)
│   └── tests/
│       └── test_orchestrator.py  # Unit tests (stdlib only)
└── requirements.txt
```

---

## Phase 1 Quick-Start (Mac M4 – Local Simulation)

### 1. Prerequisites

- Docker Desktop for Mac (Apple Silicon) — enable Rosetta if needed
- [Ollama](https://ollama.com) installed and running natively on macOS
- Python 3.11+

### 2. Configure environment

```bash
cp config/.env.example config/.env
# Edit config/.env and set strong passwords / tokens
```

### 3. Start infrastructure services

```bash
docker compose -f docker/docker-compose.yml up -d
```

Services exposed:
| Service | URL |
|---------|-----|
| MinIO S3 API | <http://localhost:9000> |
| MinIO Console | <http://localhost:9001> |
| ChromaDB | <http://localhost:8000> |

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Thinking Loop

```bash
python -m orchestrator.main
```

### 6. Run tests

```bash
python -m pytest orchestrator/tests/ -v
```

---

## Phase 2 Migration (Synology DS224+ over LAN 1 Gbps)

No business logic changes needed.  Edit **only** `config/.env`:

```dotenv
# Phase 1 (local Docker)
MINIO_HOST=minio
CHROMA_HOST=chromadb

# Phase 2 (Synology NAS)
MINIO_HOST=synology.citta.local
CHROMA_HOST=synology.citta.local
```

All virtual hostnames resolve to the correct endpoint automatically.

---

## Thinking Loop – Workflow

For each poll interval (`ORCHESTRATOR_POLL_INTERVAL_SECONDS`):

1. **Fetch** pending scrape items from Node 2 (Node 4 / Huawei Y9 relay)
2. **Store** raw payload in MinIO (date-partitioned S3 key)
3. **Embed** content via Local LLM (Ollama `/api/embeddings`)
4. **Query** ChromaDB for relevant memory (RAG context)
5. **Decide** — Local LLM analyzes item + memory → Action (`alert | store | summarize | ignore`)
6. **Dispatch** non-`ignore` actions to Node 3 (n8n webhook)
7. **Upsert** embedding into ChromaDB (update long-term memory)
8. **Acknowledge** item on Node 2 (prevent re-processing)
# 🧠 Citta (จิตตะ)

> *"Knowledge is not a static state, but a continuous process of arising and ceasing."*

**Citta** is an Enterprise-Grade, Zero-Waste Distributed AI Ecosystem designed for continuous web-intelligence and cognitive processing. Operating on a strictly decoupled edge-to-core architecture, it orchestrates localized High-Compute Inference, persistent Vector Data Lakes, low-latency API Gateways, and thermal-balanced Edge Scrapers into a unified, auto-healing "Stream of Consciousness."

## 🎯 The Pain Points We Solve

Modern AI pipelines suffer from severe structural bottlenecks. Citta eliminates them:

* 💸 **Token Bleeding:** Stops runaway LLM API costs by routing requests through a multi-tier semantic cache and local neural cores.
* 🧱 **Scraping Fragility:** Bypasses aggressive anti-bot measures using distributed, auto-rotating Edge Swarms instead of centralized servers.
* 🗑️ **Processing Noise:** Filters and minifies context at the edge, ensuring LLMs only process high-value, sanitized data (preventing hallucinations and saving context windows).
* 💥 **Single Point of Failure:** Guarantees absolute uptime with a DNS-level auto-healing watchdog and active-passive failover swarms.

## 🏗️ Architectural Core Principles

* **Absolute Zero-Waste:** Zero idle API costs via *Cognitive Memory Layer* (Semantic Caching). Zero compute waste via Hardware-Targeted Workloads.
* **Defense-in-Depth Pipeline:** Strict schema validation, output sanitization, and fallback routing ensure 100% data consistency.
* **The Hybrid Translation Router:** Token-optimized edge processing that strips, dynamically evades, and translates non-essential data locally before hitting LLM inference, reducing input costs by up to 75%.
* **Resilient Active-Passive Swarm:** DNS-level auto-healing Watchdogs guarantee IDE AI availability even during catastrophic node failures.

## 🕸️ Node Topology (Abstraction Level 0)

Citta distributes workloads across highly specialized functional nodes:

* **Node 1 (Dedicated Neural Core):** The high-compute local brain for zero-cost, privacy-first inference.
* **Node 2 (Persistent Vector Fabric):** The data lake for long-term semantic memory and vector storage.
* **Node 3 (Active Orchestrator):** The gateway router handling traffic logic, context minification, and cache lookups.
* **Node 4 (Adaptive Ingress Swarm):** Thermal-balanced edge devices responsible for resilient data ingestion.

---

## 🗺️ High-Level System Architecture

![High-Level System Architecture](https://github.com/user-attachments/assets/b68d184b-4e5e-4621-9544-4df46acf0177)

## 🔄 Sequence: The Logic of Arising & Ceasing

![Sequence: The Logic of Arising & Ceasing](https://github.com/user-attachments/assets/137c4777-096c-4b43-8019-23c54807ffeb)

## Deployment Assets

* `docker-compose.yml` boots a single-host local PoC for Node 1.
* `docker/node1-neural-core.yml` defines the dedicated neural-core host.
* `docker/node2-vector-fabric.yml` defines Redis, Qdrant, and Watchdog for storage and coordination.
* `docker/node3-orchestrator.yml` defines the orchestration host with semantic cache and memory layer.
* `docker/node4-ingress-swarm.yml` defines reusable edge-worker and queue-consumer services for ingest.
* `Docs/POC_DOCKER_SETUP.md` explains how to run the multi-node PoC.
* `Docs/PRODUCTION_DEPLOYMENT_PLAN.md` explains how to move the PoC onto real hardware.

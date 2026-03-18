# MASTER BLUEPRINT V16 FINAL

## Purpose
This document defines the current Citta architecture and execution strategy based on the latest real hardware baseline. The system starts with a small Docker-based Proof of Concept on Node 1, then migrates gradually into a phased long-term architecture.

### Core Principles
- Zero-Waste
- Slow-but-Never-Down
- Privacy-first
- Docker-first where appropriate
- Keep all nodes under a bounded operating threshold
- Target hard limit below 80%
- Normalize all AI/API outputs before treating them as canonical

---

## Phase 1 First: Small PoC on Node 1

### Goal
Validate the full system flow on a single machine before distributed deployment.

### Node Used
- **Node 1 only**

### Components in the PoC
- FastAPI
- Redis
- Qdrant
- mock ingestion worker
- mock summarization worker
- normalization layer
- optional bot bridge mock
- local LLM runtime or equivalent integration

### Deployment Style
- Docker Compose on Node 1
- small bounded datasets only
- local persistence only
- no heavy production load
- no external dependency required for baseline flow validation

### Acceptance Gate
Phase 1 is considered successful only when:
1. The stack runs reliably on Node 1.
2. End-to-end flow works.
3. Retrieval, validation, queueing, and formatting all work.
4. Response schema remains consistent.
5. Kilo extension can call the system successfully.
6. Restarting the stack does not break the flow.
7. Resource usage remains under the defined threshold envelope.

---

## Why PoC on Node 1 First

### Benefits
- fastest validation path
- lowest debugging complexity
- minimal network variables
- easy local inspection of logs, queues, and volumes
- reduced migration risk

### Accepted Rework
- services will later move from Node 1 to Node 2
- bounded PoC data will later be migrated
- API base URLs and service endpoints will later be reconfigured

---

## Phase 2 — Begin Real Development and Controlled Migration

### Goal
Move from single-node proof into a resilient service-oriented baseline.

### First Services to Migrate
1. FastAPI
2. Redis
3. Qdrant
4. normalization service
5. scheduler / queue workers

### Destination
- **Node 2** becomes the always-on service core

### Node 1 Keeps
- coding workstation role
- premium AI compute
- deeper reasoning
- deferred high-complexity tasks

### Rules
- Node 2 becomes the always-on control plane
- Node 1 becomes premium/on-demand compute
- Node 3 becomes durable storage authority
- Node 4 becomes watchdog / utility / staging
- Node 5 stays optional and non-critical

---

## Long-Term Node Roles

| Node | Long-Term Role |
|------|----------------|
| Node 1 | Coding workstation + premium AI compute |
| Node 2 | Always-on service core |
| Node 3 | Durable archive / backup / snapshots |
| Node 4 | Watchdog / utility / staging |
| Node 5 | Edge watcher / collector |
| External Operator | Mobile command / status interface |

---

## Service Placement

### Node 1
**Run**
- local development
- PoC stack during Phase 1
- local LLM runtime
- heavy reasoning
- deep summarization
- response shaping

**Avoid**
- becoming the final always-on service center

### Node 2
**Run**
- FastAPI
- Redis
- Qdrant
- scheduler
- workers
- normalization service
- bot bridge
- bounded logs

**Avoid**
- long-term archive
- detached cold backup storage

### Node 3
**Run / Store**
- snapshots
- backups
- archive
- exported reports
- historical outputs

**Avoid**
- live hot database path

### Node 4
**Run**
- watchdog services
- health probes
- retention jobs
- checksum helpers
- staging workflows

**Avoid**
- heavy inference
- high-concurrency apps

### Node 5
**Run**
- background source watchers
- lightweight collectors
- polling jobs
- raw feed submission

**Avoid**
- critical orchestration

---

## Storage Strategy

### Hot Tier
- Node 1 ADATA NVMe 2TB
- Node 2 SATA SSD 256GB

### Warm Tier
- Node 3 Seagate Exos 8TB x2
- Node 4 staging disk if attached

### Cold Tier
- removable 1TB HDDs
- detached backup drives

### Offline / Recovery Tier
- WD3200 external desktop HDD
- rescue USB media

---

## Recommended Additional Storage Uses

| Asset | Recommended Use |
|-------|-----------------|
| HGST 1TB 7200RPM | Node 4 staging / ingest workspace |
| Seagate Mobile HDD 1TB | rotating cold backup |
| KINGMAX 120GB SSD | scratch / logging / spare |
| WD portable ~1TB | detachable shuttle backup |
| WD3200 320GB | emergency frozen vault |
| Schneider 16GB USB | rescue / bootstrap toolkit |

---

## Response Normalization Standard

All outputs from:
- local LLM
- external AI
- external API
- collectors
- automation jobs

must pass through a normalization layer before they are treated as canonical.

### Required Fields
- task_id
- source_type
- task_type
- summary_short
- summary_long
- key_points
- actions
- confidence_score
- generated_by
- normalized_at
- needs_human_review
- raw_payload_ref

---

## Threshold Envelope

| Resource | Soft Limit | Hard Limit | Action |
|----------|-----------:|-----------:|--------|
| Node 1 CPU | 65% | 80% | stop non-critical heavy jobs |
| Node 1 RAM | 70% | 80% | reduce model concurrency |
| Node 1 Disk | 70% | 80% | trim local PoC data |
| Node 2 CPU | 60% | 80% | throttle workers |
| Node 2 RAM | 65% | 80% | reduce caching / queue pressure |
| Node 2 Disk | 70% | 80% | rotate logs, move snapshots to Node 3 |
| Node 4 CPU | 50% | 70% | utility-only workloads |
| Node 4 Disk | 70% | 80% | purge staging data |
| Node 3 Disk | 75% | 85% | enforce archive retention |

---

## Trade-off Matrix

| Decision | Benefit | Cost | Acceptable? |
|----------|---------|------|-------------|
| PoC on Node 1 only | fastest validation | later migration work | Yes |
| Move services to Node 2 later | stable always-on backend | more phased work | Yes |
| Keep Node 3 storage-centric | durable and safe | not usable for hot DB path | Yes |
| Use Node 4 as utility/staging | zero-waste helper role | limited compute ability | Yes |
| Keep Node 5 non-critical | avoids fragile dependency | less aggressive edge automation | Yes |
| Normalize all outputs | consistency and accuracy | extra implementation work | Required |

---

## Failure Policy

### If Node 1 is offline
- system remains alive on Node 2 after migration
- high-complexity tasks are deferred
- queue remains intact

### If Node 2 fails
- this is the most critical service-plane failure after migration
- recovery priority is highest

### If Node 3 fails
- archive and backup lag increase temporarily
- hot path may continue for a short period

### If Node 4 fails
- monitoring and housekeeping reduce temporarily

### If Node 5 fails
- source watching degrades but core operation remains alive

---

## Final Recommendation
Start with a **small Docker-based PoC on Node 1** and validate the complete flow through **Kilo extension** first.

Only after that:
- promote **Node 2** into the always-on service core,
- use **Node 3** for durable storage and backup,
- activate **Node 4** for watchdog/staging duties,
- and use **Node 5** as optional edge watchers.

This is the best current path under the real constraints:
- zero-waste
- threshold under 80%
- slow but never down
- scalable through Docker where appropriate
- consistent normalized outputs.
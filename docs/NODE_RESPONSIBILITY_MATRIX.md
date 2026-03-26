# Node Responsibility Matrix

## Purpose
This document defines the responsibility of each node under the current real resource baseline, starting with a small Docker-based PoC on Node 1 and then migrating services gradually in later phases.

---

## Current Development Strategy
1. Start with a small Docker-based PoC on Node 1.
2. Validate the complete end-to-end flow through Kilo extension.
3. Only after PoC stability is confirmed, begin phased migration to the long-term node roles.

---

## Node Role Matrix

| Node | Primary Role | Secondary Role | Run in PoC? | Run in Phase 2+? | Avoid Using For |
|------|--------------|----------------|-------------|------------------|-----------------|
| Node 1 | Coding workstation + PoC all-in-one + premium AI compute | local testing / heavy reasoning / response shaping | Yes | Yes | always-on service center |
| Node 2 | Always-on service core | API, Redis, Qdrant, workers, normalization | No | Yes | long-term archive, detached backup storage |
| Node 3 | Durable archive / backup / snapshot authority | cold storage / export / historical outputs | No | Yes | live hot DB path |
| Node 4 | Watchdog / utility / staging | health checks, retention jobs, checksum, log spool | Optional | Yes | heavy inference, high-concurrency apps |
| Node 5 | Edge watcher / collector | background polling / source monitoring / feed capture | No | Optional | critical orchestration |
| External Operator | Human interface | mobile status / commands / alerts | Optional | Yes | infrastructure execution core |

---

## What Each Node Should Run

### Node 1
- Docker-based PoC stack
- FastAPI
- Redis
- Qdrant
- mock ingestion / mock worker
- normalization layer
- LLM runtime for local testing
- Kilo integration validation

### Node 2
- FastAPI
- Redis
- Qdrant
- scheduler
- queue consumers
- normalization service
- bot bridge
- bounded log volumes

### Node 3
- backup target
- snapshots
- archive
- exported reports
- removable backup coordination

### Node 4
- watchdog services
- health probes
- retention jobs
- rsync/checksum helpers
- staging pipeline

### Node 5
- source watchers
- lightweight collectors
- polling jobs
- raw feed submission

---

## Docker Suitability

| Node | Docker-first? | Notes |
|------|---------------|------|
| Node 1 | Yes for PoC stack | local LLM runtime may be native if more stable |
| Node 2 | Yes | main service host in future phases |
| Node 3 | Selective | use native NAS features where better suited |
| Node 4 | Yes | ideal for lightweight utility containers |
| Node 5 | Limited | Android constraints |

---

## Threshold Policy

| Node | CPU Soft / Hard | RAM Soft / Hard | Disk Soft / Hard |
|------|------------------|------------------|------------------|
| Node 1 | 65% / 80% | 70% / 80% | 70% / 80% |
| Node 2 | 60% / 80% | 65% / 80% | 70% / 80% |
| Node 3 | storage-centric | storage-centric | 75% / 85% |
| Node 4 | 50% / 70% | 60% / 75% | 70% / 80% |
| Node 5 | stability-first | stability-first | low local retention only |

---

## Core Operating Rules
1. Node 1 is the first PoC node and the primary coding workstation.
2. Node 2 becomes the always-on service center after PoC succeeds.
3. Node 3 remains the durable storage authority.
4. Node 4 supports reliability, staging, and housekeeping.
5. Node 5 remains outside the critical path.
6. All outputs from local AI and external AI/API must pass through a normalization layer before being treated as canonical results.
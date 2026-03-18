# MASTER BLUEPRINT V16 FINAL

## Purpose
เอกสารนี้เป็นแผนสถาปัตยกรรมหลักของระบบ Citta ฉบับอัปเดตตามทรัพยากรจริงที่มีอยู่ โดยยึดหลัก:
- Zero-Waste
- Slow-but-Never-Down
- Privacy-first
- Decoupled architecture
- ใช้ hardware ให้เหมาะกับประเภทงาน

---

## Design Principles

1. **Compute แยกจาก Storage**
   - Node 1 ทำงาน AI/LLM
   - Node 5 ทำงาน service/orchestration
   - Node 2 ทำงาน durability/storage

2. **Degrade gracefully**
   - ถ้า AI node ไม่พร้อม ระบบต้องยังตอบได้
   - ถ้า NAS ไม่พร้อม งาน hot path ต้องยังทำงานต่อได้ชั่วคราว

3. **Use the right model for the right task**
   - งาน routing / tagging ใช้ model เล็ก
   - งาน structured generation ใช้ model กลาง
   - งาน reasoning ลึกใช้ model ใหญ่บน Mac M4

4. **Local fast storage for hot path**
   - Hot inference ใช้ Node 1 NVMe
   - Hot service ใช้ Node 5 SSD
   - Backup/snapshots ไป Node 2

5. **Unassigned assets stay non-critical**
   - storage ที่ยังไม่ verify ห้ามใช้เป็น production dependency

---

## Current End-State Node Roles

| Node | Role |
|------|------|
| Node 1 | Primary LLM / AI Compute |
| Node 2 | Durable NAS / Backup / Archive |
| Node 3 | Utility / Watchdog / Backup Verifier |
| Node 4 | Edge Ingestion / Headless Collectors |
| Node 5 | API Gateway / Redis / Qdrant / Semantic Router / Orchestration |

---

## Service Placement

### Node 1 — MacBook Pro M4
**Run**
- Ollama or equivalent local LLM runtime
- heavy reasoning tasks
- embeddings / reranking
- evaluation and model testing

**Do not make primary**
- long-term archive
- only-copy backups
- critical shared database persistence

### Node 2 — Synology DS224+
**Run / Store**
- archive
- snapshots
- backup targets
- historical logs
- exported datasets

**Do not use as**
- primary low-latency database path
- heavy compute runtime

### Node 3 — DIY J1900 NAS
**Run**
- monitoring
- health checks
- backup verification
- rsync / checksum / retention jobs
- archive staging

**Avoid**
- heavy AI workloads
- high-concurrency services

### Node 4 — Huawei Y9 2018 x2
**Run**
- data collection
- payload submission
- edge scraping
- remote capture

**Avoid**
- orchestration
- durable storage
- critical-path processing

### Node 5 — Lenovo ThinkCentre M720q
**Run**
- FastAPI
- Redis
- Qdrant
- workers
- semantic router
- validation layer
- task queue
- retrieval orchestration

---

## Storage Strategy

### Hot Tier
- Node 1 ADATA NVMe 2TB
- Node 5 SATA SSD 256GB

### Warm Tier
- Node 2 Seagate Exos 8TB x2
- optional Node 3 staging disk

### Cold Tier
- removable 1TB HDDs
- detached backup drives

### Offline / Recovery Tier
- WD3200 desktop external
- rescue USB media

---

## Unassigned Storage Recommended Uses

| Asset | Recommended Use |
|-------|-----------------|
| HGST 1TB 7200RPM | Node 3 archive staging |
| Seagate Mobile HDD 1TB | rotating cold backup |
| KINGMAX 120GB SSD | spare / maintenance / scratch SSD |
| WD portable ~1TB | shuttle backup / export disk |
| WD3200 320GB | deep cold archive / emergency vault |
| Schneider 16GB USB | rescue boot / admin toolkit |

---

## Phased Implementation Plan

### Phase 1 — Stable Core Bring-up
**Goal:** make the system work correctly on the core nodes first.

**Primary arrangement**
- Node 1 = AI compute
- Node 5 = service plane
- Node 2 = durable backup/archive
- Node 3 = optional watchdog
- Node 4 = not yet in critical flow

**Tasks**
1. Bring up FastAPI, Redis, and Qdrant on Node 5.
2. Connect Node 5 to Node 1 for LLM requests.
3. Store hot service state locally on Node 5 SSD.
4. Send backups/snapshots to Node 2.
5. Establish health checks and timeout handling.

### Phase 2 — Reliability Hardening
**Goal:** ensure restartability, backup validity, and degraded-mode behavior.

**Tasks**
1. Add snapshot/export jobs from Node 5 to Node 2.
2. Add model/config backup from Node 1 to Node 2.
3. Run monitoring and verification jobs on Node 3.
4. Add log rotation and retention policy.
5. Test recovery from backup.

### Phase 3 — Edge Activation
**Goal:** activate Node 4 without making it a critical dependency.

**Tasks**
1. Build a lightweight ingestion protocol.
2. Route edge payloads into Node 5.
3. Archive raw payloads to Node 2.
4. Use Node 3 for integrity checks and staging workflows.

### Phase 4 — Controlled Optimization
**Goal:** increase throughput without increasing fragility.

**Tasks**
1. Introduce background queues.
2. Limit concurrency on heavy services.
3. Promote only verified storage into operational use.
4. Use removable drives for offline recovery copies.

---

## Trade-off Matrix

| Option | Strength | Weakness | Recommendation |
|--------|----------|----------|----------------|
| Mac-only core | simple and fast to start | overload risk, poor separation | not preferred now |
| NAS-centric | good durability | poor hot-path latency | not preferred for services |
| Split core (Node 1 + Node 5 + Node 2) | balanced, reliable, scalable | more setup work than single-node | **recommended** |

---

## Recommended Operating Policy

1. **Node 5 is the service center.**
2. **Node 1 is the AI brain.**
3. **Node 2 is the memory and archive.**
4. **Node 3 is the caretaker and watchdog.**
5. **Node 4 is the external sensor/collector layer.**

---

## Failure Policy

### If Node 1 fails
- Node 5 remains online
- requests can queue, reject gracefully, or fall back to lighter logic

### If Node 2 fails temporarily
- hot path continues on Node 1 / Node 5
- backup lag is tolerated temporarily

### If Node 3 fails
- monitoring and housekeeping reduce, but core services remain online

### If Node 4 fails
- ingestion capacity drops, but core remains online

### If Node 5 fails
- this is the most critical service-plane failure
- recovery priority is highest
- snapshots and config backups must support rapid restore

---

## Final Recommendation
Use a **split-core architecture**:

- **Node 1:** AI compute
- **Node 5:** live services and orchestration
- **Node 2:** durable storage and backup
- **Node 3:** utility reliability node
- **Node 4:** edge ingestion only

This architecture best satisfies the system goals of:
- zero-waste resource allocation
- acceptable slowness
- strong operational resilience
- minimal unnecessary complexity
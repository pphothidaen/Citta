# Node Responsibility Matrix

## Purpose
เอกสารนี้กำหนดหน้าที่ของแต่ละ node และ storage role ของระบบ Citta โดยยึดหลัก Zero-Waste, Slow-but-Never-Down และแยก compute / service / storage / edge ให้ชัดเจน

## Node Role Map
| Node | Hardware | Primary Role | Secondary Role | Avoid Using For |
|------|----------|--------------|----------------|-----------------|
| Node 1 | MacBook Pro M4 + ADATA NVMe 2TB | Primary LLM / AI Compute | Dev, evaluation, model experimentation | Long-term archive, backup authority |
| Node 2 | Synology DS224+ + Seagate Exos 8TB x2 | Durable NAS / backup / archive | Snapshot repository, log retention | Live low-latency DB path, heavy compute |
| Node 3 | DIY J1900 NAS + 8GB RAM + Advantech mSATA 256GB | Utility / watchdog / backup verifier | Archive staging, relay jobs, low-power helper | Heavy AI inference, high-concurrency services |
| Node 4 | Huawei Y9 2018 x2 | Edge ingestion / headless collectors | Remote/mobile capture endpoints | Orchestrator, durable storage, compute core |
| Node 5 | Lenovo ThinkCentre M720q i5-8500T + 32GB RAM + SATA SSD 256GB | Main API / Redis / Qdrant / orchestration | Workers, semantic routing, validation | Long-term archive, removable backup storage |

## Storage Role Map
| Storage | Assigned Role | Node |
|---------|---------------|------|
| ADATA NVMe 2TB | Hot AI workspace, model storage, local cache | Node 1 |
| Seagate Exos 8TB x2 | Durable NAS storage, archive, snapshots, backups | Node 2 |
| Advantech mSATA SSD 256GB | System disk for utility runtime | Node 3 |
| Lenovo SATA SSD 256GB | Service disk for API, Redis, Qdrant | Node 5 |
| HGST 1TB 7200RPM | Recommended archive staging disk | Node 3 (recommended) |
| Seagate Mobile HDD 1TB | Rotating backup / cold copy | External / removable |
| KINGMAX SMV32 120GB | Spare / maintenance / scratch SSD | Unassigned |
| WD portable external ~1TB | Detachable shuttle backup | External / removable |
| WD3200H1U-00 320GB | Deep cold archive / emergency vault | Offline |
| Schneider USB flash 16GB | Rescue / recovery / admin toolkit | Admin |

## Hot / Warm / Cold / Offline Mapping
- Hot: Node 1 ADATA NVMe, Node 5 SATA SSD
- Warm: Node 2 NAS storage, Node 3 staging if attached
- Cold: removable HDD backup copies
- Offline: WD3200 desktop external, rescue USB media

## Guiding Rules
1. Node 1 handles heavy AI reasoning only.
2. Node 5 handles live services and orchestration.
3. Node 2 is the durability authority for backups and archives.
4. Node 3 protects reliability through monitoring and housekeeping.
5. Node 4 stays outside the critical path.
6. Unassigned storage must be explicitly verified before promotion into production.
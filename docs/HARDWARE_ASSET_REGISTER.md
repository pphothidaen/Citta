# Hardware & Storage Asset Register

## Purpose
This document records the latest real hardware and storage resources used by CittaProject as the baseline for the Node 1 small Docker PoC, phased migration, and real development.

---

## Node Mapping (Definitive)

| Node | Hardware | Current Intent |
|------|----------|----------------|
| Node 1 | MacBook Pro M4 + Hagibis Dock + ADATA NVMe 2TB | Primary coding workstation + PoC node + premium AI compute |
| Node 2 | Lenovo ThinkCentre M720q, Intel i5-8500T, RAM 32GB, SATA SSD 256GB | Future always-on service core |
| Node 3 | Synology DS224+, onboard 2GB DDR4 non-ECC + added 16GB RAM, Seagate Exos 8TB x2 | Durable storage / backup / archive |
| Node 4 | DIY J1900 NAS, RAM 8GB, Advantech mSATA SSD 256GB | Utility / watchdog / staging node |
| Node 5 | Huawei Y9 2018 x2, no monitor, no battery, direct USB-A | Edge watcher / collector nodes |
| External Operator | Personal phone | Remote command / status via Telegram, Discord, or Line |

---

## Assigned Storage

| Asset | Capacity | Type | Assigned To | Role | Tier |
|------|---------:|------|-------------|------|------|
| ADATA NVMe | 2TB | NVMe SSD | Node 1 | hot AI workspace / model cache / local dev data | Hot |
| Lenovo internal SSD | 256GB | SATA SSD | Node 2 | service runtime / Docker volumes / API / Redis / Qdrant | Hot |
| Seagate Exos x2 | 8TB x2 | NAS HDD | Node 3 | durable archive / snapshot / backup / historical output | Warm / Cold |
| Advantech mSATA | 256GB | mSATA SSD | Node 4 | OS only / utility runtime | OS-only |

---

## Recommended Additional Storage Assignment

| Asset | Capacity | Type | Recommended Assignment | Intended Role | Tier | Status |
|------|---------:|------|------------------------|---------------|------|--------|
| HGST 2.5" HDD | 1TB | 7200RPM SATA HDD | Node 4 | staging / raw ingest landing / batch workspace | Warm | Recommended |
| KINGMAX SMV32 | 120GB | SATA SSD | Node 4 if port available, otherwise spare | logging / scratch / rescue SSD | Warm / Spare | Recommended |
| Seagate Mobile HDD | 1TB | 2.5" SATA HDD | Node 3 via external USB or backup rotation | rotating cold backup | Cold | Recommended |
| WD portable external | ~1TB | External HDD | Node 3 external rotation / shuttle backup | detachable backup / export disk | Cold | Recommended |
| WD desktop external WD3200H1U-00 | 320GB | Desktop external HDD | Offline only | emergency vault / frozen snapshot | Offline | Recommended |
| Schneider USB flash | 16GB | USB flash | Admin toolkit | rescue / bootstrap / recovery media | Offline | Recommended |

---

## Status Categories

| Category | Assets |
|----------|--------|
| Assigned / In-use | Node 1 ADATA 2TB, Node 2 SSD 256GB, Node 3 Exos 8TB x2, Node 4 Advantech 256GB |
| Recommended to assign next | HGST 1TB, KINGMAX 120GB, Seagate Mobile 1TB, WD portable ~1TB, WD 320GB, USB 16GB |
| Spare | KINGMAX 120GB if not installed |
| Cold / Offline | Seagate Mobile 1TB, WD portable ~1TB, WD 320GB, USB 16GB |

---

## Constraints
- Node 1 is the initial PoC environment but will not be the final always-on service center.
- Node 2 has only 256GB SSD, so retention and bounded local persistence are mandatory.
- Node 3 should remain storage-centric and must not be used as the primary live vector database path.
- Node 4 should remain a low-power utility/staging host, not a heavy compute node.
- Node 5 must stay outside the critical path.
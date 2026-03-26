<<<<<<< HEAD
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

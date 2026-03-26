# Citta
Citta is a zero-waste, distributed AI ecosystem designed for continuous web-intelligence and cognitive processing. Built on a decoupled edge-to-core architecture, it orchestrates Local LLMs, persistent Data Lakes, and low-power Edge Scrapers into a unified "Stream of Consciousness."

“Knowledge is not a static state, but a continuous process of arising and ceasing.”

## Deployment Assets

- `docker-compose.yml` boots a single-host local PoC for Node 1.
- `docker/node1-neural-core.yml` defines the dedicated neural-core host.
- `docker/node2-vector-fabric.yml` defines Redis, Qdrant, and Watchdog for storage and coordination.
- `docker/node3-orchestrator.yml` defines the orchestration host with semantic cache and memory layer.
- `docker/node4-ingress-swarm.yml` defines reusable edge-worker and queue-consumer services for ingest.
- `Docs/POC_DOCKER_SETUP.md` explains how to run the multi-node PoC.
- `Docs/PRODUCTION_DEPLOYMENT_PLAN.md` explains how to move the PoC onto real hardware.

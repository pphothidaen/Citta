# Phase 1 Acceptance Checklist

## Goal
Validate that the Node 1 small Docker PoC is stable enough to begin real development and phased migration.

## Functional Checks
- [ ] FastAPI starts successfully.
- [ ] Redis starts successfully.
- [ ] Qdrant starts successfully.
- [ ] Worker mock starts successfully.
- [ ] Normalization service starts successfully.
- [ ] End-to-end request completes.
- [ ] Retrieval flow works.
- [ ] Queue flow works.
- [ ] Response schema is consistent.
- [ ] Kilo extension can call the system successfully.

## Reliability Checks
- [ ] Restarting the Docker Compose stack does not break the flow.
- [ ] Temporary data remains bounded.
- [ ] Logs remain bounded and rotated.
- [ ] No single container enters an uncontrolled restart loop.
- [ ] Local persistence paths are mapped correctly.

## Threshold Checks
- [ ] Node 1 CPU stays below 80% hard limit.
- [ ] Node 1 RAM stays below 80% hard limit.
- [ ] Node 1 disk utilization stays below 80% hard limit.

## Migration Readiness
- [ ] Service boundaries are clear enough to move FastAPI to Node 2 later.
- [ ] Redis data path is isolated enough to migrate later.
- [ ] Qdrant data path is isolated enough to migrate later.
- [ ] Environment variables are externalized.
- [ ] API base URLs can be changed without code rewrite.

## Decision Rule
Proceed to Phase 2 only when all critical checks are complete and the PoC remains stable under repeated local testing.
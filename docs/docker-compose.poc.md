# docker-compose PoC Guide

## Purpose
This document defines the initial small Proof of Concept deployment on Node 1 using Docker Compose.

## Goal
Validate the complete local flow before any real migration begins.

## PoC Services
- `api`: FastAPI application
- `redis`: queue / cache / transient state
- `qdrant`: bounded local vector store
- `worker-mock`: mock ingestion / background worker
- `normalizer`: response normalization service

## Design Principles
- one Docker network
- bounded local persistence
- explicit named volume directories
- small corpus only
- fixed schema outputs
- no uncontrolled concurrency
- log rotation from day one

## Suggested Volume Layout
- `./volumes/api-logs`
- `./volumes/redis-data`
- `./volumes/qdrant-data`
- `./volumes/worker-state`
- `./volumes/normalizer-cache`

## Boundaries
- do not use large production datasets
- do not treat PoC data as canonical archive
- do not exceed threshold limits
- do not depend on distributed networking yet

## Exit Criteria
Proceed only when:
1. Kilo extension can call the system.
2. FastAPI, Redis, and Qdrant restart cleanly.
3. queue flow works end-to-end.
4. response normalization is stable.
5. all major components remain within thresholds.
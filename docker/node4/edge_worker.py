import json
import os
import time
from datetime import datetime, timezone

import httpx
import redis


def build_payload(worker_id: str, source_url: str) -> dict[str, str]:
    document = {
        "worker_id": worker_id,
        "source_url": source_url,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        response = httpx.get(source_url, timeout=10.0, follow_redirects=True)
        document["status_code"] = str(response.status_code)
        document["content_type"] = response.headers.get("content-type", "unknown")
        document["excerpt"] = response.text[:500]
    except Exception as exc:  # pragma: no cover - defensive logging for a long-lived worker
        document["error"] = str(exc)

    return {"items": [document]}


def main() -> None:
    worker_id = os.getenv("WORKER_ID", "edge-unknown")
    source_url = os.getenv("EDGE_SOURCE_URL", "https://example.com")
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    queue_name = os.getenv("INGEST_QUEUE", "citta:ingest")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    client = redis.Redis.from_url(redis_url, decode_responses=True)

    while True:
        payload = build_payload(worker_id, source_url)
        client.rpush(queue_name, json.dumps(payload))
        print(f"queued ingest payload for {worker_id}", flush=True)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
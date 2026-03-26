import json
import os

import httpx
import redis


def main() -> None:
    queue_name = os.getenv("INGEST_QUEUE", "citta:ingest")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ingest_url = os.getenv("NODE3_INGEST_URL", "http://localhost:8001/v1/ingest")

    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    while True:
        message = redis_client.blpop(queue_name, timeout=0)
        if not message:
            continue

        _, raw_payload = message
        payload = json.loads(raw_payload)
        response = httpx.post(ingest_url, json=payload, timeout=10.0)
        response.raise_for_status()
        print(f"forwarded {len(payload.get('items', []))} item(s) to {ingest_url}", flush=True)


if __name__ == "__main__":
    main()
"""
Citta Orchestrator – Main Entry Point
"The Thinking Loop" (Brain Logic on Mac M4 / Node 1)

Workflow (runs every ORCHESTRATOR_POLL_INTERVAL_SECONDS):
    1. Pull pending scrape items from Node 2 (relay for Node 4 / Huawei Y9)
    2. For each item:
        a. Store raw payload in MinIO (S3 Object Storage)
        b. Generate embedding via Local LLM (Ollama on Mac M4)
        c. Query ChromaDB for relevant memory (RAG context)
        d. Ask Local LLM to analyze item + memory → Action decision
        e. Dispatch Action to Node 3 (J1900 / n8n webhook)
        f. Upsert document + embedding into ChromaDB (update memory)
        g. Acknowledge item on Node 2 so it is not re-processed

Usage:
    python -m orchestrator.main

Environment:
    All configuration via config/.env (see config/.env.example).
    The script looks for config/.env relative to the project root.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import structlog
from dotenv import load_dotenv

# ── Load environment from config/.env ────────────────────────────────
_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE = _PROJECT_ROOT / "config" / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=False)

# ── Structured logging setup ─────────────────────────────────────────
_log_level = os.environ.get("ORCHESTRATOR_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _log_level, logging.INFO),
    format="%(message)s",
    stream=sys.stdout,
)
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, _log_level, logging.INFO)
    ),
)
log = structlog.get_logger()

# ── Lazy imports (after env is loaded) ───────────────────────────────
from orchestrator.connectors.node3_connector import Node3Connector  # noqa: E402
from orchestrator.connectors.node4_connector import Node4Connector  # noqa: E402
from orchestrator.llm.local_llm import LocalLLMClient  # noqa: E402
from orchestrator.storage.chroma_client import ChromaStorageClient  # noqa: E402
from orchestrator.storage.minio_client import MinioStorageClient  # noqa: E402


def _object_name_for(item: dict) -> str:
    """Build a MinIO key for the given scrape item (date-partitioned)."""
    ts = item.get("captured_at", datetime.now(UTC).isoformat())
    date_part = ts[:10]  # YYYY-MM-DD
    return f"{date_part}/{item['id']}.json"


def process_item(
    item: dict,
    minio: MinioStorageClient,
    chroma: ChromaStorageClient,
    llm: LocalLLMClient,
    node3: Node3Connector,
) -> None:
    """Full processing pipeline for a single scrape item."""
    item_id: str = item["id"]
    log.info("Processing item", item_id=item_id, source=item.get("source"))

    # 2a. Store raw payload in MinIO
    object_name = _object_name_for(item)
    minio.put_json(object_name, item)
    log.debug("Stored raw payload in MinIO", object_name=object_name)

    # 2b. Generate embedding
    content_text = str(item.get("content", ""))
    embedding = llm.embed(content_text[:2000])  # Ollama token limit guard

    # 2c. Query ChromaDB for relevant memory (RAG)
    memory_hits = chroma.query(query_embedding=embedding, n_results=5)
    log.debug("RAG context retrieved", hit_count=len(memory_hits))

    # 2d. Analyze item + memory → Action
    action = llm.analyze_and_decide(item, memory_context=memory_hits)
    log.info(
        "LLM decision",
        item_id=item_id,
        action_type=action["type"],
        reason=action.get("reason", "")[:120],
    )

    # 2e. Dispatch Action to Node 3 (n8n)
    if action["type"] != "ignore":
        node3.dispatch_action(action)
        log.info("Action dispatched to Node 3", action_type=action["type"])

    # 2f. Upsert into ChromaDB (update long-term memory)
    chroma.upsert(
        doc_id=item_id,
        document=content_text[:2000],
        embedding=embedding,
        metadata={
            "source": item.get("source", ""),
            "captured_at": item.get("captured_at", ""),
            "action_type": action["type"],
            "minio_key": object_name,
        },
    )
    log.debug("Upserted embedding into ChromaDB", item_id=item_id)


def run_once(
    node4: Node4Connector,
    node3: Node3Connector,
    minio: MinioStorageClient,
    chroma: ChromaStorageClient,
    llm: LocalLLMClient,
) -> int:
    """Execute one iteration of the Thinking Loop.

    Returns:
        Number of items processed.
    """
    items = node4.fetch_pending_items()
    if not items:
        log.debug("No pending items – sleeping until next cycle")
        return 0

    log.info("Thinking loop iteration started", item_count=len(items))
    processed = 0
    for item in items:
        try:
            process_item(item, minio, chroma, llm, node3)
            node4.acknowledge_item(item["id"])
            processed += 1
        except Exception:  # noqa: BLE001
            log.exception("Failed to process item", item_id=item.get("id"))
            # Continue with the next item – do not crash the whole loop

    log.info("Thinking loop iteration complete", processed=processed, total=len(items))
    return processed


def main() -> None:
    """Bootstrap all clients and start the continuous Thinking Loop."""
    poll_interval = int(os.environ.get("ORCHESTRATOR_POLL_INTERVAL_SECONDS", "30"))

    log.info("Citta Orchestrator starting", poll_interval_seconds=poll_interval)

    node4 = Node4Connector()
    node3 = Node3Connector()
    minio = MinioStorageClient()
    chroma = ChromaStorageClient()
    llm = LocalLLMClient()

    log.info("All clients initialised – entering Thinking Loop")

    while True:
        try:
            run_once(node4, node3, minio, chroma, llm)
        except Exception:  # noqa: BLE001
            log.exception("Unhandled error in Thinking Loop – will retry next cycle")
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()

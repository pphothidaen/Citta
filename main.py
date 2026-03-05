"""Citta — Phase 1 entry point.

Usage
-----
    # 1. Start infrastructure
    docker compose up -d

    # 2. (Optional) Ingest sample data
    python main.py --ingest

    # 3. Run an agent query
    python main.py --query "What files are in the data lake?"

Architecture (single-node simulation)
--------------------------------------
    Perception (ingestor.py)
        ↓  embeds & stores chunks in ChromaDB
        ↓  uploads raw files to MinIO
    Thinking (agent.py)
        ↓  ReAct LLM orchestrator (Ollama local)
        ↓  calls Acting tools as needed
    Acting (tools.py)
        ↓  list_objects → MinIO
        ↓  query_memory → ChromaDB
"""
import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("citta.main")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="citta",
        description="Citta Phase 1 — Local AI edge simulation",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Run sample data ingestion into ChromaDB and MinIO, then exit.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Send a single query to the agent and print the response.",
    )
    return parser.parse_args()


def _run_ingest() -> None:
    """Demonstrate the Perception layer with sample data."""
    from citta.perception.ingestor import ensure_bucket, ingest_texts

    logger.info("=== Perception: ensuring MinIO bucket exists ===")
    ensure_bucket()

    sample_texts = [
        "Citta is a zero-waste distributed AI edge architecture.",
        "Node 1 (Brain): MacBook Pro M4 — high-compute orchestrator.",
        "Node 2 (Data Lake): Synology DS224+ running MinIO and ChromaDB.",
        "Node 3 (Worker): Debian J1900 running n8n automation.",
        "Node 4 (Edge): ARM-based scrapers powered by Openclaw.",
    ]
    sample_metadata = [{"source": "bootstrap", "node": str(i)} for i in range(len(sample_texts))]

    logger.info("=== Perception: ingesting %d chunks into ChromaDB ===", len(sample_texts))
    ingest_texts(sample_texts, sample_metadata)
    logger.info("Ingestion complete.")


def _run_query(query: str) -> None:
    """Pass a query through the full Thinking → Acting pipeline."""
    from citta.thinking.agent import build_agent, run

    logger.info("=== Thinking: building agent ===")
    agent = build_agent()

    logger.info("=== Thinking: running query ===\n%s", query)
    answer = run(query, agent=agent)
    print("\n--- Agent Response ---")
    print(answer)


def main() -> None:
    args = _parse_args()

    if not args.ingest and args.query is None:
        # Default: ingest sample data then run a demo query
        _run_ingest()
        _run_query("What files are in the data lake?")
        return

    if args.ingest:
        _run_ingest()

    if args.query:
        _run_query(args.query)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted.")
        sys.exit(0)

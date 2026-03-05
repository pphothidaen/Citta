"""Acting layer — external actions the agent can perform.

Responsibilities
----------------
* Expose LangChain Tool objects that wrap concrete side-effects:
    - list_objects   : list files in the MinIO data lake.
    - query_memory   : semantic search against ChromaDB.

These tools are passed to the Thinking layer's agent executor so the LLM
can decide *when* and *how* to call them.
"""
import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from langchain.tools import Tool

from config import settings
from citta.perception.ingestor import _s3_client, get_vector_store

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _list_objects(prefix: str = "") -> str:
    """List objects in the MinIO bucket, optionally filtered by prefix."""
    client = _s3_client()
    try:
        resp = client.list_objects_v2(
            Bucket=settings.MINIO_BUCKET,
            Prefix=prefix,
        )
        keys = [obj["Key"] for obj in resp.get("Contents", [])]
        return json.dumps(keys)
    except (ClientError, BotoCoreError) as exc:
        logger.error("list_objects failed: %s", exc)
        return json.dumps({"error": str(exc)})


def _query_memory(query: str) -> str:
    """Semantic search against ChromaDB; returns top-3 matching chunks."""
    try:
        store = get_vector_store()
        docs = store.similarity_search(query, k=3)
        results = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
        return json.dumps(results)
    except (ValueError, RuntimeError, ConnectionError) as exc:
        logger.error("query_memory failed: %s", exc)
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Exported tool list
# ---------------------------------------------------------------------------

def get_tools() -> list[Tool]:
    """Return all acting tools ready for the agent executor."""
    return [
        Tool(
            name="list_objects",
            func=_list_objects,
            description=(
                "List files stored in the MinIO data lake. "
                "Input: optional prefix string. "
                "Output: JSON array of object keys."
            ),
        ),
        Tool(
            name="query_memory",
            func=_query_memory,
            description=(
                "Semantic search across the ChromaDB vector memory. "
                "Input: natural-language query string. "
                "Output: JSON array of the top-3 matching text chunks with metadata."
            ),
        ),
    ]

"""
ChromaDB Storage Client

Wraps the official ``chromadb`` Python client to provide Citta-specific
helpers for storing and retrieving embeddings ("Perception" / long-term
memory) used during RAG (Retrieval-Augmented Generation) queries by the
Local LLM on Mac M4.

Environment variables (from config/.env):
    CHROMA_HOST        – virtual hostname (Phase 1: "chromadb", Phase 2: NAS hostname)
    CHROMA_PORT        – HTTP port (default 8000)
    CHROMA_AUTH_TOKEN  – bearer token for server-side auth
    CHROMA_COLLECTION  – default collection name
"""

from __future__ import annotations

import logging
import os
from typing import Any

import chromadb
from chromadb.config import Settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ChromaStorageClient:
    """Store and query embeddings in ChromaDB."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        auth_token: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        _host = host or os.environ["CHROMA_HOST"]
        _port = int(port or os.environ.get("CHROMA_PORT", "8000"))
        _token = auth_token or os.environ.get("CHROMA_AUTH_TOKEN", "")
        self._collection_name = collection_name or os.environ.get(
            "CHROMA_COLLECTION", "citta_perception"
        )

        settings = Settings(
            chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
            chroma_client_auth_credentials=_token,
            anonymized_telemetry=False,
        )
        self._client = chromadb.HttpClient(
            host=_host,
            port=_port,
            settings=settings,
        )
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "Connected to ChromaDB at %s:%d, collection '%s'",
            _host,
            _port,
            self._collection_name,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def upsert(
        self,
        doc_id: str,
        document: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add or update a document embedding in the collection.

        Args:
            doc_id:    Unique identifier for the document.
            document:  Raw text of the document (stored alongside embedding).
            embedding: Pre-computed embedding vector from the Local LLM.
            metadata:  Optional dict of scalar metadata (str / int / float / bool).
        """
        self._collection.upsert(
            ids=[doc_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata or {}],
        )
        logger.debug("Upserted document '%s' into collection '%s'", doc_id, self._collection_name)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Find the *n_results* most similar documents to *query_embedding*.

        Args:
            query_embedding: Embedding vector of the query.
            n_results:       Maximum number of results to return.
            where:           Optional ChromaDB ``where`` filter dict.

        Returns:
            List of dicts with keys ``id``, ``document``, ``metadata``,
            and ``distance``.
        """
        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)
        hits: list[dict[str, Any]] = []
        for idx, doc_id in enumerate(results["ids"][0]):
            hits.append(
                {
                    "id": doc_id,
                    "document": results["documents"][0][idx],
                    "metadata": results["metadatas"][0][idx],
                    "distance": results["distances"][0][idx],
                }
            )
        logger.debug(
            "Query returned %d results from collection '%s'",
            len(hits),
            self._collection_name,
        )
        return hits

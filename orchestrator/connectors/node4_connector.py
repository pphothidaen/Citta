"""
Node 4 Connector – Huawei Y9 (Android ARM Scraper)

Node 4 runs a lightweight HTTP server that exposes scraped data
(raw web content, sensor readings, etc.) to the rest of the Citta
network via Node 2.  This connector polls Node 2's ingestion endpoint
and returns structured payloads ready for storage in MinIO and
embedding in ChromaDB.

Environment variables (from config/.env):
    NODE2_HOST  – virtual hostname of the ingestion relay node
    NODE2_PORT  – HTTP port of the ingestion relay node
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class Node4Connector:
    """Fetches scraped data from Node 2 (the relay for Node 4 / Huawei Y9)."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._host = host or os.environ["NODE2_HOST"]
        self._port = int(port or os.environ.get("NODE2_PORT", "8080"))
        self._timeout = timeout
        self._base_url = f"http://{self._host}:{self._port}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def fetch_pending_items(self) -> list[dict[str, Any]]:
        """Return a list of unprocessed scrape payloads from Node 2.

        Each item is a dict with at least the keys:
            id       – unique identifier assigned by the scraper
            source   – originating URL or sensor identifier
            content  – raw text / binary content (base64 when binary)
            captured_at – ISO-8601 timestamp of capture
        """
        url = f"{self._base_url}/api/v1/items/pending"
        logger.debug("Fetching pending items from %s", url)
        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            data: list[dict[str, Any]] = response.json()
            logger.info("Fetched %d pending items from Node 2", len(data))
            return data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def acknowledge_item(self, item_id: str) -> None:
        """Mark an item as processed so Node 2 does not re-send it."""
        url = f"{self._base_url}/api/v1/items/{item_id}/ack"
        logger.debug("Acknowledging item %s at %s", item_id, url)
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url)
            response.raise_for_status()
            logger.debug("Acknowledged item %s", item_id)

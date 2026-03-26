"""
Node 3 Connector – J1900 Edge Server (n8n Action Dispatcher)

Node 3 runs n8n and exposes Webhook endpoints that trigger
downstream automations (notifications, database writes, physical
actuators, etc.).  The orchestrator calls this connector to deliver
"Action" commands after the Local LLM has finished its analysis.

Environment variables (from config/.env):
    NODE3_HOST             – virtual hostname of the J1900 node
    NODE3_N8N_PORT         – n8n HTTP port (default 5678)
    NODE3_N8N_WEBHOOK_PATH – webhook path registered in n8n
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class Node3Connector:
    """Sends LLM-derived Action commands to n8n on Node 3 (J1900)."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        webhook_path: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._host = host or os.environ["NODE3_HOST"]
        self._port = int(port or os.environ.get("NODE3_N8N_PORT", "5678"))
        self._webhook_path = webhook_path or os.environ.get(
            "NODE3_N8N_WEBHOOK_PATH", "/webhook/citta-action"
        )
        self._timeout = timeout
        self._base_url = f"http://{self._host}:{self._port}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def webhook_url(self) -> str:
        """Full URL of the n8n action webhook."""
        return f"{self._base_url}{self._webhook_path}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def dispatch_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """POST an action payload to the n8n webhook on Node 3.

        Args:
            action: dict containing at least:
                type      – action type (e.g. "alert", "store", "notify")
                source_id – ID of the originating scrape item
                payload   – arbitrary data for the action handler

        Returns:
            The JSON response from n8n (may be empty ``{}``)
        """
        logger.info(
            "Dispatching action '%s' (source_id=%s) to Node 3 webhook %s",
            action.get("type"),
            action.get("source_id"),
            self.webhook_url,
        )
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(self.webhook_url, json=action)
            response.raise_for_status()
            result: dict[str, Any] = response.json() if response.content else {}
            logger.debug("Node 3 webhook response: %s", result)
            return result

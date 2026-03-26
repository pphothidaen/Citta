"""
Local LLM Interface – Ollama on Mac M4

Communicates with the Ollama API running natively on macOS.
Provides:
    - text generation (``generate``)
    - embedding generation (``embed``) for ChromaDB ingestion

Environment variables (from config/.env):
    LOCAL_LLM_HOST  – Ollama host (default: host.docker.internal)
    LOCAL_LLM_PORT  – Ollama port (default: 11434)
    LOCAL_LLM_MODEL – model name (default: llama3)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """Thin wrapper around the Ollama HTTP API for Mac M4."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        _host = host or os.environ.get("LOCAL_LLM_HOST", "host.docker.internal")
        _port = int(port or os.environ.get("LOCAL_LLM_PORT", "11434"))
        self._model = model or os.environ.get("LOCAL_LLM_MODEL", "llama3")
        self._timeout = timeout
        self._base_url = f"http://{_host}:{_port}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=30),
        reraise=True,
    )
    def generate(
        self,
        prompt: str,
        system: str | None = None,
        context: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate a text completion using the local Ollama model.

        Args:
            prompt:      User prompt / instruction.
            system:      Optional system message (roles, persona, constraints).
            context:     Optional prior conversation messages for multi-turn.
            temperature: Sampling temperature (lower = more deterministic).

        Returns:
            Generated text as a plain string.
        """
        payload: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system
        if context:
            payload["context"] = context

        url = f"{self._base_url}/api/generate"
        logger.debug("Sending generate request to %s (model=%s)", url, self._model)
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result: str = response.json()["response"]
            logger.debug("LLM response length: %d chars", len(result))
            return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for *text* using the local model.

        Args:
            text: The text to embed.

        Returns:
            Embedding as a list of floats.
        """
        payload = {"model": self._model, "prompt": text}
        url = f"{self._base_url}/api/embeddings"
        logger.debug("Requesting embedding from %s (model=%s)", url, self._model)
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            embedding: list[float] = response.json()["embedding"]
            logger.debug("Embedding dimension: %d", len(embedding))
            return embedding

    def analyze_and_decide(
        self,
        item: dict[str, Any],
        memory_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Higher-level helper: analyze a scraped item and return an Action dict.

        Builds a structured prompt, calls ``generate``, and parses the output
        into an action dict for Node3Connector to dispatch.

        Args:
            item:           Scraped data item (id, source, content, …).
            memory_context: Relevant documents retrieved from ChromaDB (RAG).

        Returns:
            Action dict with keys: ``type``, ``source_id``, ``payload``.
        """
        context_block = ""
        if memory_context:
            excerpts = "\n".join(
                f"- [{h['id']}] {h['document'][:200]}" for h in memory_context
            )
            context_block = f"\n\nRelevant memory:\n{excerpts}"

        system_prompt = (
            "You are Citta, a privacy-first AI orchestrator. "
            "Analyze the provided data item and decide what action to take. "
            "Respond ONLY with a JSON object with keys: "
            "\"type\" (string), \"reason\" (string), \"payload\" (object). "
            "Valid action types: alert | store | summarize | ignore."
        )
        user_prompt = (
            f"Item ID: {item.get('id')}\n"
            f"Source: {item.get('source')}\n"
            f"Content:\n{str(item.get('content', ''))[:1000]}"
            f"{context_block}"
        )

        import json  # noqa: PLC0415

        raw = self.generate(prompt=user_prompt, system=system_prompt)
        try:
            decision: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON output; defaulting to 'store' action")
            decision = {"type": "store", "reason": raw[:200], "payload": {}}

        return {
            "type": decision.get("type", "store"),
            "source_id": item.get("id"),
            "payload": decision.get("payload", {}),
            "reason": decision.get("reason", ""),
        }

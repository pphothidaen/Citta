"""
Unit tests for the Citta orchestrator.

These tests use only the standard library (unittest + unittest.mock)
so no extra test dependencies are required.
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch


# ──────────────────────────────────────────────────────────────────────
# Node4Connector
# ──────────────────────────────────────────────────────────────────────

class TestNode4Connector(unittest.TestCase):
    """Tests for orchestrator.connectors.node4_connector.Node4Connector."""

    def _make_connector(self, items: list | None = None):
        """Return a Node4Connector with httpx.Client patched."""
        from orchestrator.connectors.node4_connector import Node4Connector

        mock_response = MagicMock()
        mock_response.json.return_value = items or []
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"ok"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client.post.return_value = mock_response

        with patch("orchestrator.connectors.node4_connector.httpx.Client", return_value=mock_client):
            connector = Node4Connector(host="node2.test", port=8080)
        connector._mock_client = mock_client
        connector._mock_response = mock_response
        return connector

    def test_fetch_pending_items_returns_list(self):
        items = [{"id": "abc", "source": "http://x", "content": "hello", "captured_at": "2024-01-01T00:00:00Z"}]
        connector = self._make_connector(items=items)

        with patch("orchestrator.connectors.node4_connector.httpx.Client", return_value=connector._mock_client):
            result = connector.fetch_pending_items()

        self.assertEqual(result, items)

    def test_fetch_pending_items_returns_empty_list(self):
        connector = self._make_connector(items=[])
        with patch("orchestrator.connectors.node4_connector.httpx.Client", return_value=connector._mock_client):
            result = connector.fetch_pending_items()
        self.assertEqual(result, [])

    def test_acknowledge_item_calls_post(self):
        connector = self._make_connector()
        with patch("orchestrator.connectors.node4_connector.httpx.Client", return_value=connector._mock_client):
            connector.acknowledge_item("abc")
        connector._mock_client.post.assert_called_once()
        call_url = connector._mock_client.post.call_args[0][0]
        self.assertIn("abc", call_url)
        self.assertIn("ack", call_url)

    def test_base_url_uses_virtual_hostname(self):
        from orchestrator.connectors.node4_connector import Node4Connector
        c = Node4Connector.__new__(Node4Connector)
        c._host = "node2.citta.local"
        c._port = 9999
        c._timeout = 30.0
        c._base_url = f"http://{c._host}:{c._port}"
        self.assertEqual(c._base_url, "http://node2.citta.local:9999")


# ──────────────────────────────────────────────────────────────────────
# Node3Connector
# ──────────────────────────────────────────────────────────────────────

class TestNode3Connector(unittest.TestCase):
    """Tests for orchestrator.connectors.node3_connector.Node3Connector."""

    def _make_connector(self, response_json: dict | None = None):
        from orchestrator.connectors.node3_connector import Node3Connector

        mock_response = MagicMock()
        mock_response.json.return_value = response_json or {}
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"ok"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response

        with patch("orchestrator.connectors.node3_connector.httpx.Client", return_value=mock_client):
            connector = Node3Connector(
                host="node3.test",
                port=5678,
                webhook_path="/webhook/citta-action",
            )
        connector._mock_client = mock_client
        return connector

    def test_webhook_url_built_correctly(self):
        connector = self._make_connector()
        self.assertEqual(connector.webhook_url, "http://node3.test:5678/webhook/citta-action")

    def test_dispatch_action_posts_json(self):
        connector = self._make_connector()
        action = {"type": "alert", "source_id": "item-1", "payload": {"msg": "test"}}
        with patch("orchestrator.connectors.node3_connector.httpx.Client", return_value=connector._mock_client):
            connector.dispatch_action(action)
        connector._mock_client.post.assert_called_once()
        call_kwargs = connector._mock_client.post.call_args[1]
        self.assertEqual(call_kwargs["json"], action)

    def test_dispatch_action_returns_response_json(self):
        connector = self._make_connector(response_json={"status": "ok"})
        action = {"type": "store", "source_id": "item-2", "payload": {}}
        with patch("orchestrator.connectors.node3_connector.httpx.Client", return_value=connector._mock_client):
            result = connector.dispatch_action(action)
        self.assertEqual(result, {"status": "ok"})


# ──────────────────────────────────────────────────────────────────────
# LocalLLMClient
# ──────────────────────────────────────────────────────────────────────

class TestLocalLLMClient(unittest.TestCase):
    """Tests for orchestrator.llm.local_llm.LocalLLMClient."""

    def _make_client(self, generate_text: str = '{"type":"store","reason":"ok","payload":{}}', embedding: list | None = None):
        from orchestrator.llm.local_llm import LocalLLMClient

        mock_gen_response = MagicMock()
        mock_gen_response.json.return_value = {"response": generate_text}
        mock_gen_response.raise_for_status.return_value = None

        mock_emb_response = MagicMock()
        mock_emb_response.json.return_value = {"embedding": embedding or [0.1, 0.2, 0.3]}
        mock_emb_response.raise_for_status.return_value = None

        def post_side_effect(url, **kwargs):
            if "embeddings" in url:
                return mock_emb_response
            return mock_gen_response

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = post_side_effect

        with patch("orchestrator.llm.local_llm.httpx.Client", return_value=mock_client):
            client = LocalLLMClient(host="localhost", port=11434, model="llama3")
        client._mock_client = mock_client
        return client

    def test_generate_returns_string(self):
        client = self._make_client(generate_text="hello world")
        with patch("orchestrator.llm.local_llm.httpx.Client", return_value=client._mock_client):
            result = client.generate("test prompt")
        self.assertEqual(result, "hello world")

    def test_embed_returns_list_of_floats(self):
        client = self._make_client(embedding=[0.1, 0.2, 0.3])
        with patch("orchestrator.llm.local_llm.httpx.Client", return_value=client._mock_client):
            result = client.embed("some text")
        self.assertEqual(result, [0.1, 0.2, 0.3])

    def test_analyze_and_decide_parses_json(self):
        payload = json.dumps({"type": "alert", "reason": "anomaly detected", "payload": {"score": 0.9}})
        client = self._make_client(generate_text=payload, embedding=[0.1, 0.2])
        item = {"id": "item-42", "source": "http://test.com", "content": "some content"}

        with patch("orchestrator.llm.local_llm.httpx.Client", return_value=client._mock_client):
            action = client.analyze_and_decide(item)

        self.assertEqual(action["type"], "alert")
        self.assertEqual(action["source_id"], "item-42")
        self.assertIn("score", action["payload"])

    def test_analyze_and_decide_handles_non_json_gracefully(self):
        client = self._make_client(generate_text="This is not JSON at all.", embedding=[0.0])
        item = {"id": "item-99", "source": "http://x.com", "content": "data"}

        with patch("orchestrator.llm.local_llm.httpx.Client", return_value=client._mock_client):
            action = client.analyze_and_decide(item)

        self.assertEqual(action["type"], "store")
        self.assertEqual(action["source_id"], "item-99")


# ──────────────────────────────────────────────────────────────────────
# Orchestrator main – run_once
# ──────────────────────────────────────────────────────────────────────

class TestRunOnce(unittest.TestCase):
    """Tests for orchestrator.main.run_once."""

    def _make_mocks(self, items: list | None = None):
        node4 = MagicMock()
        node4.fetch_pending_items.return_value = items or []
        node3 = MagicMock()
        minio = MagicMock()
        chroma = MagicMock()
        chroma.query.return_value = []
        llm = MagicMock()
        llm.embed.return_value = [0.1, 0.2, 0.3]
        llm.analyze_and_decide.return_value = {
            "type": "store",
            "source_id": "item-1",
            "payload": {},
            "reason": "test",
        }
        return node4, node3, minio, chroma, llm

    def test_run_once_no_items_returns_zero(self):
        from orchestrator.main import run_once
        node4, node3, minio, chroma, llm = self._make_mocks(items=[])
        result = run_once(node4, node3, minio, chroma, llm)
        self.assertEqual(result, 0)
        node4.fetch_pending_items.assert_called_once()

    def test_run_once_processes_all_items(self):
        from orchestrator.main import run_once
        items = [
            {"id": "a", "source": "http://x.com", "content": "hello", "captured_at": "2024-01-01T00:00:00Z"},
            {"id": "b", "source": "http://y.com", "content": "world", "captured_at": "2024-01-02T00:00:00Z"},
        ]
        node4, node3, minio, chroma, llm = self._make_mocks(items=items)
        result = run_once(node4, node3, minio, chroma, llm)
        self.assertEqual(result, 2)
        self.assertEqual(node4.acknowledge_item.call_count, 2)
        self.assertEqual(minio.put_json.call_count, 2)

    def test_run_once_skips_failed_item_and_continues(self):
        from orchestrator.main import run_once
        items = [
            {"id": "a", "source": "http://x.com", "content": "good", "captured_at": "2024-01-01T00:00:00Z"},
            {"id": "b", "source": "http://y.com", "content": "bad", "captured_at": "2024-01-02T00:00:00Z"},
        ]
        node4, node3, minio, chroma, llm = self._make_mocks(items=items)
        # Make item "b" raise an error at the minio stage
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise RuntimeError("simulated failure")

        minio.put_json.side_effect = side_effect
        result = run_once(node4, node3, minio, chroma, llm)
        # item "a" processed successfully, item "b" failed → 1 processed
        self.assertEqual(result, 1)

    def test_run_once_does_not_dispatch_ignore_actions(self):
        from orchestrator.main import run_once
        items = [{"id": "c", "source": "http://z.com", "content": "noise", "captured_at": "2024-01-01T00:00:00Z"}]
        node4, node3, minio, chroma, llm = self._make_mocks(items=items)
        llm.analyze_and_decide.return_value = {
            "type": "ignore",
            "source_id": "c",
            "payload": {},
            "reason": "irrelevant",
        }
        run_once(node4, node3, minio, chroma, llm)
        node3.dispatch_action.assert_not_called()


if __name__ == "__main__":
    unittest.main()

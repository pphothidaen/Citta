"""
MinIO Storage Client

Wraps the official ``minio`` Python SDK to provide a thin, Citta-specific
interface for uploading raw scraper payloads (unstructured data) to the
MinIO object store.

Environment variables (from config/.env):
    MINIO_HOST            – virtual hostname (Phase 1: "minio", Phase 2: NAS hostname)
    MINIO_API_PORT        – S3 API port (default 9000)
    MINIO_ROOT_USER       – access key
    MINIO_ROOT_PASSWORD   – secret key
    MINIO_DEFAULT_BUCKET  – default bucket name
"""

from __future__ import annotations

import io
import json
import logging
import os
from typing import Any

from minio import Minio
from minio.error import S3Error
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class MinioStorageClient:
    """Upload and retrieve objects from MinIO."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        secure: bool = False,
    ) -> None:
        _host = host or os.environ["MINIO_HOST"]
        _port = int(port or os.environ.get("MINIO_API_PORT", "9000"))
        self._endpoint = f"{_host}:{_port}"
        self._bucket = bucket or os.environ.get("MINIO_DEFAULT_BUCKET", "citta-raw")
        self._client = Minio(
            self._endpoint,
            access_key=access_key or os.environ["MINIO_ROOT_USER"],
            secret_key=secret_key or os.environ["MINIO_ROOT_PASSWORD"],
            secure=secure,
        )
        self._ensure_bucket()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_bucket(self) -> None:
        """Create the default bucket if it does not exist yet."""
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)
            logger.info("Created MinIO bucket '%s'", self._bucket)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def put_json(self, object_name: str, data: dict[str, Any]) -> str:
        """Serialize *data* as JSON and store it in MinIO.

        Args:
            object_name: S3 key path (e.g. ``"2024/01/01/item-abc.json"``)
            data: Python dict to serialize

        Returns:
            The object name (key) that was written.
        """
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        stream = io.BytesIO(payload)
        self._client.put_object(
            self._bucket,
            object_name,
            stream,
            length=len(payload),
            content_type="application/json",
        )
        logger.info(
            "Stored object '%s' (%d bytes) in bucket '%s'",
            object_name,
            len(payload),
            self._bucket,
        )
        return object_name

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get_json(self, object_name: str) -> dict[str, Any]:
        """Retrieve and deserialize a JSON object from MinIO.

        Args:
            object_name: S3 key path

        Returns:
            Deserialized Python dict.

        Raises:
            S3Error: if the object does not exist or cannot be read.
        """
        response = self._client.get_object(self._bucket, object_name)
        try:
            data: dict[str, Any] = json.loads(response.read())
        finally:
            response.close()
            response.release_conn()
        logger.debug("Retrieved object '%s' from bucket '%s'", object_name, self._bucket)
        return data

    def object_url(self, object_name: str) -> str:
        """Return the internal (virtual-hostname) URL for an object."""
        return f"http://{self._endpoint}/{self._bucket}/{object_name}"

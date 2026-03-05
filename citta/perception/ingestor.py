"""Perception layer — data ingestion into ChromaDB and MinIO.

Responsibilities
----------------
* Upload raw documents/artifacts to MinIO (S3-compatible data lake).
* Embed and upsert text chunks into ChromaDB (vector memory).
* Return a ChromaDB retriever ready for the Thinking layer.
"""
import logging
from typing import List

import boto3
from botocore.exceptions import ClientError
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

from config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MinIO helpers
# ---------------------------------------------------------------------------

def _s3_client() -> boto3.client:
    return boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT_URL,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
    )


def ensure_bucket() -> None:
    """Create the MinIO bucket if it does not exist."""
    client = _s3_client()
    try:
        client.head_bucket(Bucket=settings.MINIO_BUCKET)
        logger.debug("Bucket '%s' already exists.", settings.MINIO_BUCKET)
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=settings.MINIO_BUCKET)
            logger.info("Created bucket '%s'.", settings.MINIO_BUCKET)
        else:
            raise


def upload_file(local_path: str, object_key: str) -> str:
    """Upload a file to MinIO and return the S3 URI."""
    ensure_bucket()
    _s3_client().upload_file(local_path, settings.MINIO_BUCKET, object_key)
    uri = f"s3://{settings.MINIO_BUCKET}/{object_key}"
    logger.info("Uploaded %s → %s", local_path, uri)
    return uri


# ---------------------------------------------------------------------------
# ChromaDB helpers
# ---------------------------------------------------------------------------

def _chroma_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )


def get_vector_store() -> Chroma:
    """Return a LangChain Chroma vector store backed by the running container."""
    embeddings = OllamaEmbeddings(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.LLM_MODEL,
    )
    return Chroma(
        client=_chroma_client(),
        collection_name=settings.CHROMA_COLLECTION,
        embedding_function=embeddings,
    )


def ingest_texts(texts: List[str], metadata_list: List[dict] | None = None) -> None:
    """Embed and upsert a list of text chunks into ChromaDB."""
    store = get_vector_store()
    store.add_texts(texts=texts, metadatas=metadata_list or [{}] * len(texts))
    logger.info("Ingested %d chunks into collection '%s'.",
                len(texts), settings.CHROMA_COLLECTION)

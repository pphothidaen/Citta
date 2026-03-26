"""Central configuration — reads from environment / .env file.

All hostnames are env-driven so Phase 2 migration (Node 1 → Node 2/3)
requires only an .env update, not code changes.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- MinIO ---
MINIO_HOST: str = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT: int = int(os.getenv("MINIO_PORT", "9000"))
MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "cittaadmin")
MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "cittasecret")
MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "citta-lake")
MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"

MINIO_ENDPOINT_URL: str = (
    f"{'https' if MINIO_SECURE else 'http'}://{MINIO_HOST}:{MINIO_PORT}"
)

# --- ChromaDB ---
CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "citta-memory")

# --- LLM (Ollama) ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")

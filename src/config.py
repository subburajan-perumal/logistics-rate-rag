import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "sample_docs"
PERSIST_DIR = PROJECT_ROOT / "chroma_db"

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# text-embedding-004 was shut down by Google on 2026-01-14; the 2.5 family
# returns 404 for keys created after mid-2026 (verified 2026-09-17).
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768
CHAT_MODEL = "gemini-3.6-flash"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
RETRIEVAL_K = 4


def require_api_key() -> str:
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Copy .env.example to .env and add your "
            "own key from https://aistudio.google.com/apikey"
        )
    return GOOGLE_API_KEY

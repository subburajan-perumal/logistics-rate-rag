"""Vector stores, lexical index and retriever (docs/SPEC.md §4)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings

    from logistics_rate_rag.config import Settings
    from logistics_rate_rag.store.base import StoreBackend


def build_backend(
    settings: Settings, store: str, embedder: Embeddings, *, enriched: bool = False
) -> StoreBackend:
    """`store` -> backend for the current corpus version (SPEC.md §4.3/§4.4).
    `enriched` selects the separate D-34 collection/namespace."""
    version = settings.manifest.corpus_version
    suffix = "_enriched" if enriched else ""
    if store == "chroma":
        from logistics_rate_rag.store.chroma_backend import ChromaBackend

        return ChromaBackend(
            settings.project_root / ".chroma", f"rates_v{version}{suffix}", embedder
        )
    if store == "pinecone":
        from logistics_rate_rag.store.pinecone_backend import PineconeBackend

        return PineconeBackend(
            settings.pinecone_api_key,
            settings.pinecone_index,
            f"corpus-v{version}{suffix.replace('_', '-')}",
            settings.embedding_dim,
        )
    raise ValueError(f"unknown store: {store}")

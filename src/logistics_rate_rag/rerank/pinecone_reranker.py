"""Managed reranker via Pinecone Inference (docs/SPEC.md §4.8, D-28).

Needs PINECONE_API_KEY even when the vector store is Chroma.
"""

from __future__ import annotations

from collections.abc import Sequence

from logistics_rate_rag.errors import MissingCredential
from logistics_rate_rag.ingest.models import Chunk


class PineconeReranker:
    name = "pinecone"

    def __init__(self, api_key: str | None, model: str = "bge-reranker-v2-m3") -> None:
        if not api_key:
            raise MissingCredential("PINECONE_API_KEY")
        from pinecone import Pinecone

        self._pc = Pinecone(api_key=api_key)
        self._model = model

    def rerank(
        self, query: str, chunks: Sequence[Chunk], top_n: int
    ) -> list[tuple[Chunk, float | None]]:
        if not chunks:
            return []
        result = self._pc.inference.rerank(
            model=self._model,
            query=query,
            documents=[{"id": c.chunk_id, "text": c.text} for c in chunks],
            rank_fields=["text"],
            top_n=top_n,
            return_documents=False,
        )
        return [(chunks[r.index], float(r.score)) for r in result.data]

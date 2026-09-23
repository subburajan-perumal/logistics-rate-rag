"""Gemini embedder (docs/SPEC.md §4.2, D-01, D-26)."""

from __future__ import annotations

import math

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from logistics_rate_rag.errors import EmbeddingError, MissingCredential


def _normalize(v: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in v))
    if norm == 0.0:
        raise EmbeddingError("embedding vector has zero norm")
    return [x / norm for x in v]


class GeminiEmbedder(Embeddings):
    def __init__(self, model: str, dim: int, api_key: str | None) -> None:
        if not api_key:
            raise MissingCredential("GOOGLE_API_KEY")
        self._dim = dim
        self._impl = GoogleGenerativeAIEmbeddings(
            model=model, output_dimensionality=dim, google_api_key=api_key
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), 100):
            batch = texts[i : i + 100]
            vectors = self._impl.embed_documents(batch)
            out.extend(self._check_and_normalize(v) for v in vectors)
        return out

    def embed_query(self, text: str) -> list[float]:
        return self._check_and_normalize(self._impl.embed_query(text))

    def _check_and_normalize(self, v: list[float]) -> list[float]:
        if len(v) != self._dim:
            from logistics_rate_rag.errors import DimensionMismatch

            raise DimensionMismatch(self._dim, len(v))
        return _normalize(v)

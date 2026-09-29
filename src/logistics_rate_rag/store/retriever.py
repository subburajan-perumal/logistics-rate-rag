"""Retriever (docs/SPEC.md §4.6).

Dense top-k from the store, optionally fused with a BM25 leg via RRF
(`RETRIEVAL_MODE=hybrid`, D-33), then cut to `k_final` by a reranker
(`RERANKER=flashrank|pinecone|none`, D-28). `build_retriever` is the one
place that turns settings into a retriever, so `ask`, `eval`, `recall`
and threshold tuning can't drift apart.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever

from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.base import Hit, StoreBackend

if TYPE_CHECKING:
    from logistics_rate_rag.config import Settings

# `lexical` and `reranker` are typed `Any` so this module imports without
# rank_bm25/flashrank installed (the Streamlit demo runs dense-only):
# pydantic, which BaseRetriever is built on, resolves field annotations
# eagerly, so a TYPE_CHECKING-only import would fail at class creation.


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk: Chunk
    rank: int
    similarity_norm: float
    vector_rank: int | None
    bm25_score: float | None
    lexical_rank: int | None
    rrf_score: float | None
    rerank_score: float | None


class RateRetriever(BaseRetriever):
    model_config: ClassVar[dict] = {"arbitrary_types_allowed": True}

    backend: StoreBackend
    embedder: Embeddings
    lexical: Any = None
    reranker: Any = None
    k_retrieve: int
    k_final: int
    rrf_k: int = 60

    def retrieve(self, question: str, filter: dict | None) -> list[RetrievedChunk]:
        qv = self.embedder.embed_query(question)
        dense: list[Hit] = self.backend.query(qv, self.k_retrieve, filter)

        if self.lexical is not None:
            from logistics_rate_rag.store.lexical import fuse_rrf

            lex = self.lexical.query(question, self.k_retrieve)
            if filter:
                lex = [
                    (chunk, score, rank)
                    for chunk, score, rank in lex
                    if chunk.metadata.get("carrier") in (filter["carrier"], "ALL")
                ]
            fused = fuse_rrf(dense, lex, self.rrf_k)[: self.k_retrieve]
        else:
            fused = [
                _FusedHit(
                    chunk=h.chunk,
                    similarity_norm=h.similarity_norm,
                    vector_rank=h.vector_rank,
                    bm25_score=None,
                    lexical_rank=None,
                    rrf_score=None,
                )
                for h in dense
            ]

        min_sim = min((h.similarity_norm for h in dense), default=0.5)
        chunks_for_rerank = [f.chunk for f in fused]
        if self.reranker is not None:
            reranked = self.reranker.rerank(question, chunks_for_rerank, top_n=self.k_final)
        else:
            reranked = [(c, None) for c in chunks_for_rerank[: self.k_final]]

        by_chunk_id = {f.chunk.chunk_id: f for f in fused}
        retrieved: list[RetrievedChunk] = []
        for rank, (chunk, rerank_score) in enumerate(reranked, start=1):
            f = by_chunk_id[chunk.chunk_id]
            similarity_norm = f.similarity_norm if f.similarity_norm is not None else min_sim
            retrieved.append(
                RetrievedChunk(
                    chunk=chunk,
                    rank=rank,
                    similarity_norm=similarity_norm,
                    vector_rank=f.vector_rank,
                    bm25_score=f.bm25_score,
                    lexical_rank=f.lexical_rank,
                    rrf_score=f.rrf_score,
                    rerank_score=rerank_score,
                )
            )
        return retrieved

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun, filter: dict | None = None
    ) -> list[Document]:
        docs = []
        for rc in self.retrieve(query, filter):
            docs.append(
                Document(
                    page_content=rc.chunk.text,
                    metadata={
                        **rc.chunk.metadata,
                        "rank": rc.rank,
                        "similarity_norm": rc.similarity_norm,
                        "vector_rank": rc.vector_rank if rc.vector_rank is not None else -1,
                        "bm25_score": rc.bm25_score if rc.bm25_score is not None else -1.0,
                        "lexical_rank": rc.lexical_rank if rc.lexical_rank is not None else -1,
                        "rrf_score": rc.rrf_score if rc.rrf_score is not None else -1.0,
                        "rerank_score": rc.rerank_score if rc.rerank_score is not None else -1.0,
                    },
                )
            )
        return docs


@dataclass(frozen=True, slots=True)
class _FusedHit:
    chunk: Chunk
    similarity_norm: float | None
    vector_rank: int | None
    bm25_score: float | None
    lexical_rank: int | None
    rrf_score: float | None


def build_retriever(
    settings: Settings,
    backend: StoreBackend,
    embedder: Embeddings,
    all_chunks: Sequence[Chunk],
    *,
    retrieval_mode: str | None = None,
    reranker: str | None = None,
) -> RateRetriever:
    """Settings -> retriever. `retrieval_mode`/`reranker` override settings."""
    from logistics_rate_rag.rerank import build_reranker

    mode = retrieval_mode or settings.retrieval_mode
    lexical = None
    if mode == "hybrid":
        from logistics_rate_rag.store.lexical import LexicalIndex

        lexical = LexicalIndex(all_chunks)
    return RateRetriever(
        backend=backend,
        embedder=embedder,
        lexical=lexical,
        reranker=build_reranker(
            reranker or settings.reranker,
            model_name=settings.rerank_model,
            cache_dir=settings.flashrank_cache_dir,
            pinecone_api_key=settings.pinecone_api_key,
        ),
        k_retrieve=settings.retrieval.k_retrieve,
        k_final=settings.retrieval.k_final,
        rrf_k=settings.retrieval.rrf_k,
    )

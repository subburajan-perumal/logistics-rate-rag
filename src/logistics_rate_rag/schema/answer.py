"""Verdict / RateAnswer models (docs/SPEC.md §6.1)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any, Literal

from logistics_rate_rag.schema.candidate import RateCandidate
from logistics_rate_rag.schema.outcome import Outcome

if TYPE_CHECKING:
    # Deferred: schema/ may not import chain/ at runtime (import-purity
    # rule, SPEC.md §1) — this is a type hint only.
    from logistics_rate_rag.chain.usage import Usage


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    gate: str
    reason: str | None
    details: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SourceRef:
    source_doc: str
    chunk_id: str
    span: str | None
    role: Literal["rate", "policy", "nearest"]


@dataclass(frozen=True, slots=True)
class Verdict:
    outcome: Outcome
    reason: str | None
    gate_results: tuple[GateResult, ...]
    confidence_score: float | None
    candidate: RateCandidate | None
    sources: tuple[SourceRef, ...]


@dataclass(frozen=True, slots=True)
class RateAnswer:
    outcome: Outcome
    reason: str | None
    carrier: str | None
    origin: str | None
    destination: str | None
    container_type: str | None
    rate_value: int | None
    currency: str | None
    valid_from: date | None
    valid_to: date | None
    includes_surcharge: bool | None
    sources: tuple[SourceRef, ...]
    confidence_score: float | None
    similarity_norm: float | None
    rank: int | None
    rerank_score: float | None
    store: str
    retrieval_mode: str
    reranker: str
    latency_ms: int
    cache_hit: bool
    usage: Usage

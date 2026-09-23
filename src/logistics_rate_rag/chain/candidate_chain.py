"""The only LLM-touching code (docs/SPEC.md §5.4, D-03, D-25)."""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from langchain_google_genai import ChatGoogleGenerativeAI

from logistics_rate_rag.chain.cache import ResponseCache
from logistics_rate_rag.chain.context import order_for_context, pin_global, render_context
from logistics_rate_rag.chain.planner import QueryPlan, QueryPlanner
from logistics_rate_rag.chain.prompt import PROMPT_VERSION, build_prompt
from logistics_rate_rag.chain.ratelimit import RateLimiter
from logistics_rate_rag.chain.usage import Usage
from logistics_rate_rag.config import Settings
from logistics_rate_rag.errors import LLMError, MissingCredential
from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.schema.candidate import RateCandidate
from logistics_rate_rag.store.retriever import RateRetriever, RetrievedChunk


@dataclass(frozen=True, slots=True)
class CandidateResult:
    candidate: RateCandidate | None
    parsing_error: str | None
    raw_text: str
    retrieved: tuple[RetrievedChunk, ...]
    pinned: tuple[Chunk, ...]
    plan: QueryPlan
    usage: Usage
    latency_ms: int
    cache_hit: bool
    prompt_version: str
    model: str


class CandidateChain:
    def __init__(
        self,
        settings: Settings,
        retriever: RateRetriever,
        all_chunks: Sequence[Chunk],
        cache: ResponseCache | None,
        limiter: RateLimiter,
    ) -> None:
        self._settings = settings
        self._retriever = retriever
        self._all_chunks = all_chunks
        self._cache = cache
        self._limiter = limiter
        self._planner = QueryPlanner(settings.carriers, settings.guardrails.surcharge_keywords)
        self._prompt = build_prompt()

    def run(self, question: str, as_of: date) -> CandidateResult:
        start = time.perf_counter()
        plan = self._planner.plan(question, as_of)

        retrieved = self._retriever.retrieve(plan.question, plan.filter)
        pinned = pin_global(retrieved, self._all_chunks, self._settings.retrieval)
        context = render_context(order_for_context(retrieved), pinned)

        model = self._settings.chat_model
        cache_key = None
        if self._cache is not None:
            cache_key = self._cache.key(
                model, PROMPT_VERSION, question, plan.as_of, retrieved, pinned
            )
            cached = self._cache.get(cache_key)
            if cached is not None:
                candidate = (
                    RateCandidate.model_validate(cached["parsed"]) if cached["parsed"] else None
                )
                latency_ms = int((time.perf_counter() - start) * 1000)
                return CandidateResult(
                    candidate=candidate,
                    parsing_error=cached["parsing_error"],
                    raw_text=cached["raw_text"],
                    retrieved=tuple(retrieved),
                    pinned=tuple(pinned),
                    plan=plan,
                    usage=Usage.make_cached(model),
                    latency_ms=latency_ms,
                    cache_hit=True,
                    prompt_version=PROMPT_VERSION,
                    model=model,
                )

        if not self._settings.google_api_key:
            raise MissingCredential("GOOGLE_API_KEY")

        from google.genai.errors import ClientError

        attempt = 0
        while True:
            self._limiter.wait()
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model,
                    thinking_level=self._settings.llm_thinking_level,
                    seed=self._settings.llm_seed,
                    max_retries=3,
                    timeout=60,
                    google_api_key=self._settings.google_api_key,
                )
                structured = llm.with_structured_output(
                    RateCandidate, method="json_schema", include_raw=True
                )
                out = (self._prompt | structured).invoke(
                    {"as_of": plan.as_of.isoformat(), "context": context, "question": question}
                )
                break
            except ClientError as e:
                if getattr(e, "code", None) == 429 and attempt < 3:
                    self._limiter.backoff(attempt)
                    attempt += 1
                    continue
                raise LLMError(str(e)) from e

        raw_msg = out["raw"]
        raw_text = raw_msg.text if raw_msg is not None else ""
        parsed: RateCandidate | None = out.get("parsed")
        parsing_error = str(out["parsing_error"]) if out.get("parsing_error") else None
        usage = Usage.from_message(raw_msg, model)
        latency_ms = int((time.perf_counter() - start) * 1000)

        if self._cache is not None and cache_key is not None:
            self._cache.put(
                cache_key,
                {
                    "model": model,
                    "prompt_version": PROMPT_VERSION,
                    "question": question,
                    "as_of": plan.as_of.isoformat(),
                    "chunk_ids": [rc.chunk.chunk_id for rc in retrieved],
                    "parsed": parsed.model_dump(mode="json") if parsed else None,
                    "parsing_error": parsing_error,
                    "raw_text": raw_text,
                    "usage": {
                        "input_tokens": usage.input_tokens,
                        "output_tokens": usage.output_tokens,
                        "thought_tokens": usage.thought_tokens,
                    },
                },
            )

        return CandidateResult(
            candidate=parsed,
            parsing_error=parsing_error,
            raw_text=raw_text,
            retrieved=tuple(retrieved),
            pinned=tuple(pinned),
            plan=plan,
            usage=usage,
            latency_ms=latency_ms,
            cache_hit=False,
            prompt_version=PROMPT_VERSION,
            model=model,
        )

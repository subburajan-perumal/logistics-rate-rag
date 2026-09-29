"""Optional LLM chunk enrichment (docs/SPEC.md §5.8, D-34). Ablation only.

A ~100-word search description per chunk is prepended to the text that is
embedded and BM25-indexed. The LLM context and Gate 3 grounding keep using
the raw chunk text, so a description can move retrieval but never an
answer's value.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from logistics_rate_rag.chain.usage import Usage
from logistics_rate_rag.errors import LLMError, MissingCredential
from logistics_rate_rag.ingest.models import Chunk

if TYPE_CHECKING:
    from logistics_rate_rag.chain.ratelimit import RateLimiter
    from logistics_rate_rag.config import Settings

ENRICH_PROMPT_VERSION = "1"

ENRICH_PROMPT_V1 = """Write a search description for the freight-tariff text below so that a retrieval system can find it. In about 100 words of plain prose: name the carrier and tariff reference, list every origin and destination port (LOCODE and city) that appears, the container types, the currency, the validity period, and what kind of question this text answers (a rate lookup, a policy rule, remarks). Do not include any rate amounts, surcharge amounts or other numbers except dates and the tariff reference. Do not use bullet points.

Text:
{text}"""  # noqa: E501 - verbatim (SPEC.md §5.8); changing it means bumping the version


def cache_key(model: str, chunk: Chunk) -> str:
    return hashlib.sha256(
        "\n".join([model, ENRICH_PROMPT_VERSION, chunk.content_sha256]).encode("utf-8")
    ).hexdigest()


def leaked_rate_values(description: str, rate_values: Sequence[int]) -> list[int]:
    """Rate values that appear as a whole number (plain or with a thousands
    comma) in a description. The prompt forbids them; this checks it.
    Hyphen-joined digits are dates or tariff refs, which the prompt allows."""
    leaked = []
    for v in rate_values:
        variants = {str(v), f"{v:,}"}
        if any(
            re.search(rf"(?<![\d,.-]){re.escape(x)}(?![\d.-]|,\d)", description) for x in variants
        ):
            leaked.append(v)
    return leaked


def enrich_chunk(
    chunk: Chunk, settings: Settings, cache_dir: Path, limiter: RateLimiter
) -> tuple[str, Usage]:
    model = settings.chat_model
    path = cache_dir / f"{cache_key(model, chunk)}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))["description"], Usage.make_cached(
                model
            )
        except (json.JSONDecodeError, KeyError):
            pass  # corrupt entry: treat as a miss and overwrite

    if not settings.google_api_key:
        raise MissingCredential("GOOGLE_API_KEY")
    from langchain_google_genai import ChatGoogleGenerativeAI

    limiter.wait()
    try:
        llm = ChatGoogleGenerativeAI(
            model=model,
            thinking_level=settings.llm_thinking_level,
            seed=settings.llm_seed,
            max_retries=3,
            timeout=60,
            google_api_key=settings.google_api_key,
        )
        msg = llm.invoke(ENRICH_PROMPT_V1.format(text=chunk.text))
    except Exception as e:  # the SDK raises several transport/client types
        raise LLMError(str(e)) from e

    description = " ".join(msg.text.split())
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "model": model,
                "prompt_version": ENRICH_PROMPT_VERSION,
                "chunk_id": chunk.chunk_id,
                "content_sha256": chunk.content_sha256,
                "description": description,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return description, Usage.from_message(msg, model)


def enrich_chunks(
    chunks: Sequence[Chunk], settings: Settings, limiter: RateLimiter
) -> tuple[list[Chunk], list[Usage]]:
    cache_dir = settings.project_root / ".cache" / "enrich"
    enriched: list[Chunk] = []
    usages: list[Usage] = []
    for c in chunks:
        description, usage = enrich_chunk(c, settings, cache_dir, limiter)
        usages.append(usage)
        enriched.append(
            dataclasses.replace(
                c,
                index_text=f"{description}\n{c.text}",
                metadata={**c.metadata, "description": description},
            )
        )
    return enriched, usages

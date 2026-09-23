"""Token usage and cost accounting (docs/SPEC.md §5.7, D-36)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from logistics_rate_rag.errors import ConfigError

if TYPE_CHECKING:
    from langchain_core.messages import AIMessage

    from logistics_rate_rag.config import Price


@dataclass(frozen=True, slots=True)
class Usage:
    model: str
    input_tokens: int
    output_tokens: int
    thought_tokens: int
    cached: bool

    @classmethod
    def from_message(cls, msg: AIMessage, model: str) -> Usage:
        meta = msg.usage_metadata or {}
        details = meta.get("output_token_details") or {}
        return cls(
            model=model,
            input_tokens=meta.get("input_tokens", 0),
            output_tokens=meta.get("output_tokens", 0),
            thought_tokens=details.get("reasoning", 0),
            cached=False,
        )

    @classmethod
    def make_cached(cls, model: str) -> Usage:
        # Named make_cached, not cached: SPEC.md names both the `cached: bool`
        # field and this classmethod `cached`, which is unusable together on
        # a slots=True dataclass — the slot descriptor for the field clobbers
        # the classmethod at class-creation time. Documented as D-41.
        return cls(model=model, input_tokens=0, output_tokens=0, thought_tokens=0, cached=True)

    def cost_usd(self, prices: dict[str, Price]) -> float:
        price = prices.get(self.model)
        if price is None:
            raise ConfigError(f"no price entry for model {self.model!r} in prices.yaml")
        return (
            self.input_tokens * price.input
            + (self.output_tokens + self.thought_tokens) * price.output
        ) / 1e6


@dataclass(frozen=True, slots=True)
class UsageTotals:
    input_tokens: int
    output_tokens: int
    thought_tokens: int
    live_calls: int
    cache_hits: int


def sum_usage(usages: Iterable[Usage]) -> UsageTotals:
    input_tokens = output_tokens = thought_tokens = live_calls = cache_hits = 0
    for u in usages:
        if u.cached:
            cache_hits += 1
        else:
            live_calls += 1
            input_tokens += u.input_tokens
            output_tokens += u.output_tokens
            thought_tokens += u.thought_tokens
    return UsageTotals(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        thought_tokens=thought_tokens,
        live_calls=live_calls,
        cache_hits=cache_hits,
    )

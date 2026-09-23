"""Query planner (docs/SPEC.md §5.1)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from logistics_rate_rag.config import Carrier

_AS_OF_RE = re.compile(r"\bas of (\d{4}-\d{2}-\d{2})\b", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class QueryPlan:
    question: str
    filter: dict | None
    as_of: date
    mentions_surcharge: bool
    carriers_mentioned: tuple[str, ...]


def _whole_word_present(alias: str, text_lower: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
    return re.search(pattern, text_lower) is not None


class QueryPlanner:
    def __init__(self, carriers: dict[str, Carrier], keywords: Sequence[str]) -> None:
        self._carriers = carriers
        self._keywords = list(keywords)

    def plan(self, question: str, as_of: date) -> QueryPlan:
        text_lower = question.lower()

        carriers_mentioned = tuple(
            code
            for code, carrier in self._carriers.items()
            if any(_whole_word_present(alias, text_lower) for alias in carrier.aliases)
        )
        filter_ = {"carrier": carriers_mentioned[0]} if len(carriers_mentioned) == 1 else None

        resolved_as_of = as_of
        if m := _AS_OF_RE.search(question):
            try:
                resolved_as_of = date.fromisoformat(m[1])
            except ValueError:
                resolved_as_of = as_of

        mentions_surcharge = any(_whole_word_present(kw, text_lower) for kw in self._keywords)

        return QueryPlan(
            question=question,
            filter=filter_,
            as_of=resolved_as_of,
            mentions_surcharge=mentions_surcharge,
            carriers_mentioned=carriers_mentioned,
        )

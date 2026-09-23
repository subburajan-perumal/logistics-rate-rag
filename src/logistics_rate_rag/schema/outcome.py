"""Outcome enum and reject-reason strings (docs/SPEC.md §6.1)."""

from __future__ import annotations

from enum import StrEnum

# RejectReason is a plain str: "parse_error" | "unknown_source" | "unknown_port"
# | "rule:<name>" | "ungrounded:rate_value" | "ungrounded:valid_to" |
# "ungrounded:source_span" — not an enum, since gate2's "rule:<name>" and
# gate3's "ungrounded:<field>" are parameterised.
RejectReason = str


class Outcome(StrEnum):
    ANSWER = "ANSWER"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REFUSED = "REFUSED"
    REJECT = "REJECT"
    ERROR = "ERROR"

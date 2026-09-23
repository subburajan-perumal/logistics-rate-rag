"""LLM candidate output model (docs/SPEC.md §6.1)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class RateCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answerable: bool
    carrier: str | None = None
    origin: str | None = None
    destination: str | None = None
    container_type: Literal["20DRY", "40DRY", "40HC"] | None = None
    rate_value: int | None = None
    currency: Literal["USD", "EUR"] | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    includes_surcharge: bool | None = None
    source_doc: str | None = None
    source_chunk_id: str | None = None
    policy_source_chunk_id: str | None = None
    source_span: str | None = None
    confidence: float = 0.0

    @field_validator("carrier", "origin", "destination", mode="before")
    @classmethod
    def _upper_strip(cls, v: object) -> object:
        return v.strip().upper() if isinstance(v, str) else v

    @field_validator("rate_value", mode="before")
    @classmethod
    def _rate_value_must_be_whole(cls, v: object) -> object:
        if isinstance(v, float):
            if v.is_integer():
                return int(v)
            raise ValueError(f"rate_value must be a whole number, got {v}")
        return v

    @field_validator("rate_value")
    @classmethod
    def _rate_value_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("rate_value must be > 0")
        return v

    @field_validator("confidence")
    @classmethod
    def _confidence_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("confidence must be between 0 and 1")
        return v

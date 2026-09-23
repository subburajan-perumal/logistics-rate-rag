"""Question-set loading (docs/SPEC.md §7.1, docs/CORPUS.md §6.1)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict

from logistics_rate_rag.errors import ConfigError


class Key(BaseModel):
    model_config = ConfigDict(extra="forbid")
    carrier: str
    origin: str
    destination: str
    container_type: str
    tariff_ref: str


class Expected(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outcome: Literal["ANSWER", "NOT_ANSWER"]
    rate_value: int | None = None
    currency: str | None = None
    valid_to: date | None = None
    includes_surcharge: bool | None = None
    source_doc: str | None = None
    policy_source_required: bool | None = None
    must_not_contain: list[int] | None = None


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    tag: str
    question: str
    as_of: date
    key: Key | None = None
    expected: Expected


class QuestionSet(BaseModel):
    version: int
    corpus_version: int
    verified_by: str
    questions: list[Question]


def load_question_set(path: Path, manifest_corpus_version: int) -> QuestionSet:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = raw.get("questions") if "questions" in raw else raw.get("prompts")
    if items is None:
        raise ConfigError(f"{path}: expected a 'questions' or 'prompts' key")

    qs = QuestionSet(
        version=raw["version"],
        corpus_version=raw["corpus_version"],
        verified_by=raw["verified_by"],
        questions=[Question.model_validate(q) for q in items],
    )
    if qs.corpus_version != manifest_corpus_version:
        raise ConfigError(
            f"{path}: corpus_version {qs.corpus_version} != manifest corpus_version "
            f"{manifest_corpus_version}"
        )
    ids = [q.id for q in qs.questions]
    if len(set(ids)) != len(ids):
        raise ConfigError(f"{path}: duplicate question ids")
    if ids != sorted(ids):
        raise ConfigError(f"{path}: question ids not sorted")
    return qs

"""Settings and config-file loading (docs/SPEC.md §2)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from logistics_rate_rag.errors import ConfigError

# --- Pydantic config-file models ---------------------------------------------------


class Carrier(BaseModel):
    model_config = ConfigDict(extra="forbid")
    display_name: str
    aliases: list[str]
    currency: str
    baf_included: bool
    thc_included: bool
    tariff_refs: list[str]


class _CarriersFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    carriers: dict[str, Carrier]


class Ports(BaseModel):
    model_config = ConfigDict(extra="forbid")
    locode: dict[str, str]
    city_lower: dict[str, str]


class Enums(BaseModel):
    model_config = ConfigDict(extra="forbid")
    container_types: list[str]
    currencies: list[str]


class RuleSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    params: dict[str, float] | None = None


class WeightsWithReranker(BaseModel):
    model_config = ConfigDict(extra="forbid")
    w_model: float
    w_sim: float
    w_rerank: float
    w_rank: float


class WeightsWithoutReranker(BaseModel):
    model_config = ConfigDict(extra="forbid")
    w_model: float
    w_sim: float
    w_rank: float


class ConfidenceWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")
    with_reranker: WeightsWithReranker
    without_reranker: WeightsWithoutReranker


class ConfidenceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weights: ConfidenceWeights
    threshold: dict[str, float]
    tuned_on: dict[str, str]


class GuardrailsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rules: list[RuleSpec]
    surcharge_keywords: list[str]
    confidence: ConfidenceConfig


class RetrievalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    k_retrieve: int
    k_final: int
    rrf_k: int
    rows_per_chunk_md: int
    rows_per_chunk_csv: int
    pinned_doc_types: list[str]
    pinned_cap: int


class Price(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input: float
    output: float


class _PricesFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prices_read_on: date
    source: str
    models: dict[str, Price]


class LaneRange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min: int
    max: int
    docs: list[str]


class ManifestDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    carrier: str
    tariff_ref: str
    doc_type: str
    currency: str
    valid_from: date
    valid_to: date
    status: str


class ManifestRate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doc: str
    carrier: str
    tariff_ref: str
    origin: str
    destination: str
    container_type: str
    rate_value: int
    currency: str
    valid_from: date
    valid_to: date
    transit_days: int


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    corpus_version: int
    generated_with_seed: int
    generated_on: date
    files: dict[str, str]
    documents: dict[str, ManifestDocument]
    rates: list[ManifestRate]
    rate_values: list[int]
    lane_ranges: dict[str, LaneRange]


# --- Settings -----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Settings:
    project_root: Path
    google_api_key: str | None
    pinecone_api_key: str | None
    pinecone_index: str
    vector_store: Literal["chroma", "pinecone"]
    retrieval_mode: Literal["hybrid", "dense"]
    reranker: Literal["flashrank", "pinecone", "none"]
    rerank_model: str
    flashrank_cache_dir: Path
    chat_model: str
    embedding_model: str
    embedding_dim: int
    llm_thinking_level: Literal["minimal", "low", "medium", "high"]
    llm_seed: int
    llm_min_interval_s: float
    llm_cache_dir: Path
    enrich_chunks: bool
    gates_enabled: bool
    as_of_default: date
    carriers: dict[str, Carrier]
    ports: Ports
    enums: Enums
    guardrails: GuardrailsConfig
    retrieval: RetrievalConfig
    prices: dict[str, Price]
    rate_ranges: dict[str, LaneRange]
    manifest: Manifest


def find_project_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise ConfigError(f"no pyproject.toml found walking up from {start}")


def _parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in {"true", "1", "yes"}:
        return True
    if v in {"false", "0", "no"}:
        return False
    raise ConfigError(f"cannot parse boolean from {value!r}")


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_settings(env_file: Path | None = None, **overrides: object) -> Settings:
    project_root = find_project_root(Path(__file__).resolve())
    load_dotenv(env_file or project_root / ".env", override=False)

    def env(name: str, default: str) -> str:
        return str(overrides.get(name.lower(), os.environ.get(name, default)))

    config_dir = project_root / "config"
    data_dir = project_root / "data"

    carriers_raw = _load_yaml(config_dir / "carriers.yaml")
    carriers = _CarriersFile.model_validate(carriers_raw).carriers

    ports_raw = _load_yaml(config_dir / "ports.yaml")["ports"]
    ports = Ports(
        locode=dict(ports_raw),
        city_lower={city.lower(): locode for locode, city in ports_raw.items()},
    )

    enums_raw = _load_yaml(config_dir / "enums.yaml")
    enums = Enums.model_validate(enums_raw)

    guardrails_raw = _load_yaml(config_dir / "guardrails.yaml")
    guardrails = GuardrailsConfig.model_validate(guardrails_raw)

    retrieval_raw = _load_yaml(config_dir / "retrieval.yaml")
    retrieval = RetrievalConfig.model_validate(retrieval_raw)

    prices_raw = _load_yaml(config_dir / "prices.yaml")
    prices = _PricesFile.model_validate(prices_raw).models

    import json

    with (config_dir / "rate_ranges.json").open(encoding="utf-8") as f:
        rate_ranges_raw = json.load(f)
    rate_ranges = {k: LaneRange.model_validate(v) for k, v in rate_ranges_raw.items()}

    with (data_dir / "corpus" / "manifest.json").open(encoding="utf-8") as f:
        manifest_raw = json.load(f)
    manifest = Manifest.model_validate(manifest_raw)

    known_rule_names = {
        "carrier_known",
        "rate_in_range",
        "currency_matches_source",
        "dates_ordered",
        "not_expired",
        "surcharge_consistent",
    }
    for rule in guardrails.rules:
        if rule.name not in known_rule_names:
            raise ConfigError(f"unknown guardrail rule in guardrails.yaml: {rule.name}")

    for key, lr in rate_ranges.items():
        for doc in lr.docs:
            if doc not in manifest.documents:
                raise ConfigError(f"rate_ranges.json key {key!r} references unknown doc {doc!r}")

    for mode, weights in (
        ("with_reranker", guardrails.confidence.weights.with_reranker),
        ("without_reranker", guardrails.confidence.weights.without_reranker),
    ):
        total = sum(weights.model_dump().values())
        if abs(total - 1.0) > 1e-9:
            raise ConfigError(f"guardrails.yaml confidence.weights.{mode} sums to {total}, not 1.0")

    if retrieval.k_final > retrieval.k_retrieve:
        raise ConfigError(
            f"retrieval.yaml: k_final ({retrieval.k_final}) must be <= k_retrieve "
            f"({retrieval.k_retrieve})"
        )

    as_of_raw = env("AS_OF_DATE", "")
    as_of_default = date.fromisoformat(as_of_raw) if as_of_raw else date.today()

    return Settings(
        project_root=project_root,
        google_api_key=os.environ.get("GOOGLE_API_KEY") or None,
        pinecone_api_key=os.environ.get("PINECONE_API_KEY") or None,
        pinecone_index=env("PINECONE_INDEX", "logistics-rate-rag"),
        vector_store=env("VECTOR_STORE", "chroma"),  # type: ignore[arg-type]
        retrieval_mode=env("RETRIEVAL_MODE", "hybrid"),  # type: ignore[arg-type]
        reranker=env("RERANKER", "flashrank"),  # type: ignore[arg-type]
        rerank_model=env("RERANK_MODEL", "ms-marco-MiniLM-L-12-v2"),
        flashrank_cache_dir=project_root / env("FLASHRANK_CACHE_DIR", ".cache/flashrank"),
        chat_model=env("CHAT_MODEL", "gemini-3.6-flash"),
        embedding_model=env("EMBEDDING_MODEL", "gemini-embedding-001"),
        embedding_dim=int(env("EMBEDDING_DIM", "768")),
        llm_thinking_level=env("LLM_THINKING_LEVEL", "minimal"),  # type: ignore[arg-type]
        llm_seed=int(env("LLM_SEED", "42")),
        llm_min_interval_s=float(env("LLM_MIN_INTERVAL_S", "7")),
        llm_cache_dir=project_root / env("LLM_CACHE_DIR", ".cache/llm"),
        enrich_chunks=_parse_bool(env("ENRICH_CHUNKS", "false")),
        gates_enabled=_parse_bool(env("GATES_ENABLED", "true")),
        as_of_default=as_of_default,
        carriers=carriers,
        ports=ports,
        enums=enums,
        guardrails=guardrails,
        retrieval=retrieval,
        prices=prices,
        rate_ranges=rate_ranges,
        manifest=manifest,
    )

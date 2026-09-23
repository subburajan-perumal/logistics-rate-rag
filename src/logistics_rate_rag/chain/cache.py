"""LLM response cache (docs/SPEC.md §5.5, D-15)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path

from logistics_rate_rag.ingest.models import Chunk
from logistics_rate_rag.store.retriever import RetrievedChunk


class ResponseCache:
    def __init__(self, cache_dir: Path) -> None:
        self._dir = cache_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def key(
        self,
        model: str,
        prompt_version: str,
        question: str,
        as_of: date,
        retrieved: Sequence[RetrievedChunk],
        pinned: Sequence[Chunk],
    ) -> str:
        parts = [model, prompt_version, question, as_of.isoformat()]
        parts += [f"{rc.chunk.chunk_id}:{rc.chunk.content_sha256}" for rc in retrieved]
        parts.append("--pinned--")
        parts += [f"{c.chunk_id}:{c.content_sha256}" for c in pinned]
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

    def _path(self, key: str) -> Path:
        return self._dir / f"{key}.json"

    def get(self, key: str) -> dict | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def put(self, key: str, payload: dict) -> None:
        payload = {**payload, "key": key, "stored_at": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")}
        self._path(key).write_text(
            json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2), encoding="utf-8"
        )

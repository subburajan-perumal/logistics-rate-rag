"""Exception hierarchy (docs/SPEC.md §11.2)."""

from __future__ import annotations


class RateRagError(Exception):
    pass


class ConfigError(RateRagError):
    """Bad or inconsistent config / question files."""


class CorpusFormatError(RateRagError):
    """A corpus file deviates from docs/CORPUS.md §4."""

    def __init__(self, path: object, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason


class PdfTableError(CorpusFormatError):
    def __init__(self, path: object, page: int, row: int, cells: object) -> None:
        super().__init__(path, f"bad table row on page {page}, row {row}: {cells!r}")
        self.page = page
        self.row = row
        self.cells = cells


class MissingCredential(RateRagError):
    def __init__(self, var_name: str) -> None:
        super().__init__(f"missing credential: {var_name}")
        self.var_name = var_name


class StoreError(RateRagError):
    pass


class DimensionMismatch(StoreError):
    def __init__(self, expected: int, got: int) -> None:
        super().__init__(f"embedding dimension mismatch: expected {expected}, got {got}")
        self.expected = expected
        self.got = got


class EmbeddingError(RateRagError):
    pass


class LLMError(RateRagError):
    pass


class CacheError(RateRagError):
    """Never raised for a corrupt cache file — those are treated as misses."""

"""Import-purity rule (docs/SPEC.md §1, D-19/D-30).

`guardrails/` and `schema/` may import only the standard library,
pydantic, and logistics_rate_rag's own `schema`, `errors`, `config`
modules. A `TYPE_CHECKING`-guarded import is exempt since it never
executes — that's the escape hatch this project actually uses (see
guardrails/context.py, guardrails/pipeline.py, schema/answer.py).
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARDED_DIRS = ["guardrails", "schema"]
FORBIDDEN_TOP_LEVEL = {
    "chain",
    "store",
    "rerank",
    "eval",
    "cli",
    "flashrank",
    "rank_bm25",
    "chromadb",
    "langchain_chroma",
    "pinecone",
    "langchain_google_genai",
    "langchain_core",
    "google",
}


def _is_type_checking_guard(node: ast.If) -> bool:
    test = node.test
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    return bool(isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")


def _runtime_import_names(tree: ast.Module) -> list[str]:
    names: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_If(self, node: ast.If) -> None:
            if _is_type_checking_guard(node):
                return  # body never executes at runtime — skip it
            self.generic_visit(node)

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                names.append(alias.name.split(".")[0])

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if not node.module:
                return
            parts = node.module.split(".")
            if parts[0] == "logistics_rate_rag":
                if len(parts) >= 2:
                    names.append(parts[1])
            else:
                names.append(parts[0])

    Visitor().visit(tree)
    return names


def _all_guarded_files() -> list[Path]:
    files = []
    for d in GUARDED_DIRS:
        files.extend((REPO_ROOT / "src" / "logistics_rate_rag" / d).rglob("*.py"))
    return files


def test_no_forbidden_runtime_imports():
    violations: dict[str, list[str]] = {}
    for path in _all_guarded_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        bad = [n for n in _runtime_import_names(tree) if n in FORBIDDEN_TOP_LEVEL]
        if bad:
            violations[str(path.relative_to(REPO_ROOT))] = bad
    assert not violations, f"guardrails/schema import purity violated: {violations}"


def test_guarded_dirs_actually_have_files():
    # Sanity check the test isn't silently scanning nothing.
    assert len(_all_guarded_files()) >= 6

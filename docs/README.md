# docs/ — read me first

Four documents, each answering a different kind of question. They were
written before the code (frozen 2026-09-17) and the code is built to
them. If code and docs disagree, the docs win until a Decision Log row
in `PLAN.md` says otherwise.

| Question you have | Read |
|---|---|
| Why does this project exist, what must it prove, what was decided and why, what are the phases and their acceptance checks, what are the risks? | [`PLAN.md`](PLAN.md) — §1 goals, §2 audit findings, §3 Decision Log (append-only), §18 phases, Appendix A session log |
| What exactly is in every data file, every rate rule, every question and its expected answer? | [`CORPUS.md`](CORPUS.md) |
| What is the public API of every module, every data model, every algorithm step, every config file's contents, the exact prompt, the CLI's arguments and output, the result-file schema, the tests? | [`SPEC.md`](SPEC.md) |
| How does a request flow through the system and which component is allowed to decide what? | [`architecture.md`](architecture.md) |

## Reading order for a developer starting Phase 1

1. `architecture.md` (10 minutes) — the shape.
2. `PLAN.md` §3 Decision Log and §18 phases (20 minutes) — what is
   settled and what is next.
3. `CORPUS.md` in full (20 minutes) — you will write the generator first.
4. `SPEC.md` §0–§3 (before Phase 1–2), §4–§5 (before Phase 2–3),
   §6 (before Phase 4–6), §7–§8 (before Phase 3 and 8), §9–§11 (Phase 0).

## Rules of change

- `PLAN.md` §1–§21: never edited; deviations are new Decision Log rows.
- `CORPUS.md`, `SPEC.md`, `architecture.md`: edited only together with a
  Decision Log row that names the section, in the same commit.
- Phase checkboxes and the session log in `PLAN.md` are updated every
  session.

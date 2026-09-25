# Functional spec: skill-tree

LOCKED pulled from `docs/vision.md`. Service: MCP skill DAG resolver.

## Phase 0

1. Schema for skill `requires` (front matter or sidecar — pick in build).
2. Fixture catalog + diamond DAG + `manager-git` role preset.
3. Resolver CLI: list, resolve, cycle/missing hard fail.
4. `pytest` for success rows S1–S4, S7.
5. `.grok/skills/harvest-agent-skills` with `github:` this repo.
6. Vision pack + operator mocks in `docs/`.

## Phase 1+

- MCP tools: `list_skills`, `list_roles`, `explain_tree`, `resolve_role` / `resolve_ids`.
- Multi-home scanner over configured clones (S6).
- Thin seat skill to equip a role via MCP.
- Later FRs on umbrella homes to declare `requires` instead of inlined globs.

## Acceptance

| id | statement |
|----|-----------|
| A1 | `manager-git` resolve ≤ 40% of fixture load-all and excludes IRC. |
| A2 | Diamond DAG dedupes leaf bodies. |
| A3 | Leaf edit visible through all parents on next resolve. |
| A4 | Cycles and missing refs error; no silent partial load. |
| A5 | MCP contract tests cover list + resolve (Phase 1). |

## UNKNOWN

- MCP SDK and transport.
- Production token estimator.
- Auto-migrate PRs to other skill repos.

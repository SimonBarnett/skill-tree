# Vision: skill-tree

Skill: `visionary`. New-product intake for **skill-tree** (MCP skill DAG).

## Objective

Agents load only the skill nodes required for the current role, resolved
from a DAG of skill books (base leaves plus composite managers), so
context size stays minimal while low-level playbooks stay single-sourced
and updates fan out through references.

LOCKED

## Success

| id | metric | target | how measured | fail-when |
|----|--------|--------|--------------|-----------|
| S1 | Context budget for resolved role | Fixture role `manager-git` (git + MRB + UAT, no IRC): resolved skill body total ≤ 40% of naive load-all baseline on the same fixture catalog | `pytest`: baseline = sum of fixture `SKILL.md` bytes under catalog roots; resolved = unique closure; assert `resolved <= 0.4 * baseline` | IRC skills in resolved set, or ratio > 40% |
| S2 | Unique closure | Diamond DAG: each leaf body appears once in expand payload | `pytest` on diamond fixture | Same leaf text twice |
| S3 | Single-source fan-out | Edit one leaf fixture → both parent composites see new content on next resolve | `pytest`: mutate leaf, re-resolve two parents, hashes match | Parents serve stale leaf |
| S4 | Role filter | `manager-git` includes declared git/MRB/UAT ids and excludes `agentic-irc` / bob-irc class ids | `pytest` set equality on resolved ids | IRC id present or required git id missing |
| S5 | MCP select + resolve | `list_skills` / `select_role` / `resolve_skills` return ordered skill markdown or paths | Contract tests on MCP tool schema + in-process server | Tools missing or empty resolve for valid role |
| S6 | Multi-home catalog | Index ≥3 fixture mirrors of listed SimonBarnett skill homes | Integration test: config paths → `list` returns skills from each home | Catalog hard-codes a single home |
| S7 | Cycle / missing-ref fail | Cyclic `requires` or missing id → explicit error | `pytest` negative fixtures | Cycle ignored or missing ref skipped quietly |
| S8 | Product home harvest | Schema + MCP server live in this public repo; learnings PR via harvest twin | README + `tests/` + `.grok/skills/harvest-agent-skills` with `github:` this repo | Logic only in `~/.grok` with no home PR |

Baseline for S1: union of every `SKILL.md` under **fixture** skill-home
roots (not live `~/.grok`).

LOCKED

## Shape

Primary: service

Hybrid note: the product is an MCP server plus skill catalog/resolver
(and a thin seat playbook). Cursor/Grok seats and existing skill git
homes are delivery. No consumer website or installable GUI in Phase 0.

LOCKED

## Stack

Default:

- Python 3.11+ MCP server (stdio and/or local SSE; exact SDK UNKNOWN)
- Catalog: YAML/JSON index + per-skill `requires: [skill-id, …]`
  (front matter or sidecar — UNKNOWN which)
- Skill sources: local paths / clones of public SimonBarnett skill repos
- `pytest` for S1–S8
- Public GitHub `SimonBarnett/skill-tree`
- Optional `.grok/skills/skill-tree` playbook: equip role via MCP

Why: fleet already uses MCP and markdown skills; DAG resolve is
deterministic and testable; single-source leaves match harvest model.

Why-not: dump-all context (fails S1); monorepo copies of every skill
(fails S3); website-as-product; invented registry URLs or secrets.

Catalog roots (operator list; not build dependencies of this repo):

gh-Jeeves, agentic_build, agentic_irc, club-madeira-skill,
skills-visionary, agentic_fomprep, club-madeira-onboarding,
club-madeira-campaign, open-tts, mud-skill, club-madeira-awin-connector,
bob-design-uat, skill-dba, irc-skill.

LOCKED (defaults). MCP SDK and `requires` storage form remain UNKNOWN.

## Architecture

Who talks to what. Phase 0 only.

```
[skill git homes / local paths]
        |  scan SKILL.md + requires[]
        v
[catalog]  id, path, title, requires[], tags, weight
        |
        v
[resolver]  roots (role or ids) -> topo order, dedupe, cycle detect
        |
        v
[MCP server]  list_skills | list_roles | explain_tree | resolve_*
        |
        v
[agent seat]  inject ONLY resolved skill bodies into context
```

MUD metaphor (`mud-skill` / `discworld-skills-experience`): character =
session; tree = branch skills; equip role = advance one branch, not the
whole tree. Umbrella skills become composites with `requires` instead of
inlined globs.

Trust: config is local paths / public git; resolver returns markdown only
(no skill script execution); harvest write-back stays existing harvest
skills on each home repo.

Normative test composite:

```
role:manager-git -> git-pr-workflow, bob-mrb-worker, design-uat
# agentic-irc NOT in this DAG
```

LOCKED (Phase 0 diagram). Exact production skill ids UNKNOWN until catalog pass.

## Screens

No product UI in Phase 0. Operator/MCP status wireframes for the vision
gate (not a website product). Visual UAT later: `design-uat`.

| id | file | state |
|----|------|-------|
| M1 | docs/mocks/home.html | primary — role selected, tree + size estimate |
| M2 | docs/mocks/empty.html | empty — no catalog roots |
| M3 | docs/mocks/error.html | error — cycle / missing requires |

## LOCKED

- Shape: service (MCP + catalog/resolver).
- Success S1–S8 as table.
- Composites reference bases; leaf updates fan out.
- MUD skill-tree is the metaphor; mud-skill is a source pack, not this runtime.
- First commit includes this vision pack + mocks + harvest foundation.

## UNKNOWN

- MCP SDK choice and transport defaults.
- `requires` in SKILL.md front matter vs sidecar `skill.yaml`.
- Token estimator for production logs (chars/4 vs tiktoken).
- In-process vs stdio MCP from Plan seats.
- Phase 3 auto-migrate PRs onto umbrella skills in other repos.
- Live Discworld connect in CI (optional study only; not Phase 0 gate).

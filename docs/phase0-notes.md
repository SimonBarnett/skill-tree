# Phase 0 notes

## Decisions

- **requires storage:** YAML frontmatter in each `SKILL.md` (decided in build;
  sidecar `skill.yaml` remains a possible later option).
- **Resolver:** pure Python, no LLM. Topological order via Kahn's algorithm;
  cycles and missing refs raise `ResolverError` (hard fail, S7).
- **Dedup:** the resolved closure contains each skill id at most once (S2).
- **Context metric (S1):** byte size of skill bodies. Baseline = sum of every
  fixture `SKILL.md` body; resolved = unique closure of `manager-git`.
- **MCP (S5):** deferred to Phase 1 per the functional spec.

## How to run

```
pip install -e ".[dev]"
skill-tree --catalog tests/fixtures/catalog list
skill-tree --catalog tests/fixtures/catalog resolve manager-git
pytest -q
```

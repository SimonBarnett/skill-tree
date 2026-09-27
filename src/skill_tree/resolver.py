"""Deterministic DAG resolver: topo order, dedupe, cycle/missing hard fail."""

from __future__ import annotations

from collections import defaultdict, deque

from .schema import Skill


class ResolverError(Exception):
    """Raised for cycles or missing requires references."""


def resolve(catalog: dict[str, Skill], roots: list[str]) -> list[Skill]:
    """Return skills reachable from roots in topological order, deduped.

    Hard-fails with ResolverError on a missing id or a cycle.
    """
    missing = [r for r in roots if r not in catalog]
    if missing:
        raise ResolverError(f"missing skill id(s): {', '.join(missing)}")

    indeg: dict[str, int] = {sid: 0 for sid in catalog}
    children: dict[str, list[str]] = defaultdict(list)
    for sid, skill in catalog.items():
        for req in skill.requires:
            if req not in catalog:
                raise ResolverError(f"skill {sid!r} requires missing id {req!r}")
            indeg[sid] += 1
            children[req].append(sid)

    queue: deque[str] = deque(sorted(r for r in roots))
    order: list[str] = []
    while queue:
        sid = queue.popleft()
        order.append(sid)
        for child in sorted(children[sid]):
            indeg[child] -= 1
            if indeg[child] == 0:
                queue.append(child)

    if len(order) != len(catalog):
        cycled = sorted(sid for sid, d in indeg.items() if d > 0)
        raise ResolverError(f"cycle detected involving: {', '.join(cycled)}")

    # Only the closure of the requested roots, in topo order.
    reachable: set[str] = set()
    stack = list(roots)
    while stack:
        sid = stack.pop()
        if sid in reachable:
            continue
        reachable.add(sid)
        stack.extend(catalog[sid].requires)
    return [catalog[sid] for sid in order if sid in reachable]

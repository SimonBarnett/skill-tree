"""Deterministic DAG resolver: topo order, dedupe, cycle/missing hard fail."""

from __future__ import annotations

from collections import defaultdict, deque

from .schema import Skill


class ResolverError(Exception):
    """Raised for cycles or missing requires references."""


def resolve(catalog: dict[str, Skill], roots: list[str]) -> list[Skill]:
    """Return skills reachable from roots in topological order, deduped.

    Dependencies appear before dependents. Hard-fails with ResolverError on a
    missing id or a cycle in the reachable subgraph.
    """
    missing = [r for r in roots if r not in catalog]
    if missing:
        raise ResolverError(f"missing skill id(s): {', '.join(missing)}")

    # Closure of roots via requires[] (parents → leaves).
    reachable: set[str] = set()
    stack = list(roots)
    while stack:
        sid = stack.pop()
        if sid in reachable:
            continue
        if sid not in catalog:
            raise ResolverError(f"missing skill id {sid!r}")
        reachable.add(sid)
        for req in catalog[sid].requires:
            if req not in catalog:
                raise ResolverError(f"skill {sid!r} requires missing id {req!r}")
            stack.append(req)

    # Kahn on the reachable subgraph only (indegree = number of requires).
    indeg: dict[str, int] = {sid: 0 for sid in reachable}
    children: dict[str, list[str]] = defaultdict(list)
    for sid in reachable:
        for req in catalog[sid].requires:
            # req must precede sid
            indeg[sid] += 1
            children[req].append(sid)

    queue: deque[str] = deque(sorted(sid for sid, d in indeg.items() if d == 0))
    order: list[str] = []
    while queue:
        sid = queue.popleft()
        order.append(sid)
        for child in sorted(children[sid]):
            indeg[child] -= 1
            if indeg[child] == 0:
                queue.append(child)

    if len(order) != len(reachable):
        cycled = sorted(sid for sid, d in indeg.items() if d > 0)
        raise ResolverError(f"cycle detected involving: {', '.join(cycled)}")

    return [catalog[sid] for sid in order]

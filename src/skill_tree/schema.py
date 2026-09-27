"""Skill schema: id, path, title, requires[], tags, weight."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


def _parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"\'":
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict[str, object]:
    """Parse a minimal YAML-ish frontmatter block into a dict.

    Empty ``key:`` lines (common for ``requires:`` / ``tags:`` with zero
    items) must not block a following list — they stay unset until the first
    ``- item`` promotes the value to a list (MRB #5 / CI AssertionError).
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    data: dict[str, object] = {}
    current_key: str | None = None
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and current_key is not None:
            existing = data.get(current_key)
            if not isinstance(existing, list):
                # Promote empty/missing scalar from ``key:`` into a list.
                data[current_key] = [] if existing in (None, "") else [existing]
            data[current_key].append(_parse_scalar(line.lstrip()[2:]))  # type: ignore[union-attr]
            continue
        km = KEY_RE.match(line)
        if km:
            current_key = km.group(1)
            raw_val = km.group(2)
            if raw_val.strip() == "":
                # Defer: next lines may be a sequence, or the key stays empty.
                data[current_key] = None
            else:
                data[current_key] = _parse_scalar(raw_val)
        else:
            current_key = None
    # Normalize leftover None (empty ``key:`` with no items) to "" for scalars.
    for k, v in list(data.items()):
        if v is None:
            data[k] = ""
    return data


def _as_list(value: object) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v)]
    return [str(value)]


@dataclass
class Skill:
    """One node in the skill DAG."""

    id: str
    path: Path
    title: str
    requires: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    weight: int = 0
    body: str = ""

    @property
    def size(self) -> int:
        return len(self.body.encode("utf-8"))


def load_skill(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    body = FRONTMATTER_RE.sub("", text, count=1) if FRONTMATTER_RE.match(text) else text
    sid = str(fm.get("id") or path.parent.name)
    title = str(fm.get("title") or sid)
    return Skill(
        id=sid,
        path=path,
        title=title,
        requires=_as_list(fm.get("requires")),
        tags=_as_list(fm.get("tags")),
        weight=int(fm.get("weight") or 0),
        body=body.strip() + "\n",
    )


def load_catalog(root: Path) -> dict[str, Skill]:
    """Load every SKILL.md under root into an id -> Skill map."""
    catalog: dict[str, Skill] = {}
    for path in sorted(root.rglob("SKILL.md")):
        if ".git" in path.parts:
            continue
        skill = load_skill(path)
        if skill.id in catalog:
            raise ValueError(
                f"duplicate skill id {skill.id!r}: {catalog[skill.id].path} and {path}"
            )
        catalog[skill.id] = skill
    return catalog

"""Shared fixtures: diamond DAG + manager-git role."""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_tree.schema import load_catalog

# Diamond DAG:
#   manager-git -> git-pr-workflow, bob-mrb-worker, design-uat
#   git-pr-workflow -> git-base
#   bob-mrb-worker  -> git-base
#   design-uat      -> (none)
# agentic-irc is NOT in this DAG (role filter S4).

SKILL_BODIES = {
    "git-base": "# git-base\nshared git primitives\n",
    "git-pr-workflow": "# git-pr-workflow\nPR workflow on top of git-base\n",
    "bob-mrb-worker": "# bob-mrb-worker\nMRB worker on top of git-base\n",
    "design-uat": "# design-uat\nUAT playbook\n",
    "manager-git": (
        "# manager-git\n"
        "composite: git-pr-workflow + bob-mrb-worker + design-uat\n"
    ),
    # Large body so excluding IRC from manager-git keeps S1 ≤ 40% of load-all.
    "agentic-irc": (
        "# agentic-irc\n"
        "IRC skills - must NOT appear in manager-git resolve\n"
        + ("irc-playbook-line\n" * 80)
    ),
}

REQUIRES = {
    "git-base": [],
    "git-pr-workflow": ["git-base"],
    "bob-mrb-worker": ["git-base"],
    "design-uat": [],
    "manager-git": ["git-pr-workflow", "bob-mrb-worker", "design-uat"],
    "agentic-irc": [],
}

TAGS = {
    "git-base": ["git"],
    "git-pr-workflow": ["git", "pr"],
    "bob-mrb-worker": ["git", "mrb"],
    "design-uat": ["uat", "design"],
    "manager-git": ["role", "manager"],
    "agentic-irc": ["irc"],
}

WEIGHTS = {
    "git-base": 10,
    "git-pr-workflow": 20,
    "bob-mrb-worker": 20,
    "design-uat": 15,
    "manager-git": 5,
    "agentic-irc": 30,
}


def _write_skill(root: Path, sid: str) -> None:
    d = root / sid
    d.mkdir(parents=True, exist_ok=True)
    req_block = "".join(f"  - {r}\n" for r in REQUIRES[sid])
    tag_block = "".join(f"  - {t}\n" for t in TAGS[sid])
    text = (
        "---\n"
        f"id: {sid}\n"
        f"title: {sid}\n"
        f"weight: {WEIGHTS[sid]}\n"
        "requires:\n"
        f"{req_block}"
        "tags:\n"
        f"{tag_block}"
        "three_laws: bound\n"
        "three_laws_checklist: passed\n"
        "---\n"
        "> CAST IRON: This skill is bound by [the Three Laws](CAST_IRON/THREE_LAWS.md) and is void where it conflicts with them.\n"
        f"{SKILL_BODIES[sid]}"
    )
    (d / "SKILL.md").write_text(text, encoding="utf-8")


def _write_cycle(root: Path) -> None:
    for sid, reqs in (("a", ["b"]), ("b", ["a"])):
        d = root / sid
        d.mkdir(parents=True, exist_ok=True)
        req_block = "".join(f"  - {r}\n" for r in reqs)
        (d / "SKILL.md").write_text(
            "---\n"
            f"id: {sid}\n"
            "title: cycle\n"
            "requires:\n"
            f"{req_block}"
            "three_laws: bound\n"
            "three_laws_checklist: passed\n"
            "---\n"
            "> CAST IRON: This skill is bound by [the Three Laws](CAST_IRON/THREE_LAWS.md) and is void where it conflicts with them.\n"
            f"# {sid}\n",
            encoding="utf-8",
        )


def _write_missing_ref(root: Path) -> None:
    d = root / "orphan"
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        "---\n"
        "id: orphan\n"
        "title: orphan\n"
        "requires:\n"
        "  - does-not-exist\n"
        "three_laws: bound\n"
        "three_laws_checklist: passed\n"
        "---\n"
        "> CAST IRON: This skill is bound by [the Three Laws](CAST_IRON/THREE_LAWS.md) and is void where it conflicts with them.\n"
        "# orphan\n",
        encoding="utf-8",
    )


def _write_duplicate(root: Path) -> None:
    for sub in ("one", "two"):
        d = root / sub / "dup"
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(
            "---\n"
            "id: dup\n"
            "title: dup\n"
            "three_laws: bound\n"
            "three_laws_checklist: passed\n"
            "---\n"
            "> CAST IRON: This skill is bound by [the Three Laws](CAST_IRON/THREE_LAWS.md) and is void where it conflicts with them.\n"
            f"# {sub}/dup\n",
            encoding="utf-8",
        )


def _build(root: Path, kind: str) -> None:
    if kind == "diamond":
        for sid in SKILL_BODIES:
            _write_skill(root, sid)
    elif kind == "cycle":
        _write_cycle(root)
    elif kind == "missing":
        _write_missing_ref(root)
    elif kind == "duplicate":
        _write_duplicate(root)
    else:
        raise ValueError(kind)


CATALOGS = {
    "diamond": _build,
    "cycle": _build,
    "missing": _build,
    "duplicate": _build,
}


def _make_fixture(kind: str, *, load: bool = True):
    @pytest.fixture
    def _fixture(tmp_path: Path):
        root = tmp_path / kind
        root.mkdir()
        _build(root, kind)
        # Duplicate-id catalogs hard-fail at load_catalog — return root only
        # so the test can assert the ValueError (MRB #5 CI ERROR at setup).
        if not load:
            return root, None
        return root, load_catalog(root)

    _fixture.__name__ = f"catalog_{kind}"
    return _fixture


catalog_diamond = _make_fixture("diamond")
catalog_cycle = _make_fixture("cycle")
catalog_missing = _make_fixture("missing")
catalog_duplicate = _make_fixture("duplicate", load=False)

"""Phase 0 resolver tests: S1, S2, S3, S4, S7."""

from __future__ import annotations

import pytest

from skill_tree.resolver import ResolverError, resolve
from skill_tree.schema import load_catalog


# S1: manager-git resolved body <= 40% of naive load-all, no IRC.
def test_s1_context_budget(catalog_diamond):
    root, catalog = catalog_diamond
    baseline = sum(s.size for s in catalog.values())
    ordered = resolve(catalog, ["manager-git"])
    resolved = sum(s.size for s in ordered)
    assert "agentic-irc" not in {s.id for s in ordered}
    assert resolved <= 0.4 * baseline, f"resolved {resolved} > 40% of baseline {baseline}"


# S2: diamond DAG dedupes - git-base appears once.
def test_s2_unique_closure(catalog_diamond):
    root, catalog = catalog_diamond
    ordered = resolve(catalog, ["manager-git"])
    ids = [s.id for s in ordered]
    assert ids.count("git-base") == 1
    assert set(ids) == {
        "manager-git",
        "git-pr-workflow",
        "bob-mrb-worker",
        "design-uat",
        "git-base",
    }


# S3: single-source fan-out - edit one leaf, both parents' resolve closures see it.
def test_s3_single_source_fanout(catalog_diamond, tmp_path):
    root, catalog = catalog_diamond
    leaf = root / "git-base" / "SKILL.md"
    leaf.write_text(leaf.read_text(encoding="utf-8") + "NEW LINE\n", encoding="utf-8")
    catalog = load_catalog(root)
    for root_id in ("git-pr-workflow", "bob-mrb-worker"):
        ordered = resolve(catalog, [root_id])
        by_id = {s.id: s for s in ordered}
        assert "git-base" in by_id
        assert "NEW LINE" in by_id["git-base"].body


# S4: role filter - manager-git includes git/MRB/UAT, excludes IRC.
def test_s4_role_filter(catalog_diamond):
    root, catalog = catalog_diamond
    ordered = resolve(catalog, ["manager-git"])
    ids = {s.id for s in ordered}
    assert {"git-pr-workflow", "bob-mrb-worker", "design-uat"} <= ids
    assert "agentic-irc" not in ids
    assert "git-base" in ids  # transitive dep


# S7: cycle -> explicit error.
def test_s7_cycle_fails(catalog_cycle):
    root, catalog = catalog_cycle
    with pytest.raises(ResolverError, match="cycle"):
        resolve(catalog, ["a"])


# S7: missing ref -> explicit error.
def test_s7_missing_ref_fails(catalog_missing):
    root, catalog = catalog_missing
    with pytest.raises(ResolverError, match="missing"):
        resolve(catalog, ["orphan"])


# S7: missing root -> explicit error.
def test_s7_missing_root_fails(catalog_diamond):
    root, catalog = catalog_diamond
    with pytest.raises(ResolverError, match="missing skill id"):
        resolve(catalog, ["no-such-role"])


# Duplicate ids across the catalog are a hard error at load time.
def test_duplicate_id_fails(catalog_duplicate):
    root, catalog = catalog_duplicate
    assert catalog is None  # fixture must not pre-load (would ERROR at setup)
    with pytest.raises(ValueError, match="duplicate skill id"):
        load_catalog(root)


def test_empty_requires_then_tags_list():
    """Empty ``requires:`` must not break following ``tags:`` list items."""
    from skill_tree.schema import parse_frontmatter

    fm = parse_frontmatter(
        "---\n"
        "id: agentic-irc\n"
        "requires:\n"
        "tags:\n"
        "  - irc\n"
        "---\n"
        "# body\n"
    )
    assert fm.get("requires") in ("", None, [])
    assert fm.get("tags") == ["irc"]

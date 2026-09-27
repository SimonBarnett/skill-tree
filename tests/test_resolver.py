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


# S3: single-source fan-out - edit one leaf, both parents see it.
def test_s3_single_source_fanout(catalog_diamond, tmp_path):
    root, catalog = catalog_diamond
    leaf = root / "git-base" / "SKILL.md"
    leaf.write_text(leaf.read_text(encoding="utf-8") + "NEW LINE\n", encoding="utf-8")
    catalog = load_catalog(root)
    parents = resolve(catalog, ["git-pr-workflow", "bob-mrb-worker"])
    bodies = {s.id: s.body for s in parents}
    # S3: both parents' closures include the edited leaf body.
    assert "git-base" in bodies
    assert "NEW LINE" in bodies["git-base"]
    assert {"git-pr-workflow", "bob-mrb-worker"} <= set(bodies)


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
    root, _ = catalog_duplicate
    with pytest.raises(ValueError, match="duplicate skill id"):
        load_catalog(root)

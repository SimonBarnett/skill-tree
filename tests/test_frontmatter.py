"""Frontmatter parser edge cases."""

from pathlib import Path

from skill_tree.schema import load_skill, parse_frontmatter


def test_empty_key_then_list_items():
    text = (
        "---\n"
        "id: demo\n"
        "requires:\n"
        "tags:\n"
        "  - irc\n"
        "  - fleet\n"
        "---\n"
        "body\n"
    )
    fm = parse_frontmatter(text)
    assert fm["requires"] == []
    assert fm["tags"] == ["irc", "fleet"]


def test_load_skill_empty_requires(tmp_path: Path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        "---\n"
        "id: demo\n"
        "title: demo\n"
        "requires:\n"
        "tags:\n"
        "  - irc\n"
        "---\n"
        "# demo\n",
        encoding="utf-8",
    )
    skill = load_skill(p)
    assert skill.requires == []
    assert skill.tags == ["irc"]
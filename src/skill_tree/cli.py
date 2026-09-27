"""CLI: list and resolve skills from a catalog root."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .resolver import ResolverError, resolve
from .schema import load_catalog


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="skill-tree", description="Resolve a DAG of agent skills")
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="list skill ids")
    ls.add_argument("--catalog", type=Path, required=True)

    rs = sub.add_parser("resolve", help="resolve roots to a deduped topo-ordered list")
    rs.add_argument("--catalog", type=Path, required=True)
    rs.add_argument("roots", nargs="+", help="role or skill ids to resolve from")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.cmd == "list":
        for sid in sorted(catalog):
            print(sid)
        return 0

    try:
        ordered = resolve(catalog, args.roots)
    except ResolverError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for skill in ordered:
        print(f"{skill.id}\t{skill.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

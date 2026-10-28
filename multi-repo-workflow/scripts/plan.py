#!/usr/bin/env python3
"""Read repos.yaml and print the plan for a multi-repo change.

Usage:
  plan.py --list                               list repos with kind and purpose
  plan.py --validate                           check the map: unknown deps, cycles, missing paths
  plan.py [--ticket PLAT-1234] [--type feature] [--slug rate-limit-headers] [--json] REPO [REPO ...]
                                               print the touched repos in dependency order with
                                               path, branch name, verify commands and PR settings

The config file is found via --config, $MULTI_REPO_CONFIG, repos.yaml in the current
directory or any parent up to $HOME, then ~/.config/multi-repo/repos.yaml.
Keys starting with "_" are review notes and are ignored.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("plan.py needs PyYAML: pip install pyyaml")


# ---------------------------------------------------------------- loading

def find_config(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("MULTI_REPO_CONFIG"):
        candidates.append(Path(os.environ["MULTI_REPO_CONFIG"]))
    home = Path.home().resolve()
    cur = Path.cwd().resolve()
    while True:
        candidates.append(cur / "repos.yaml")
        if cur == home or cur.parent == cur:
            break
        cur = cur.parent
    candidates.append(home / ".config" / "multi-repo" / "repos.yaml")
    for c in candidates:
        if c.expanduser().is_file():
            return c.expanduser()
    sys.exit("repos.yaml not found (tried --config, $MULTI_REPO_CONFIG, cwd and parents, "
             "~/.config/multi-repo/). Generate one with references/inventory.md.")


def strip_private(obj):
    """Drop keys that start with '_' at every level."""
    if isinstance(obj, dict):
        return {k: strip_private(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, list):
        return [strip_private(v) for v in obj]
    return obj


def load(path: Path) -> dict:
    with path.open() as fh:
        data = strip_private(yaml.safe_load(fh) or {})
    data.setdefault("defaults", {})
    data["defaults"].setdefault("default_branch", "main")
    data["defaults"].setdefault("branch_pattern", "{type}/{ticket}-{slug}")
    data["defaults"].setdefault("pr_draft_downstream", True)
    data.setdefault("repos", [])
    data["workspace_root"] = os.path.expanduser(data.get("workspace_root") or str(path.parent))
    for r in data["repos"]:
        r.setdefault("depends_on", [])
        r.setdefault("provides", [])
        r.setdefault("consumes", [])
        r.setdefault("verify", [])
        r.setdefault("pr", {})
        r.setdefault("default_branch", data["defaults"]["default_branch"])
    return data


def by_name(data: dict) -> dict[str, dict]:
    return {r["name"]: r for r in data["repos"]}


# ---------------------------------------------------------------- graph

def topo_order(names: list[str], repos: dict[str, dict]) -> list[str]:
    """Kahn's algorithm over the selected repos only; raises on a cycle."""
    selected = set(names)
    indeg = {n: 0 for n in selected}
    for n in selected:
        for d in repos[n]["depends_on"]:
            if d in selected:
                indeg[n] += 1
    ready = sorted(n for n, k in indeg.items() if k == 0)
    order: list[str] = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for m in selected:
            if n in repos[m]["depends_on"]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    ready.append(m)
                    ready.sort()
    if len(order) != len(selected):
        raise ValueError("dependency cycle among: " + ", ".join(sorted(selected - set(order))))
    return order


# ---------------------------------------------------------------- commands

def cmd_list(data: dict) -> int:
    width = max((len(r["name"]) for r in data["repos"]), default=4)
    for r in data["repos"]:
        deps = ", ".join(r["depends_on"]) or "-"
        print(f"{r['name']:<{width}}  {r.get('kind', '?'):<14} deps: {deps}")
        print(f"{'':<{width}}  {r.get('purpose', '(no purpose)')}")
    return 0


def cmd_validate(data: dict) -> int:
    repos = by_name(data)
    errors: list[str] = []
    warnings: list[str] = []
    names = [r["name"] for r in data["repos"]]
    for n in names:
        if names.count(n) > 1:
            errors.append(f"duplicate repo name: {n}")
    for r in data["repos"]:
        for d in r["depends_on"]:
            if d not in repos:
                errors.append(f"{r['name']}: depends_on unknown repo '{d}'")
        if not r.get("purpose"):
            warnings.append(f"{r['name']}: no purpose")
        if not r["verify"]:
            warnings.append(f"{r['name']}: no verify commands")
        p = r.get("path")
        if p and not Path(data["workspace_root"], p).is_dir():
            warnings.append(f"{r['name']}: path not found on disk: {Path(data['workspace_root'], p)}")
    provided = {x for r in data["repos"] for x in r["provides"]}
    for r in data["repos"]:
        for c in r["consumes"]:
            if c not in provided:
                warnings.append(f"{r['name']}: consumes '{c}' which no repo provides")
    try:
        topo_order(list(repos), repos)
    except ValueError as e:
        errors.append(str(e))
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    print(f"{len(data['repos'])} repos, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def cmd_plan(data: dict, args: argparse.Namespace) -> int:
    repos = by_name(data)
    unknown = [n for n in args.repos if n not in repos]
    if unknown:
        sys.exit("unknown repo(s): " + ", ".join(unknown) + "  (see --list)")
    try:
        order = topo_order(args.repos, repos)
    except ValueError as e:
        sys.exit(str(e))

    branch = data["defaults"]["branch_pattern"].format(
        type=args.type, ticket=args.ticket or "TICKET", slug=slugify(args.slug or "change"))

    plan = []
    for i, n in enumerate(order):
        r = repos[n]
        upstream_in_change = [d for d in r["depends_on"] if d in order]
        upstream_outside = [d for d in r["depends_on"] if d not in order]
        plan.append({
            "order": i + 1,
            "name": n,
            "path": str(Path(data["workspace_root"], r.get("path") or n)),
            "default_branch": r["default_branch"],
            "branch": branch,
            "kind": r.get("kind"),
            "purpose": r.get("purpose"),
            "verify": r["verify"],
            "pr": {
                "reviewers": r["pr"].get("reviewers", []),
                "labels": r["pr"].get("labels", []),
                "template": r["pr"].get("template") or data["defaults"].get("pr_template"),
                "draft": bool(upstream_in_change) and data["defaults"]["pr_draft_downstream"],
            },
            "merge_after": upstream_in_change,
            "depends_on_outside_change": upstream_outside,
            "notes": r.get("notes"),
        })

    if args.json:
        print(json.dumps({"ticket": args.ticket, "branch": branch, "repos": plan}, indent=2))
        return 0

    print(f"Ticket: {args.ticket or '(none — ask the user)'}")
    print(f"Branch: {branch}")
    print("Order:  " + " → ".join(order))
    for p in plan:
        print()
        print(f"{p['order']}. {p['name']}  ({p['kind'] or '?'})")
        print(f"   path:    {p['path']}")
        print(f"   base:    origin/{p['default_branch']}")
        if p["merge_after"]:
            print(f"   merge after: {', '.join(p['merge_after'])}" + ("  → open PR as draft" if p["pr"]["draft"] else ""))
        if p["depends_on_outside_change"]:
            print(f"   depends on (unchanged): {', '.join(p['depends_on_outside_change'])}")
        print("   verify:  " + (" && ".join(p["verify"]) if p["verify"] else "(none listed — pick the obvious one and tell the user)"))
        pr = p["pr"]
        bits = []
        if pr["reviewers"]:
            bits.append("reviewers " + ", ".join(pr["reviewers"]))
        if pr["labels"]:
            bits.append("labels " + ", ".join(pr["labels"]))
        if pr["template"]:
            bits.append("template " + pr["template"])
        print("   pr:      " + ("; ".join(bits) if bits else "(defaults)"))
        if p["notes"]:
            print(f"   notes:   {p['notes']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", help="path to repos.yaml")
    ap.add_argument("--list", action="store_true", help="list repos")
    ap.add_argument("--validate", action="store_true", help="validate the map")
    ap.add_argument("--ticket", help="ticket id, e.g. PLAT-1234")
    ap.add_argument("--type", default="feature", help="feature | fix | chore | hotfix")
    ap.add_argument("--slug", help="short description for the branch name")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("repos", nargs="*", help="repos touched by this change")
    args = ap.parse_args(argv)

    data = load(find_config(args.config))
    if args.list:
        return cmd_list(data)
    if args.validate:
        return cmd_validate(data)
    if not args.repos:
        ap.error("give repo names, or --list / --validate")
    return cmd_plan(data, args)


if __name__ == "__main__":
    sys.exit(main())

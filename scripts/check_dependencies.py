#!/usr/bin/env python3
"""Read-only verification of sibling checkouts; Python 3.9+, no network."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import unicodedata


REPOSITORY = Path(__file__).resolve().parents[1]
ROUTE_DEPENDENCIES = {
    "audience": {"prompt-audience-research"},
    "hvco": {"promt-hvco", "promt-copywriting"},
    "clip": {"prompt-clip-landing", "promt-copywriting"},
    "copywriting": {"promt-copywriting"},
}


def read_manifest(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"dependencies"}:
        raise ValueError("manifest schema")
    entries = data["dependencies"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("dependencies must be a nonempty list")
    names = set()
    for item in entries:
        if not isinstance(item, dict) or set(item) != {
            "name", "url", "revision", "files", "purpose", "routes"
        }:
            raise ValueError("dependency schema")
        routes = item["routes"]
        if (not isinstance(routes, list) or not routes or
                any(r not in ("audience", "hvco", "clip", "copywriting") for r in routes) or
                len(set(routes)) != len(routes)):
            raise ValueError("invalid routes")
        name = item["name"]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name):
            raise ValueError("invalid checkout name")
        if name in names:
            raise ValueError("duplicate checkout name")
        names.add(name)
        if not isinstance(item["revision"], str) or not re.fullmatch(r"[0-9a-f]{40}", item["revision"]):
            raise ValueError("revision must be an exact 40-character SHA")
        for key in ("url", "purpose"):
            if not isinstance(item[key], str) or not item[key].strip() or any(
                ord(c) < 32 or unicodedata.category(c) == "Cf" for c in item[key]
            ):
                raise ValueError("invalid dependency metadata")
        files = item["files"]
        if not isinstance(files, list) or not files or len(set(map(str, files))) != len(files):
            raise ValueError("files must be a nonempty unique list")
        for file in files:
            if not isinstance(file, str) or not file or "\\" in file or any(ord(c) < 32 or unicodedata.category(c) == "Cf" for c in file):
                raise ValueError("invalid relative file")
            relative = PurePosixPath(file)
            if relative.is_absolute() or any(p in ("", ".", "..") for p in file.split("/")):
                raise ValueError("files must stay inside checkout")
    return entries


def select_entries(entries, route):
    routes = [route] if route else list(ROUTE_DEPENDENCIES)
    for selected_route in routes:
        names = {item["name"] for item in entries if selected_route in item["routes"]}
        missing = ROUTE_DEPENDENCIES[selected_route] - names
        if missing:
            raise ValueError("incomplete route " + selected_route + ": " + ", ".join(sorted(missing)))
    return [item for item in entries if not route or route in item["routes"]]


def git(checkout, *args):
    return subprocess.run(
        ["git", "--no-replace-objects", "--no-optional-locks", "-C", str(checkout), *args],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, check=True, timeout=10,
    ).stdout


def check_dependency(root, item):
    checkout = root / item["name"]
    if checkout.is_symlink():
        return "invalid checkout (symlink)"
    if not checkout.is_dir():
        return "missing checkout"
    if checkout.resolve().parent != root.resolve():
        return "invalid checkout"
    try:
        top = Path(git(checkout, "rev-parse", "--show-toplevel").decode().strip()).resolve()
        if top != checkout.resolve():
            return "invalid checkout"
        head = git(checkout, "rev-parse", "HEAD").decode().strip()
        if head != item["revision"]:
            return "stale revision"
        problems = []
        for file in item["files"]:
            target = checkout / file
            parts = PurePosixPath(file).parts
            symlink = any(checkout.joinpath(*parts[:depth]).is_symlink()
                          for depth in range(1, len(parts) + 1))
            if symlink or not target.is_file() or checkout.resolve() not in target.resolve().parents:
                problems.append(file + ": missing/invalid required file")
                continue
            # Git status can hide edits behind assume-unchanged/skip-worktree.
            # Reject pinned symlinks too: their blobs store link text, not file bytes.
            entry = git(checkout, "ls-tree", "-z", item["revision"], "--", file)
            if not entry.startswith((b"100644 blob ", b"100755 blob ")):
                problems.append(file + ": missing/invalid required file")
                continue
            if target.read_bytes() != git(checkout, "show", item["revision"] + ":" + file):
                problems.append(file + ": required file differs from pinned bytes")
                continue
        if git(checkout, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
            problems.append("dirty checkout")
        return ", ".join(problems) if problems else "ok"
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return "unreadable checkout"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos-root", type=Path, required=True,
                        help="directory containing the named sibling checkouts ")
    parser.add_argument("--route", choices=("audience", "hvco", "clip", "copywriting"))
    args = parser.parse_args(argv)
    try:
        entries = select_entries(read_manifest(REPOSITORY / "dependencies.json"), args.route)
    except (OSError, ValueError, TypeError):
        print("dependencies.json: invalid manifest", file=sys.stderr)
        return 2
    failed = False
    for item in entries:
        status = check_dependency(args.repos_root, item)
        print("{}: {}".format(args.repos_root / item["name"], status))
        failed |= status != "ok"
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

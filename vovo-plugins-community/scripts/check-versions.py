#!/usr/bin/env python3
"""Checks manifest versions: semver, and bumped whenever a manifest changed since a base git revision.

Usage:
  python3 scripts/check-versions.py              compare the working tree with HEAD (the previous commit)
  VOVO_BASE_REF=origin/v1 python3 scripts/check-versions.py   compare with another revision (CI, pull requests)

A manifest whose bytes differ from the base revision must have a strictly greater semver version. A manifest
absent from the base revision (a new source) only needs a valid version. Without git or without the base
revision, the bump check is skipped with a notice. Standard library only.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

from repo_lib import ROOT, RepoError, is_semver, load_sources, semver_key  # noqa: E402


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True)


def main() -> int:
    try:
        sources = load_sources()  # also checks that every version is semver
    except RepoError as exc:
        print(f"check-versions: {exc}", file=sys.stderr)
        return 1
    base = os.environ.get("VOVO_BASE_REF", "HEAD")
    try:
        resolved = git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    except FileNotFoundError:
        print("check-versions: git not found, version bump check skipped.")
        return 0
    if resolved.returncode != 0:
        print(f"check-versions: revision {base!r} not found, version bump check skipped.")
        return 0
    errors = []
    for source in sources:
        path = f"sources/{source.key}/source.json"
        previous = git("show", f"{base}:{path}")
        if previous.returncode != 0 or previous.stdout == source.manifest_bytes:
            continue  # new source, or unchanged
        try:
            old_version = json.loads(previous.stdout.decode("utf-8")).get("version")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            old_version = None
        if not is_semver(old_version):
            continue  # the base revision had no usable version: nothing to compare with
        if semver_key(source.version) <= semver_key(old_version):
            errors.append(
                f"{path} changed since {base} but its version is still {source.version} "
                f"(was {old_version}): bump it, add a CHANGELOG.md entry, regenerate repo.json."
            )
    for error in errors:
        print(f"check-versions: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"Manifest versions OK (compared with {base}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

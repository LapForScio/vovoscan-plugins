#!/usr/bin/env python3
"""Builds repo.json (repository index, formatVersion 1) from sources/*/source.json.

Usage:
  python3 scripts/build-index.py           write repo.json at the repository root
  python3 scripts/build-index.py --check   exit 1 if repo.json is missing or out of date

Standard library only. The output is deterministic: sources sorted by key, fixed key order, 2-space
indentation, UTF-8, trailing newline.
"""

from __future__ import annotations

import argparse
import json
import sys

sys.dont_write_bytecode = True

from repo_lib import (  # noqa: E402
    FORMAT_VERSION,
    MAX_CHANGES_CHARS,
    MAX_REPO_BYTES,
    REPO_HOMEPAGE,
    REPO_ID,
    REPO_ID_RE,
    REPO_NAME,
    ROOT,
    RepoError,
    Source,
    check_icon,
    first_changelog_section,
    load_sources,
    sha256_hex,
)

REPO_FILE = ROOT / "repo.json"


def entry(source: Source) -> dict:
    manifest = source.manifest
    item = {
        "key": source.key,
        "name": manifest["name"],
        "version": manifest["version"],
        "contractVersion": manifest["contractVersion"],
        "kinds": manifest["kinds"],
        "langs": manifest["langs"],
        "rights": manifest.get("rights", {}).get("basis"),
        # Relative to the URL of repo.json, which sits at the repository root.
        "manifest": f"sources/{source.key}/source.json",
        "sha256": sha256_hex(source.manifest_bytes),
    }
    if source.icon is not None:
        check_icon(source.icon)
        item["icon"] = f"sources/{source.key}/icon.png"
    if source.changelog is not None:
        heading, changes = first_changelog_section(source.changelog)
        label = source.changelog.relative_to(ROOT)
        if heading.split()[0] != source.version:
            raise RepoError(
                f"{label}: the first section is '## {heading}', expected '## {source.version}' "
                "(write the changelog entry for the manifest version)."
            )
        if len(changes) > MAX_CHANGES_CHARS:
            raise RepoError(f"{label}: the {heading} section is {len(changes)} chars (limit {MAX_CHANGES_CHARS}).")
        item["changes"] = changes
    return item


def build() -> tuple[bytes, int]:
    if not REPO_ID_RE.match(REPO_ID):
        raise RepoError(f"repository id {REPO_ID!r} does not match {REPO_ID_RE.pattern}.")
    sources = load_sources()
    index = {
        "formatVersion": FORMAT_VERSION,
        "id": REPO_ID,
        "name": REPO_NAME,
        "homepage": REPO_HOMEPAGE,
        "sources": [entry(source) for source in sources],
    }
    data = (json.dumps(index, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if len(data) > MAX_REPO_BYTES:
        raise RepoError(f"repo.json would be {len(data)} bytes (limit {MAX_REPO_BYTES}).")
    return data, len(sources)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if repo.json is out of date")
    args = parser.parse_args()
    try:
        data, count = build()
    except RepoError as exc:
        print(f"build-index: {exc}", file=sys.stderr)
        return 1
    if args.check:
        current = REPO_FILE.read_bytes() if REPO_FILE.is_file() else None
        if current != data:
            print("build-index: repo.json is out of date: run python3 scripts/build-index.py", file=sys.stderr)
            return 1
        print("repo.json is up to date.")
        return 0
    REPO_FILE.write_bytes(data)
    print(f"Wrote {REPO_FILE.relative_to(ROOT)} ({count} source{'s' if count != 1 else ''}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

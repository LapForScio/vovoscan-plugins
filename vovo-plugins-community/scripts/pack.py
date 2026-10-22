#!/usr/bin/env python3
"""Builds .vovo packages: dist/<key>-<version>.vovo, one per source (or only the keys given).

Usage:
  python3 scripts/pack.py                 package every source
  python3 scripts/pack.py gutenberg ...   package only these keys

A .vovo is a zip with source.json at the root (exact bytes of sources/<key>/source.json), plus icon.png and
README.md when the source has them; nothing else. Limits: 1 MB total, 8 entries, icon 256 KB, manifest
256 KB. The output is deterministic (fixed entry order, timestamps and permissions). Standard library only.
dist/ is git-ignored: packages are attached to GitHub releases, not committed.
"""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

from repo_lib import (  # noqa: E402
    MAX_PACKAGE_BYTES,
    MAX_PACKAGE_ENTRIES,
    ROOT,
    RepoError,
    Source,
    check_icon,
    load_sources,
    parse_manifest,
)

DIST_DIR = ROOT / "dist"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)  # the earliest date a zip can store
ALLOWED_ENTRIES = ("source.json", "icon.png", "README.md")


def entries(source: Source) -> list[tuple[str, bytes]]:
    files = [("source.json", source.manifest_bytes)]
    if source.icon is not None:
        files.append(("icon.png", check_icon(source.icon)))
    if source.readme is not None:
        files.append(("README.md", source.readme.read_bytes()))
    return files


def build_zip(files: list[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in files:
            info = zipfile.ZipInfo(name, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix, whatever the build machine
            info.external_attr = 0o100644 << 16  # regular file, rw-r--r--
            archive.writestr(info, data, compresslevel=9)
    return buffer.getvalue()


def verify_package(data: bytes, source: Source) -> None:
    """Same rules the app applies when importing a .vovo file."""
    label = f"{source.key}-{source.version}.vovo"
    if len(data) > MAX_PACKAGE_BYTES:
        raise RepoError(f"{label}: {len(data)} bytes (limit {MAX_PACKAGE_BYTES}).")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if len(names) > MAX_PACKAGE_ENTRIES:
            raise RepoError(f"{label}: {len(names)} entries (limit {MAX_PACKAGE_ENTRIES}).")
        if len(set(names)) != len(names):
            raise RepoError(f"{label}: duplicate entries.")
        for name in names:
            if "/" in name or "\\" in name or name.startswith(".") or name not in ALLOWED_ENTRIES:
                raise RepoError(f"{label}: entry {name!r} is not allowed (only {', '.join(ALLOWED_ENTRIES)}).")
        if "source.json" not in names:
            raise RepoError(f"{label}: source.json is missing.")
        manifest = parse_manifest(archive.read("source.json"), f"{label}!source.json")
        if (manifest["key"], manifest["version"]) != (source.key, source.version):
            raise RepoError(f"{label}: the packaged manifest does not match the file name.")
        if archive.testzip() is not None:
            raise RepoError(f"{label}: corrupt entry.")


def pack(source: Source) -> Path:
    data = build_zip(entries(source))
    verify_package(data, source)
    DIST_DIR.mkdir(exist_ok=True)
    target = DIST_DIR / f"{source.key}-{source.version}.vovo"
    temporary = target.with_suffix(".vovo.tmp")
    temporary.write_bytes(data)
    temporary.replace(target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("keys", nargs="*", help="source keys to package (default: all)")
    args = parser.parse_args()
    try:
        sources = load_sources()
        if args.keys:
            known = {source.key for source in sources}
            unknown = sorted(set(args.keys) - known)
            if unknown:
                raise RepoError(f"unknown source keys: {', '.join(unknown)}.")
            sources = [source for source in sources if source.key in args.keys]
        for source in sources:
            target = pack(source)
            print(f"Wrote {target.relative_to(ROOT)} ({target.stat().st_size} bytes).")
    except RepoError as exc:
        print(f"pack: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

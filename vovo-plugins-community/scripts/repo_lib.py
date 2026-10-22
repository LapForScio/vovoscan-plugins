"""Shared helpers for the repository scripts (Python 3 standard library only).

Implements the limits and checks of the plugin spec: repository index (repo.json, formatVersion 1)
and packages (.vovo).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"

KB = 1024
MB = 1024 * KB

FORMAT_VERSION = 1
REPO_ID = "io.github.lapforscio.community"
REPO_NAME = "vovoscan community sources"
REPO_HOMEPAGE = "https://github.com/LapForScio/vovoscan-plugins"

MAX_REPO_BYTES = 512 * KB
MAX_SOURCES = 500
MAX_MANIFEST_BYTES = 256 * KB
MAX_ICON_BYTES = 256 * KB
MAX_CHANGES_CHARS = 2000
MAX_PACKAGE_BYTES = 1 * MB
MAX_PACKAGE_ENTRIES = 8

REPO_ID_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9-]+)+$")
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
RESERVED_KEYS = {"vovoscan"}
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?$"
)
REQUIRED_FIELDS = (
    "contractVersion", "key", "name", "version", "kinds", "langs", "catalog", "title", "content",
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class RepoError(Exception):
    """A source or the repository breaks a rule of the spec."""


@dataclass(frozen=True)
class Source:
    key: str
    directory: Path
    manifest_bytes: bytes
    manifest: dict

    @property
    def version(self) -> str:
        return self.manifest["version"]

    @property
    def icon(self) -> Path | None:
        path = self.directory / "icon.png"
        return path if path.is_file() else None

    @property
    def readme(self) -> Path | None:
        path = self.directory / "README.md"
        return path if path.is_file() else None

    @property
    def changelog(self) -> Path | None:
        path = self.directory / "CHANGELOG.md"
        return path if path.is_file() else None


def is_semver(value: object) -> bool:
    return isinstance(value, str) and SEMVER_RE.match(value) is not None


def semver_key(version: str) -> tuple:
    """Sort key following semver precedence (a prerelease sorts before its release)."""
    match = SEMVER_RE.match(version)
    if match is None:
        raise ValueError(f"not a semver version: {version!r}")
    core = tuple(int(part) for part in match.group(1, 2, 3))
    prerelease = match.group(4)
    if prerelease is None:
        return core + ((1,),)
    identifiers = tuple(
        (0, int(part), "") if part.isdigit() else (1, 0, part) for part in prerelease.split(".")
    )
    return core + ((0, identifiers),)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_manifest(data: bytes, label: str) -> dict:
    """Device-side checks ("can this app run it"); the backend CLI validates the full contract."""
    if len(data) > MAX_MANIFEST_BYTES:
        raise RepoError(f"{label}: manifest is {len(data)} bytes (limit {MAX_MANIFEST_BYTES}).")
    try:
        manifest = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RepoError(f"{label}: not valid UTF-8 JSON ({exc}).") from exc
    if not isinstance(manifest, dict):
        raise RepoError(f"{label}: the manifest must be a JSON object.")
    missing = [field for field in REQUIRED_FIELDS if field not in manifest]
    if missing:
        raise RepoError(f"{label}: missing required fields: {', '.join(missing)}.")
    key = manifest["key"]
    if not isinstance(key, str) or not KEY_RE.match(key):
        raise RepoError(f"{label}: key {key!r} does not match {KEY_RE.pattern}.")
    if key in RESERVED_KEYS:
        raise RepoError(f"{label}: key {key!r} is reserved.")
    if not isinstance(manifest["contractVersion"], int) or isinstance(manifest["contractVersion"], bool):
        raise RepoError(f"{label}: contractVersion must be an integer.")
    if not is_semver(manifest["version"]):
        raise RepoError(f"{label}: version {manifest['version']!r} is not semver MAJOR.MINOR.PATCH[-prerelease].")
    rights = manifest.get("rights")
    if rights is not None and (not isinstance(rights, dict) or not isinstance(rights.get("basis"), str)):
        raise RepoError(f"{label}: rights, when present, must be an object with a string basis.")
    for field in ("kinds", "langs"):
        value = manifest[field]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise RepoError(f"{label}: {field} must be a list of strings.")
    return manifest


def check_icon(path: Path) -> bytes:
    data = path.read_bytes()
    label = path.relative_to(ROOT)
    if len(data) > MAX_ICON_BYTES:
        raise RepoError(f"{label}: icon is {len(data)} bytes (limit {MAX_ICON_BYTES}).")
    if not data.startswith(PNG_SIGNATURE):
        raise RepoError(f"{label}: not a PNG file.")
    return data


def load_sources() -> list[Source]:
    """Every sources/<key>/source.json, sorted by key; the directory name must equal the manifest key."""
    sources = []
    for path in sorted(SOURCES_DIR.glob("*/source.json")):
        label = str(path.relative_to(ROOT))
        data = path.read_bytes()
        manifest = parse_manifest(data, label)
        if manifest["key"] != path.parent.name:
            raise RepoError(f"{label}: key {manifest['key']!r} must equal its directory name {path.parent.name!r}.")
        sources.append(Source(key=manifest["key"], directory=path.parent, manifest_bytes=data, manifest=manifest))
    if len(sources) > MAX_SOURCES:
        raise RepoError(f"{len(sources)} sources (limit {MAX_SOURCES}).")
    return sorted(sources, key=lambda source: source.key)


_INLINE_MARKDOWN = (
    (re.compile(r"!?\[([^\]]*)\]\([^)]*\)"), r"\1"),  # links and images: keep the text
    (re.compile(r"(\*\*|__)(.+?)\1"), r"\2"),  # bold
    (re.compile(r"`([^`]*)`"), r"\1"),  # code
)


def first_changelog_section(path: Path) -> tuple[str, str]:
    """(heading, plain-text body) of the first `## ` section of a CHANGELOG.md."""
    heading = None
    body: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if heading is not None:
                break
            heading = line[3:].strip()
            continue
        if heading is not None:
            for pattern, replacement in _INLINE_MARKDOWN:
                line = pattern.sub(replacement, line)
            body.append(line.rstrip())
    label = path.relative_to(ROOT)
    if heading is None:
        raise RepoError(f"{label}: no '## <version>' section.")
    text = "\n".join(body).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text:
        raise RepoError(f"{label}: the first section ({heading}) is empty.")
    return heading, text

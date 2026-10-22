#!/usr/bin/env bash
# Checks the repository:
#   1. manifest versions are semver, and bumped when a manifest changed since VOVO_BASE_REF (default HEAD);
#   2. repo.json is up to date (python3 scripts/build-index.py regenerates it);
#   3. every manifest is valid for the backend engine (v1 contract).
# Backend: the sibling ../backend or ../vovoscan-be, otherwise VOVOSCAN_BE=<path to the vovoscan-be repository>.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/check-versions.py
python3 scripts/build-index.py --check
backend="${VOVOSCAN_BE:-}"
for candidate in ../backend ../vovoscan-be; do
  [[ -z "$backend" && -f "$candidate/pyproject.toml" ]] && backend="$candidate"
done
if [[ -z "$backend" ]]; then
  echo "Backend not found: clone vovoscan-be next to this repository or set VOVOSCAN_BE." >&2
  exit 2
fi
# The schema here must be the engine's schema.
if ! cmp -s schema/source.schema.json "$backend/src/vovoscan/features/catalog/domain/contract/source.schema.json"; then
  echo "schema/source.schema.json differs from the backend contract: copy it again." >&2
  exit 1
fi
manifests=("$PWD"/sources/*/source.json)
(cd "$backend" && uv run --quiet vovoscan check-source "${manifests[@]}")

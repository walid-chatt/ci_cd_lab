#!/usr/bin/env bash
# Same script locally and on the CI runner. No deployment happens here.
set -euo pipefail

# Make paths work even if you launch the script from outside this folder.
cd "$(dirname "$0")/.."

uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
uv run --locked python pipeline.py

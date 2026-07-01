#!/usr/bin/env bash

set -eu

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
CACHE_DIR="${UV_CACHE_DIR:-$ROOT_DIR/.cache/uv}"
FALLBACK_PYTHON="${PBO_TEST_PYTHON:-}"
FALLBACK_RUFF="${PBO_RUFF_BIN:-}"
MIN_PYTHON="3.12"

mkdir -p "$CACHE_DIR"

check_python_version() {
  python_bin="$1"
  detected_version="$("$python_bin" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  if [ "$detected_version" != "$MIN_PYTHON" ] && [ "$detected_version" \< "$MIN_PYTHON" ]; then
    echo "Fallback python $python_bin is $detected_version but $MIN_PYTHON+ is required." >&2
    return 1
  fi
}

run_fallback_pytest() {
  python_bin="$1"
  check_python_version "$python_bin"
  PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" "$python_bin" -m pytest
}

echo "Using UV cache: $CACHE_DIR"
echo "+ uv run pytest"
if UV_CACHE_DIR="$CACHE_DIR" uv run pytest; then
  :
elif [ -n "$FALLBACK_PYTHON" ]; then
  echo "uv run pytest failed, using fallback python: $FALLBACK_PYTHON"
  run_fallback_pytest "$FALLBACK_PYTHON"
elif command -v pytest >/dev/null 2>&1; then
  echo "uv run pytest failed, using fallback pytest from PATH"
  pytest_python="$(command -v python3 || command -v python)"
  if [ -z "$pytest_python" ]; then
    echo "No python interpreter found for pytest fallback." >&2
    exit 1
  fi
  run_fallback_pytest "$pytest_python"
else
  exit 1
fi

echo "+ uv run ruff check ."
if UV_CACHE_DIR="$CACHE_DIR" uv run ruff check .; then
  :
elif [ -n "$FALLBACK_RUFF" ]; then
  echo "uv run ruff check . failed, using fallback ruff: $FALLBACK_RUFF"
  "$FALLBACK_RUFF" check "$ROOT_DIR"
elif command -v ruff >/dev/null 2>&1; then
  echo "uv run ruff check . failed, using fallback ruff from PATH"
  ruff check "$ROOT_DIR"
else
  exit 1
fi

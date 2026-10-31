#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PLAYFORGE_PYTHON:-python3}"
exec "$PY" "$DIR/main.py" "$@"

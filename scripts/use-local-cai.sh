#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT/.venv/bin/python"
DEFAULT_ENV_FILE="$HOME/.config/cai/.env"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Erro: interpretador local nao encontrado: $PYTHON_BIN" >&2
    echo "Execute scripts/bootstrap-local-venv.sh quando houver rede." >&2
    exit 1
fi

if [[ -z "${CAI_ENV_FILE:-}" && -r "$DEFAULT_ENV_FILE" ]]; then
    export CAI_ENV_FILE="$DEFAULT_ENV_FILE"
fi

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$PYTHON_BIN" -m cai.cli "$@"

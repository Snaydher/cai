#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3.13}"

cd "$ROOT"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Erro: interpretador nao encontrado: $PYTHON_BIN" >&2
    echo "Defina PYTHON_BIN=python3.12 ou outro interpretador valido e tente novamente." >&2
    exit 1
fi

"$PYTHON_BIN" -m venv --clear "$VENV_DIR"
"$VENV_DIR/bin/python" -m ensurepip --upgrade
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -e .

cat <<EOF

Venv local pronto.

Use:
  export CAI_ENV_FILE="\$HOME/.config/cai/.env"
  "$ROOT/scripts/use-local-cai.sh"

Opcional no shell rc:
  export PATH="$ROOT/.venv/bin:\$PATH"
  export CAI_ENV_FILE="\$HOME/.config/cai/.env"
EOF

#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Uso: $0 <host> [output-dir]" >&2
    exit 1
fi

TARGET="$1"
OUTPUT_DIR="${2:-scan-results}"
STAMP="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="$OUTPUT_DIR/$TARGET-$STAMP"

if ! command -v nmap >/dev/null 2>&1; then
    echo "Erro: nmap nao encontrado no PATH." >&2
    exit 1
fi

mkdir -p "$RUN_DIR"

cat <<EOF
Varredura basica autorizada
Alvo: $TARGET
Saida: $RUN_DIR
EOF

nmap -Pn -T4 --top-ports 1000 "$TARGET" -oA "$RUN_DIR/top-ports"
nmap -Pn -T4 -sV -sC "$TARGET" -oA "$RUN_DIR/services-default"
nmap -Pn -T4 -O "$TARGET" -oA "$RUN_DIR/os-detect" || true

echo "Arquivos gerados em: $RUN_DIR"

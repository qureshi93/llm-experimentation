#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a
[ $# -ge 1 ] || { echo "usage: $0 FILE.csv|json|jsonl ..."; exit 1; }
PYTHONPATH=. python -m src.ingestion.ingest_baseline "$@"

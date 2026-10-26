#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a
export PYTHONPATH=.
python -m src.enrichment.worker
[ "${EMBED:-0}" = "1" ] && python -m src.enrichment.generate_aeo_embeddings

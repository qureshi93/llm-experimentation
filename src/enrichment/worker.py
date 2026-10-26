import logging
import os
import time

from src.enrichment.active_enricher import run_once

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    interval = int(os.environ.get("ENRICH_INTERVAL_SECONDS", "300"))
    once = os.environ.get("ENRICH_ONCE") == "1"
    while True:
        n = run_once()
        logging.info("enriched %d companies", n)
        if once:
            break
        time.sleep(interval if n == 0 else 1)

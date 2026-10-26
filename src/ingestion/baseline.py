import csv
import json
from pathlib import Path

from src.db.client import get_pool
from src.utils.domains import normalize_domain

PLATFORMS = {"SHOPIFY", "WOOCOMMERCE", "MAGENTO", "CUSTOM", "OTHER"}
DOMAIN_KEYS = ("domain", "url", "website", "host", "target_uri")

UPSERT = """
INSERT INTO companies (domain, company_name, country_code, ecom_platform, estimated_monthly_traffic)
VALUES (%s, %s, 'HK', %s, %s)
ON CONFLICT (domain) DO UPDATE SET
  company_name = COALESCE(EXCLUDED.company_name, companies.company_name),
  country_code = 'HK',
  ecom_platform = CASE WHEN EXCLUDED.ecom_platform <> 'OTHER'
                       THEN EXCLUDED.ecom_platform ELSE companies.ecom_platform END,
  estimated_monthly_traffic = COALESCE(EXCLUDED.estimated_monthly_traffic, companies.estimated_monthly_traffic),
  updated_at = now()
"""


def read_records(path: Path):
    """Yield dicts from .csv, .json (array), or .jsonl/.ndjson files."""
    suffix = path.suffix.lower()
    with path.open(newline="", encoding="utf-8") as f:
        if suffix == ".csv":
            yield from csv.DictReader(f)
        elif suffix == ".json":
            data = json.load(f)
            yield from (data.get("domains", data.get("results", [])) if isinstance(data, dict) else data)
        elif suffix in (".jsonl", ".ndjson"):
            for line in f:
                if line.strip():
                    yield json.loads(line)
        else:
            raise ValueError(f"Unsupported file type: {path}")


def to_row(rec: dict):
    rec = {str(k).lower(): v for k, v in rec.items()}
    domain = next((normalize_domain(rec[k]) for k in DOMAIN_KEYS if rec.get(k)), None)
    if not domain:
        return None
    name = rec.get("company_name") or rec.get("name") or rec.get("title") or None
    platform = str(rec.get("platform") or rec.get("ecom_platform") or "OTHER").upper()
    traffic = rec.get("estimated_monthly_traffic") or rec.get("estimated_visits") or rec.get("monthly_traffic")
    try:
        traffic = int(float(traffic)) if traffic not in (None, "") else None
    except (TypeError, ValueError):
        traffic = None
    return domain, name, platform if platform in PLATFORMS else "OTHER", traffic


def ingest_file(path: str) -> tuple[int, int]:
    ok = skipped = 0
    with get_pool().connection() as conn, conn.cursor() as cur:
        for rec in read_records(Path(path)):
            row = to_row(rec)
            if row is None:
                skipped += 1
                continue
            cur.execute(UPSERT, row)
            ok += 1
    return ok, skipped

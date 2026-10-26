import logging

import httpx
from psycopg.types.json import Jsonb

from src.db.client import get_pool
from src.utils import html as H

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HKMarketingIntelBot/1.0)"}
STALE_SQL = """SELECT id, domain FROM companies
WHERE updated_at < now() - interval '30 days' ORDER BY updated_at LIMIT %s"""


def fetch(client: httpx.Client, url: str) -> str:
    try:
        r = client.get(url)
        return r.text if r.status_code == 200 else ""
    except httpx.HTTPError:
        return ""


def enrich_company(client: httpx.Client, domain: str) -> dict:
    base = f"https://{domain}"
    pages = {u: fetch(client, u) for u in (base + "/", base + "/contact")}
    combined = "\n".join(pages.values())
    home = pages[base + "/"]
    emails = set()
    for h in pages.values():
        if h:
            emails |= H.extract_emails(h)
    socials = {}
    for u, h in pages.items():
        if h:
            socials = {**H.extract_social_links(h, u), **socials}
    return {
        "reachable": bool(combined.strip()),
        "metadata": H.extract_metadata(home) if home else {},
        "socials": socials,
        "tech": H.detect_tech(combined),
        "platform": H.detect_platform(combined),
        "emails": sorted(emails),
        "text": H.visible_text(home) if home else "",
    }


def save(cur, company_id, domain: str, info: dict) -> None:
    stack = {**info["tech"], "socials": info["socials"], "metadata": info["metadata"]}
    cur.execute(
        """UPDATE companies SET tech_stack = %s,
             company_name = COALESCE(company_name, %s),
             ecom_platform = CASE WHEN %s::text IS NOT NULL THEN %s::ecom_platform ELSE ecom_platform END,
             updated_at = now() WHERE id = %s""",
        (Jsonb(stack), info["metadata"].get("og_site_name") or info["metadata"].get("title"),
         info["platform"], info["platform"], company_id),
    )
    for email in info["emails"]:
        cur.execute(
            """INSERT INTO company_contacts (company_id, full_name, email)
               VALUES (%s, %s, %s) ON CONFLICT (company_id, email) DO NOTHING""",
            (company_id, email.split("@")[0], email),
        )
    if info["text"]:
        cur.execute(
            """INSERT INTO aeo_audits (company_id, raw_scraped_html_text)
               SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM aeo_audits WHERE company_id = %s)""",
            (company_id, info["text"], company_id),
        )


def run_once(batch: int = 50) -> int:
    done = 0
    with httpx.Client(headers=HEADERS, timeout=10, follow_redirects=True) as client, \
            get_pool().connection() as conn:
        rows = conn.execute(STALE_SQL, (batch,)).fetchall()
        for cid, domain in rows:
            try:
                info = enrich_company(client, domain)
                with conn.cursor() as cur:
                    if info["reachable"]:
                        save(cur, cid, domain, info)
                    else:  # bump timestamp so unreachable sites don't block the queue
                        cur.execute("UPDATE companies SET updated_at = now() WHERE id = %s", (cid,))
                conn.commit()
                done += 1
            except Exception:
                conn.rollback()
                log.exception("enrichment failed for %s", domain)
    return done

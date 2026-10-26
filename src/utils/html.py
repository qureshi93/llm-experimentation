import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_BAD_EMAIL_SUFFIX = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js")
SOCIALS = {
    "instagram": "instagram.com",
    "facebook": "facebook.com",
    "xiaohongshu": ("xiaohongshu.com", "xhslink.com"),
}
TECH_SIGNATURES = {
    "meta_pixel": ("connect.facebook.net", "fbq("),
    "google_tag_manager": ("googletagmanager.com/gtm.js", "GTM-"),
    "google_analytics": ("google-analytics.com", "gtag/js"),
    "klaviyo": ("klaviyo.com",),
    "hotjar": ("hotjar.com",),
}


def extract_emails(html: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    found = set(EMAIL_RE.findall(soup.get_text(" ")))
    for a in soup.select('a[href^="mailto:"]'):
        found.update(EMAIL_RE.findall(a["href"].split("?")[0]))
    return {e.lower() for e in found if not e.lower().endswith(_BAD_EMAIL_SUFFIX)}


def extract_social_links(html: str, base_url: str = "") -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    out: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        for name, hosts in SOCIALS.items():
            hosts = (hosts,) if isinstance(hosts, str) else hosts
            if name not in out and any(h in href.lower() for h in hosts):
                out[name] = href
    return out


def extract_metadata(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    def meta(**attrs):
        tag = soup.find("meta", attrs=attrs)
        return tag.get("content", "").strip() if tag else None

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    return {
        "title": title,
        "description": meta(name="description"),
        "og_site_name": meta(property="og:site_name"),
    }


def detect_tech(html: str) -> dict[str, bool]:
    return {k: any(s in html for s in sigs) for k, sigs in TECH_SIGNATURES.items()}


def detect_platform(html: str) -> str | None:
    low = html.lower()
    if "cdn.shopify.com" in low or "shopify.theme" in low:
        return "SHOPIFY"
    if "woocommerce" in low or "wp-content" in low:
        return "WOOCOMMERCE"
    if "mage/cookies" in low or "magento" in low:
        return "MAGENTO"
    return None


def visible_text(html: str, limit: int = 20000) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ")).strip()[:limit]

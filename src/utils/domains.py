import re
from urllib.parse import urlsplit

_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9-]{1,63}\.)+[a-z]{2,63}$")


def normalize_domain(raw) -> str | None:
    """Strip scheme, www., path, port and trailing slashes. Returns None if invalid."""
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip().lower()
    if "://" not in s:
        s = "//" + s
    try:
        host = urlsplit(s).hostname or ""
    except ValueError:
        return None
    host = host.rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host if _DOMAIN_RE.match(host) else None

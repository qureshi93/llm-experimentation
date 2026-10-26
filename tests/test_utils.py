from src.ingestion.baseline import to_row
from src.utils.domains import normalize_domain
from src.utils.html import extract_emails, extract_social_links


def test_normalize():
    assert normalize_domain("https://www.Example.com.hk/") == "example.com.hk"
    assert normalize_domain("www.shop.hk/path?q=1") == "shop.hk"
    assert normalize_domain("not a domain") is None


def test_row():
    assert to_row({"Domain": "http://www.a.hk/", "platform": "shopify", "estimated_visits": "1200.0"}) == ("a.hk", None, "SHOPIFY", 1200)


def test_html():
    h = '<a href="mailto:Hi@a.hk">x</a><a href="https://instagram.com/a">i</a>'
    assert extract_emails(h) == {"hi@a.hk"}
    assert extract_social_links(h)["instagram"] == "https://instagram.com/a"

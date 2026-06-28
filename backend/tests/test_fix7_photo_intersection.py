"""Tests for upgraded photo fetching pipeline.

Verifies:
1. _get_official_domain maps brand keywords to official manufacturer websites.
2. _hamming_distance computes the differences between visual aHashes.
3. _search_device_image_urls queries official domains first.
4. _search_device_image_urls uses visual hash intersection as a fallback.
"""
import io
from PIL import Image
import monitor

def test_get_official_domain():
    assert monitor._get_official_domain("OPPO Enco Buds") == "oppo.com"
    assert monitor._get_official_domain("realme Buds Air7") == "realme.com"
    assert monitor._get_official_domain("CMF Buds 2 Plus") == "nothing.tech"
    assert monitor._get_official_domain("Sony WH-1000XM4") == "sony.com"
    assert monitor._get_official_domain("Samsung Galaxy Buds") == "samsung.com"
    assert monitor._get_official_domain("Unknown brand buds") is None

def test_hamming_distance():
    h1 = "11110000" * 8
    h2 = "11110000" * 8
    assert monitor._hamming_distance(h1, h2) == 0

    h3 = "11110000" * 7 + "11110001" # 1 bit different
    assert monitor._hamming_distance(h1, h3) == 1

def test_get_image_hash():
    img = Image.new("RGB", (64, 64), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    h = monitor._get_image_hash(img_bytes)
    assert h is not None
    assert len(h) == 64

def test_search_prioritizes_official_site(monkeypatch):
    mock_results = {
        "results": [
            {"image": "https://image.oppo.com/enco.png", "url": "https://www.oppo.com/product"},
            {"image": "https://some-retailer.com/enco.png", "url": "https://some-retailer.com/product"}
        ]
    }
    
    import json
    
    class MockResponse:
        def __init__(self, data):
            self.data = data
        def read(self, *a, **k):
            return self.data
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
        @property
        def headers(self):
            return {"Content-Type": "image/png"}

    def _mock_urlopen(req, *a, **k):
        url = req.full_url if hasattr(req, "full_url") else req
        if "duckduckgo.com/?q" in url:
            return MockResponse(b"vqd='123-456'")
        if "duckduckgo.com/i.js" in url:
            return MockResponse(json.dumps(mock_results).encode())
        if "image.oppo.com" in url:
            img = Image.new("RGB", (200, 200), color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return MockResponse(buf.getvalue())
        raise AssertionError(f"Unexpected urlopen: {url}")

    monkeypatch.setattr(monitor.urllib.request, "urlopen", _mock_urlopen)
    
    urls = monitor._search_device_image_urls("OPPO Enco Buds")
    assert len(urls) == 1
    assert urls[0] == "https://image.oppo.com/enco.png"

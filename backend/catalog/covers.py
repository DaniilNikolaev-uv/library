from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import urlopen

PLACEHOLDER_COVER_URL = "https://placehold.co/200x300?text=No+Cover"


def get_cover_url(isbn: str) -> str:
    normalized = (isbn or "").replace("-", "").replace(" ", "").strip()
    if not normalized:
        return PLACEHOLDER_COVER_URL
    return f"https://covers.openlibrary.org/b/isbn/{normalized}-M.jpg"


def lookup_isbn(*, title: str, author: str | None = None) -> str | None:
    query = " ".join(x for x in [title.strip(), (author or "").strip()] if x).strip()
    if not query:
        return None

    params = urlencode({"q": query, "limit": 1})
    url = f"https://openlibrary.org/search.json?{params}"
    try:
        with urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    docs = payload.get("docs") or []
    if not docs:
        return None
    isbn_list = docs[0].get("isbn") or []
    if not isbn_list:
        return None
    return str(isbn_list[0]).strip() or None

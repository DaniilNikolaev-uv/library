from __future__ import annotations

PLACEHOLDER_COVER_URL = "https://placehold.co/200x300?text=No+Cover"


def get_cover_url(isbn: str) -> str:
    normalized = (isbn or "").replace("-", "").replace(" ", "").strip()
    if not normalized:
        return PLACEHOLDER_COVER_URL
    return f"https://covers.openlibrary.org/b/isbn/{normalized}-M.jpg"

"""Stable naming helpers for generated pages."""

from __future__ import annotations

import re
import unicodedata


def slugify(value: str, *, fallback: str = "item") -> str:
    """Convert a human or identifier string into a stable ASCII slug."""
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or fallback


class UniqueSlugger:
    """Allocate deterministic unique slugs within a namespace."""

    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def allocate(self, value: str, *, fallback: str = "item") -> str:
        """Return a slug, adding a numeric suffix after the first use."""
        base = slugify(value, fallback=fallback)
        count = self._counts.get(base, 0) + 1
        self._counts[base] = count
        return base if count == 1 else f"{base}-{count}"


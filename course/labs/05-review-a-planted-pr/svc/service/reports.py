"""Report generation. Nothing to do with rate limiting."""

from __future__ import annotations


def summarise(tenant_id: str, rows: list[str]) -> dict[str, object]:
    return {"tenant": tenant_id, "count": len(rows), "generated": True}

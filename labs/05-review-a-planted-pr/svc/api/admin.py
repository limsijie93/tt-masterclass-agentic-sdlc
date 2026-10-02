"""The internal admin API. Shares limit_for with the public middleware."""

from __future__ import annotations

from svc.service.limits import limit_for


def allowance() -> int | None:
    """Internal callers are not rate limited. See limit_for."""
    return limit_for("internal")

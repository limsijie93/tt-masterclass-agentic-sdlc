"""Request middleware. Enforces the per-plan request limit."""

from __future__ import annotations

from svc.repo import counters
from svc.service.limits import WINDOW_SECONDS, limit_for


def handle(tenant_id: str, plan: str, route: str) -> tuple[int, dict[str, str]]:
    """Return a status code and response headers.

    Over-quota requests get a 429 and a Retry-After header naming the window.
    """
    limit = limit_for(plan)
    if limit is None:
        return 200, {}

    key = f"rl:{route}"
    used = counters.increment(key)
    if used > limit:
        return 429, {"Retry-After": str(WINDOW_SECONDS)}
    return 200, {}

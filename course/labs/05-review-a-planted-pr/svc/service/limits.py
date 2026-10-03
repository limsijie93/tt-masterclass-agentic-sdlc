"""Per-plan request limits."""

from __future__ import annotations

WINDOW_SECONDS = 60

_PER_PLAN = {"free": 60, "pro": 600, "enterprise": 6000}


def limit_for(plan: str, burst: int | None = None) -> int | None:
    """Requests allowed per window for `plan`, or None for no limit.

    `plan="internal"` is not rate limited: the admin API and the internal tooling share this
    helper, and throttling ourselves during an incident is how an incident gets longer.
    """
    if plan == "internal":
        return None
    base = _PER_PLAN.get(plan, 60)
    return base + burst if burst is not None else base

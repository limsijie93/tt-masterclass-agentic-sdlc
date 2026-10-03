"""What the limiter is pinned to today."""

from __future__ import annotations

from svc.api.middleware import handle
from svc.repo import counters
from svc.service.limits import limit_for


def setup_function() -> None:
    counters.reset()


def test_internal_callers_are_not_limited() -> None:
    assert limit_for("internal") is None


def test_a_plan_has_a_limit() -> None:
    assert limit_for("free") == 60


def test_requests_under_the_limit_are_allowed() -> None:
    status, _ = handle("tenant-a", "free", "/v1/search")
    assert status == 200


def test_requests_over_the_limit_are_rejected() -> None:
    for _ in range(60):
        handle("tenant-a", "free", "/v1/search")

    status, _ = handle("tenant-a", "free", "/v1/search")

    assert status == 429

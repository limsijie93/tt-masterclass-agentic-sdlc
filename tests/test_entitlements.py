"""The entitlement tests — both acceptance criteria, and the regression for finding 1.

`course/tickets/PROJ-207/07-pr-body.md` cites two lines of this file as where the criteria are
verified: line 48 for criterion 1 and line 72 for criterion 2.
`tests/test_example_consistency.py` asserts those citations, so moving a test here fails the
build until the artifact is updated to match it.

ON THE CLOCK. Criterion 1 is written at sixty seconds, and a test that waited sixty seconds
would be a test somebody deletes on a Friday. `resolve_entitlements` takes a `clock` so the
expiry branch runs in microseconds against a number the test controls. What is verified is the
branch and the boundary, not the wall clock — and that distinction is worth stating rather than
hiding behind a green run.
"""

from __future__ import annotations

import sqlite3

from myapp.api.entitlements import views
from myapp.repo.entitlements import queries
from myapp.repo.exports import queries as export_queries
from myapp.service.billing import upgrade
from myapp.service.entitlements import service

#: From answer 2 of the interrogation. The number in the criterion, not a target.
TTL_SECONDS = 60

#: A paying account, with rows.
ENTITLED_ACCOUNT = 501

#: An account whose entitlement rows have not been written yet. The state finding 1 is about.
UNWRITTEN_ACCOUNT = 502

FLAG = "advanced_export"


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(export_queries.SCHEMA)
    connection.executescript(queries.SCHEMA)
    connection.execute("INSERT INTO account (id, name) VALUES (?, ?)", (ENTITLED_ACCOUNT, "paid"))
    connection.execute("INSERT INTO account (id, name) VALUES (?, ?)", (UNWRITTEN_ACCOUNT, "new"))
    queries.seed(connection, ENTITLED_ACCOUNT, (FLAG,))
    service._CACHE.clear()
    return connection


def test_an_entitlement_change_is_visible_within_the_ttl() -> None:
    """Criterion 1 · cited by 07-pr-body.md as `tests/test_entitlements.py:48`.

    THE BOUNDARY IS THE TEST. The cache is checked with `now - resolved_at < TTL`, so the
    interesting values are TTL-1 (still cached) and TTL (expired). A test that only probed
    zero and a thousand would pass against `<=`, against `<`, and against a TTL of any size —
    it would assert that caching exists, not that it expires when the criterion says.
    """
    connection = _connection()
    clock = [1000.0]

    flags, cached = service.resolve_entitlements(connection, ENTITLED_ACCOUNT, lambda: clock[0])
    assert flags == frozenset({FLAG})
    assert cached is False

    clock[0] += TTL_SECONDS - 1
    _, cached = service.resolve_entitlements(connection, ENTITLED_ACCOUNT, lambda: clock[0])
    assert cached is True, "inside the window the answer must come from cache"

    clock[0] += 1
    _, cached = service.resolve_entitlements(connection, ENTITLED_ACCOUNT, lambda: clock[0])
    assert cached is False, "at sixty seconds the cache must have expired"


def test_an_unentitled_account_gets_403_and_an_upgrade_url() -> None:
    """Criterion 2 · cited by 07-pr-body.md as `tests/test_entitlements.py:72`."""
    connection = _connection()
    response = views.feature_view(connection, ENTITLED_ACCOUNT, "sso")
    assert response.status == 403
    assert response.granted is False
    assert response.upgrade_url == "/billing/upgrade?feature=sso"


def test_an_entitled_account_gets_200_and_no_upgrade_url() -> None:
    connection = _connection()
    response = views.feature_view(connection, ENTITLED_ACCOUNT, FLAG)
    assert response.status == 200
    assert response.granted is True
    assert response.upgrade_url is None


def test_an_account_with_no_rows_is_refused_by_the_gate() -> None:
    """The regression for finding 1.

    `has_feature` defaults to True and the view passes False explicitly. If someone deletes
    that argument to tidy the call site, the gate starts handing an unpaid feature to every
    account whose entitlements have not been written yet, and this is the test that objects.
    """
    connection = _connection()
    response = views.feature_view(connection, UNWRITTEN_ACCOUNT, FLAG)
    assert response.status == 403


def test_the_upgrade_page_still_fails_open_for_the_same_account() -> None:
    """The other half of finding 1, and the reason the shared default was not simply flipped.

    Both callers reach the same helper and want opposite behaviour when the answer is unknown.
    The gate must refuse. This page must not nag someone about a feature they may already have.
    Flipping the default would have fixed the first and silently changed the second.
    """
    connection = _connection()
    offers = upgrade.offers_for(connection, UNWRITTEN_ACCOUNT)
    assert all(offer.already_held for offer in offers)


def test_a_plan_change_drops_the_cache_rather_than_waiting_for_the_ttl() -> None:
    """The refutation of finding 3, executable.

    The review says a revoked entitlement is served for up to sixty seconds. It would be, if
    nothing invalidated. `change_plan` does, so the next read goes to the database.
    """
    connection = _connection()
    clock = [1000.0]
    service.resolve_entitlements(connection, ENTITLED_ACCOUNT, lambda: clock[0])

    connection.execute("DELETE FROM entitlement WHERE account_id = ?", (ENTITLED_ACCOUNT,))
    upgrade.change_plan(connection, ENTITLED_ACCOUNT, "free")

    flags, cached = service.resolve_entitlements(connection, ENTITLED_ACCOUNT, lambda: clock[0])
    assert cached is False, "a plan change must drop the cache, not wait for the TTL"
    assert flags == frozenset()

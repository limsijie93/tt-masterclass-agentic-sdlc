"""Entitlement resolution, with the freshness promise the criteria are written against.

The middle layer, and the only one allowed to reach `myapp.repo`. `myapp.api` must go through
here — the obvious way to make an entitlement check fast is to read the entitlements table
directly from the view, which is a layering violation, and `.importlinter` blocks it.

WHAT PROJ-207 CHANGED, AND WHY THE SIGNATURE LOOKS LIKE THIS

Before the ticket, entitlements were read once at login and held for the session. That is what
let a customer keep a feature after downgrading, and keep seeing it until they logged out.

The fix resolves server-side on every request, behind a short cache. `CACHE_TTL_SECONDS` is 60
because acceptance criterion 1 says sixty and not because sixty is a good number in general.

`has_feature` takes `default`, and it defaults to `True`. That is FAIL-OPEN: an account whose
entitlements cannot be read gets the feature. It is the footgun finding 1 of
course/tickets/PROJ-207/08-review.md identified, on the grounds that
`tooling/myapp/service/billing/upgrade.py:44` calls the same helper and was not touched.

The default is still `True`, and that is deliberate for the same reason
`myapp/service/exports/service.py` still defaults `chunk_size` to `None`: the lesson outlives
the fix. What guards it instead is .semgrep/fail-open-entitlement.yml, which fails the build on
any call site that does not pass `default` explicitly. That rule exists because a human caught
this twice — PROJ-142 first, this ticket second — and the second sighting is what made it a
rule rather than a note.
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass

from myapp.repo.entitlements import queries

#: From acceptance criterion 1: an entitlement change is visible within sixty seconds.
CACHE_TTL_SECONDS = 60

#: account_id -> (resolved_at, flags). Process-local and deliberately dumb; a shared cache is
#: a different ticket and would need an invalidation story across processes.
_CACHE: dict[int, tuple[float, frozenset[str]]] = {}


@dataclass(frozen=True)
class Entitlement:
    """The answer to one question: may this account use this flag, and how do we know."""

    account_id: int
    flag: str
    granted: bool
    resolved_from_cache: bool


def _now() -> float:
    return time.monotonic()


def invalidate(account_id: int) -> None:
    """Drop this account's cached entitlements.

    THE HOOK THE REVIEWER MISSED. Finding 3 in course/tickets/PROJ-207/08-review.md: the cache is
    stale-unsafe because a revoked entitlement is served for up to the TTL. That would be true
    if nothing called this. `myapp/service/billing/upgrade.py` calls it on every plan change,
    so a revocation is visible on the next request rather than in sixty seconds.
    """
    _CACHE.pop(account_id, None)


def resolve_entitlements(
    connection: sqlite3.Connection,
    account_id: int,
    clock: Callable[[], float] = _now,
) -> tuple[frozenset[str], bool]:
    """This account's flags, and whether the answer came from cache.

    The clock is injected so the expiry branch can be tested without sleeping for a minute.
    A test that sleeps is a test people delete.
    """
    cached = _CACHE.get(account_id)
    now = clock()
    if cached is not None and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1], True
    flags = queries.fetch_entitlements(connection, account_id)
    _CACHE[account_id] = (now, flags)
    return flags, False


def has_feature(
    connection: sqlite3.Connection,
    account_id: int,
    flag: str,
    default: bool = True,
) -> bool:
    """Whether this account may use this flag.

    `default` is returned when the account has NO entitlement rows at all — not when it has
    rows and this flag is absent from them. Pass it explicitly;
    .semgrep/fail-open-entitlement.yml fails the build if you do not.
    """
    flags, _ = resolve_entitlements(connection, account_id)
    if not flags and queries.count_entitlements(connection, account_id) == 0:
        return default
    return flag in flags

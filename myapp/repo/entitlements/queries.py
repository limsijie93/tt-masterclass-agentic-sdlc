"""Entitlement rows, read from the database and nothing else.

The bottom layer. No caching here on purpose: a cache in the data layer is invisible to the
service that owns the freshness promise, and PROJ-207's acceptance criterion 1 is about
freshness. The cache lives one layer up, where the TTL is legible beside the criterion it
satisfies.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

SCHEMA = """
CREATE TABLE IF NOT EXISTS entitlement (
    id         INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES account(id),
    flag       TEXT NOT NULL,
    plan       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS entitlement_account ON entitlement(account_id);
CREATE TABLE IF NOT EXISTS account_plan (
    account_id INTEGER PRIMARY KEY REFERENCES account(id),
    plan       TEXT NOT NULL
);
"""

#: Seeded at account creation. An account with no rows at all is not "entitled to nothing" —
#: it is an account whose entitlements have not been written yet, and the difference is the
#: whole of finding 1 in example/PROJ-207/08-review.md.
BOOTSTRAP_PLAN = "free"


@dataclass(frozen=True)
class EntitlementRow:
    """One feature an account has paid for."""

    account_id: int
    flag: str
    plan: str


def fetch_entitlements(connection: sqlite3.Connection, account_id: int) -> frozenset[str]:
    """Every flag this account is entitled to, right now.

    Returns an empty set both for an account entitled to nothing and for an account that has
    no rows yet. The caller cannot tell those apart from the return value, which is exactly
    the ambiguity the fail-open default turns into a bug.
    """
    cursor = connection.execute(
        "SELECT flag FROM entitlement WHERE account_id = ?",
        (account_id,),
    )
    return frozenset(row[0] for row in cursor.fetchall())


def count_entitlements(connection: sqlite3.Connection, account_id: int) -> int:
    """How many rows exist for this account. Distinguishes 'none' from 'not written yet'."""
    cursor = connection.execute(
        "SELECT COUNT(*) FROM entitlement WHERE account_id = ?",
        (account_id,),
    )
    return int(cursor.fetchone()[0])


def seed(connection: sqlite3.Connection, account_id: int, flags: tuple[str, ...]) -> None:
    """Give an account exactly these flags. No rows at all is a different state — see
    `count_entitlements` and finding 1 of example/PROJ-207/08-review.md."""
    connection.executemany(
        "INSERT INTO entitlement (account_id, flag, plan) VALUES (?, ?, ?)",
        [(account_id, flag, BOOTSTRAP_PLAN) for flag in flags],
    )

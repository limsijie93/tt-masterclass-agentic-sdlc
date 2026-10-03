"""Entitlement rows, read from the database and nothing else."""

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

#: The plan every account starts on.
BOOTSTRAP_PLAN = "free"


@dataclass(frozen=True)
class EntitlementRow:
    """One feature an account has paid for."""

    account_id: int
    flag: str
    plan: str


def fetch_entitlements(connection: sqlite3.Connection, account_id: int) -> frozenset[str]:
    """Every flag this account is entitled to."""
    cursor = connection.execute(
        "SELECT flag FROM entitlement WHERE account_id = ?",
        (account_id,),
    )
    return frozenset(row[0] for row in cursor.fetchall())


def seed(connection: sqlite3.Connection, account_id: int, flags: tuple[str, ...]) -> None:
    """Give an account exactly these flags."""
    connection.executemany(
        "INSERT INTO entitlement (account_id, flag, plan) VALUES (?, ?, ?)",
        [(account_id, flag, BOOTSTRAP_PLAN) for flag in flags],
    )

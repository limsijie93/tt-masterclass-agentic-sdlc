"""The upgrade page's view of what an account is missing."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from myapp.service.entitlements import service

#: The flags the upgrade page knows how to sell, in the order it shows them.
SELLABLE = ("advanced_export", "sso", "audit_log")


@dataclass(frozen=True)
class UpgradeOffer:
    """One row on the upgrade page."""

    flag: str
    already_held: bool


def offers_for(connection: sqlite3.Connection, account_id: int) -> list[UpgradeOffer]:
    """What to show this account on the upgrade page."""
    return [
        UpgradeOffer(flag=flag, already_held=service.has_feature(connection, account_id, flag))
        for flag in SELLABLE
    ]


def change_plan(connection: sqlite3.Connection, account_id: int, plan: str) -> None:
    """Record a plan change."""
    connection.execute(
        "INSERT OR REPLACE INTO account_plan (account_id, plan) VALUES (?, ?)",
        (account_id, plan),
    )

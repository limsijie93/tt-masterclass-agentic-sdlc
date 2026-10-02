"""The upgrade page's view of what an account is missing.

THE SECOND CALLER, and the reason PROJ-207's spec has a non-empty out-of-scope section.

This module shares `has_feature` with the feature gate, and it wants the opposite behaviour
from it. The gate asks "may they use this?" and must refuse when unsure. This page asks "what
should we offer them?" and showing an upgrade prompt for something they already have is a
worse customer experience than showing nothing — so being wrong in the optimistic direction is
cheaper here.

That is why the shared helper's default was never simply flipped to False. Flipping it fixes
the gate and quietly changes this page, which nobody asked for and no test here would have
caught. The fix went to the call site instead, and the rule that keeps it there is
.semgrep/fail-open-entitlement.yml.
"""

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
    """What to show this account, cheapest-to-be-wrong-about first.

    `default=True` is passed explicitly rather than inherited, so that a change to the
    helper's signature cannot silently change this page.
    """
    offers = []
    for flag in SELLABLE:
        held = service.has_feature(connection, account_id, flag, default=True)
        offers.append(UpgradeOffer(flag=flag, already_held=held))
    return offers


def change_plan(connection: sqlite3.Connection, account_id: int, plan: str) -> None:
    """Record a plan change and drop the cached entitlements for the account.

    THIS is the invalidation hook finding 3 of example/PROJ-207/08-review.md missed. Without
    it the reviewer would be right that a revoked entitlement survives for up to the TTL.
    """
    connection.execute(
        "INSERT OR REPLACE INTO account_plan (account_id, plan) VALUES (?, ?)",
        (account_id, plan),
    )
    service.invalidate(account_id)

"""The feature-gate endpoint.

The top layer. It turns an entitlement answer into a response and nothing else. `.importlinter`
forbids importing `myapp.repo` from here.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from myapp.service.entitlements import service

#: Where a blocked customer is sent.
UPGRADE_PATH = "/billing/upgrade"


@dataclass
class FeatureResponse:
    """Granted, or refused with somewhere to go."""

    status: int
    granted: bool
    upgrade_url: str | None = None


def upgrade_url_for(flag: str) -> str:
    """Deep-links to the plan that carries this flag, so the refusal is actionable."""
    return f"{UPGRADE_PATH}?feature={flag}"


def feature_view(
    connection: sqlite3.Connection,
    account_id: int,
    flag: str,
) -> FeatureResponse:
    """Answer one feature-gate question for one account."""
    if not service.has_feature(connection, account_id, flag):
        return FeatureResponse(status=403, granted=False, upgrade_url=upgrade_url_for(flag))
    return FeatureResponse(status=200, granted=True)

"""The feature-gate endpoint.

The top layer. It turns an entitlement answer into a response and nothing else: no table
access, no cache decisions, no plan logic. `.importlinter` forbids importing `myapp.repo` from
here, and the temptation is real — reading the entitlements table directly is the shortest way
to answer this and the wrong way to build it, because the freshness promise lives in the
service and a second reader silently opts out of it.

There is no web framework here, for the reason `tooling/myapp/api/exports/views.py` gives.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from myapp.service.entitlements import service

#: Where a blocked customer is sent. Acceptance criterion 2 names this field by name.
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
    """Answer one feature-gate question for one account.

    `default=False` is passed explicitly. The helper's own default is True, and a view is the
    one place where inheriting it would hand an unpaid feature to anyone whose entitlement
    rows have not been written yet.
    """
    granted = service.has_feature(connection, account_id, flag, default=False)
    if not granted:
        return FeatureResponse(status=403, granted=False, upgrade_url=upgrade_url_for(flag))
    return FeatureResponse(status=200, granted=True)

"""The feature-gate tests."""

from __future__ import annotations

import sqlite3

from myapp.api.entitlements import views
from myapp.repo.entitlements import queries as entitlement_queries
from myapp.repo.exports import queries as export_queries
from myapp.service.billing import upgrade
from myapp.service.entitlements import service


def _account(account_id: int, flags: tuple[str, ...]) -> sqlite3.Connection:
    connection = export_queries.connect()
    connection.executescript(entitlement_queries.SCHEMA)
    connection.execute("INSERT INTO account (id, name) VALUES (?, ?)", (account_id, "acme"))
    entitlement_queries.seed(connection, account_id, flags)
    service.end_session(account_id)
    return connection


def test_an_entitled_account_gets_200() -> None:
    connection = _account(1, ("advanced_export",))
    response = views.feature_view(connection, 1, "advanced_export")
    assert response.status == 200
    assert response.upgrade_url is None


def test_an_account_without_the_flag_gets_403_and_an_upgrade_url() -> None:
    connection = _account(2, ("sso",))
    response = views.feature_view(connection, 2, "advanced_export")
    assert response.status == 403
    assert response.upgrade_url == "/billing/upgrade?feature=advanced_export"


def test_the_upgrade_page_lists_every_sellable_flag() -> None:
    connection = _account(3, ("sso",))
    offers = upgrade.offers_for(connection, 3)
    assert [offer.flag for offer in offers] == list(upgrade.SELLABLE)
    assert [offer.already_held for offer in offers] == [False, True, False]

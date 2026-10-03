"""The export tests."""

from __future__ import annotations

import sqlite3

import pytest

from myapp.api.exports import views
from myapp.repo.exports import queries
from myapp.service.exports import service
from myapp.service.reports import legacy


def _account_with(rows: int) -> tuple[sqlite3.Connection, int]:
    connection = queries.connect()
    queries.seed(connection, account_id=1, rows=rows)
    return connection, 1


def test_the_export_is_a_csv_with_one_line_per_row() -> None:
    connection, account_id = _account_with(250)
    response = views.export_report(connection, account_id)
    lines = response.body.splitlines()
    assert response.status == 200
    assert lines[0] == ",".join(service.CSV_COLUMNS)
    assert len(lines) == 1 + 250


def test_only_csv_is_supported() -> None:
    with pytest.raises(ValueError):
        service.build_export_query(1, format="xlsx")


def test_the_legacy_report_renders_one_page() -> None:
    connection, account_id = _account_with(legacy.LEGACY_PAGE_SIZE + 50)
    rows = legacy.render_report(connection, account_id)
    assert len(rows) == legacy.LEGACY_PAGE_SIZE

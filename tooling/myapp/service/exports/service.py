"""Export report generation.

The middle layer, and the only one allowed to reach `myapp.repo`. `myapp.api` must go through
here; `.importlinter` blocks the view from reaching the data layer directly.
"""

from __future__ import annotations

import csv
import io
import sqlite3
from dataclasses import dataclass

from myapp.repo.exports import queries

#: The CSV header.
CSV_COLUMNS = ("id", "account_id", "occurred", "amount")


@dataclass(frozen=True)
class ExportQuery:
    """A prepared export: who it is for, what shape, and an optional row limit."""

    account_id: int
    format: str
    limit: int | None


def _csv_row(values: tuple[object, ...]) -> str:
    buffer = io.StringIO()
    csv.writer(buffer).writerow(values)
    return buffer.getvalue()


def export_csv(connection: sqlite3.Connection, query: ExportQuery) -> str:
    """Render the whole export as one CSV document."""
    lines = [_csv_row(CSV_COLUMNS)]
    for row in queries.fetch_export_rows(connection, query.account_id, limit=query.limit):
        lines.append(_csv_row((row.id, row.account_id, row.occurred, row.amount)))
    return "".join(lines)


def build_export_query(
    account_id: int,
    format: str = "csv",
    limit: int | None = None,
) -> ExportQuery:
    """Prepare an export. `limit` caps the number of rows; `None` returns all of them."""
    if format != "csv":
        raise ValueError(f"unsupported export format: {format!r}")
    return ExportQuery(account_id=account_id, format=format, limit=limit)

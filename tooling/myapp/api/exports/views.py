"""The exports endpoint.

The top layer. It turns an export into a response and nothing else: no row access and no CSV
assembly. `.importlinter` forbids importing `myapp.repo` from here.

There is no web framework here. This module is the shape of an entry point, not a router.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from myapp.service.exports import service


@dataclass
class ExportResponse:
    """A complete CSV response."""

    status: int
    body: str = ""
    content_type: str = "text/csv"


def export_report(
    connection: sqlite3.Connection,
    account_id: int,
    export_format: str = "csv",
) -> ExportResponse:
    """Export one account's report as a CSV file."""
    query = service.build_export_query(account_id, format=export_format)
    return ExportResponse(status=200, body=service.export_csv(connection, query))

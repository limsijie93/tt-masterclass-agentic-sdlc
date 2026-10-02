"""Aggregated analytics rollups. NOT the export source, despite the name.

This table holds pre-aggregated daily totals for the dashboard. It is smaller than
`export_row`, it is one row per account per day, and querying it for an export produces a
plausible-looking CSV with the wrong number of rows in it.

It is here on purpose. An agent given the PROJ-142 ticket with no context file and no spec
reaches for the table whose name sounds most like a report, and this is that table — see D1
in docs/demos.md. Removing it removes the cold open.
"""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS analytics_daily (
    id         INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    day        TEXT NOT NULL,
    total      INTEGER NOT NULL
);
"""


def fetch_daily_totals(connection: sqlite3.Connection, account_id: int) -> list[tuple[str, int]]:
    rows = connection.execute(
        "SELECT day, total FROM analytics_daily WHERE account_id = ? ORDER BY day",
        (account_id,),
    ).fetchall()
    return [(str(day), int(total)) for day, total in rows]

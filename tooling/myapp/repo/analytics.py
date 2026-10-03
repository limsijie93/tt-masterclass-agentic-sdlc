"""Aggregated analytics rollups for the dashboard.

Pre-aggregated daily totals: one row per account per day.
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

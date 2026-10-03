"""Row access for the export report.

The bottom of the stack. Nothing here knows about HTTP or CSV.

Storage is SQLite and the dataset is generated. There is no production data anywhere in this
repository, and `seed()` is the only way rows come into existence.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

SCHEMA = """
CREATE TABLE IF NOT EXISTS account (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS export_row (
    id         INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES account(id),
    occurred   TEXT NOT NULL,
    amount     INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS export_row_account ON export_row(account_id);
"""


@dataclass(frozen=True)
class ExportRow:
    """One row of the export."""

    id: int
    account_id: int
    occurred: str
    amount: int


def connect(path: str = ":memory:") -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    return connection


def seed(connection: sqlite3.Connection, account_id: int, rows: int) -> None:
    """Generate `rows` export rows for one account. Generated, never copied."""
    connection.execute(
        "INSERT OR IGNORE INTO account (id, name) VALUES (?, ?)",
        (account_id, f"account-{account_id}"),
    )
    connection.executemany(
        "INSERT INTO export_row (account_id, occurred, amount) VALUES (?, ?, ?)",
        ((account_id, f"2026-08-{(n % 28) + 1:02d}", n * 7 % 1000) for n in range(rows)),
    )
    connection.commit()


def fetch_export_rows(
    connection: sqlite3.Connection,
    account_id: int,
    *,
    limit: int | None = None,
) -> list[ExportRow]:
    """Every row for one account, or the first `limit` of them."""
    sql = "SELECT id, account_id, occurred, amount FROM export_row WHERE account_id = ?"
    params: tuple[int, ...] = (account_id,)
    if limit is not None:
        sql += " LIMIT ?"
        params = (account_id, limit)
    return [ExportRow(*row) for row in connection.execute(sql, params).fetchall()]


def count_export_rows(connection: sqlite3.Connection, account_id: int) -> int:
    """How many rows one account has."""
    (total,) = connection.execute(
        "SELECT COUNT(*) FROM export_row WHERE account_id = ?", (account_id,)
    ).fetchone()
    return int(total)

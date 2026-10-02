"""Row access for the export report.

The bottom of the stack. Nothing here knows about HTTP, CSV, or job queues — that separation
is what lets `myapp.service` decide chunking without `myapp.api` ever touching a row.

Storage is SQLite and the dataset is generated. There is no production data anywhere in this
repository, and `seed()` is the only way rows come into existence.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
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
    """One row of the export. The CSV column set, and it does not change here."""

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
    chunk_size: int | None,
) -> Iterator[ExportRow]:
    """Yield rows for one account.

    `chunk_size=None` means no server-side batching: the driver materialises the whole result
    set. That default is the footgun PROJ-142's review found — see finding 1 of
    example/PROJ-142/08-review.md — and it is why callers must pass it explicitly.
    """
    cursor = connection.execute(
        "SELECT id, account_id, occurred, amount FROM export_row WHERE account_id = ?",
        (account_id,),
    )
    if chunk_size is None:
        for row in cursor.fetchall():
            yield ExportRow(*row)
        return
    while batch := cursor.fetchmany(chunk_size):
        for row in batch:
            yield ExportRow(*row)


def count_export_rows(connection: sqlite3.Connection, account_id: int) -> int:
    """How many rows the export will contain. Decides synchronous versus queued."""
    (total,) = connection.execute(
        "SELECT COUNT(*) FROM export_row WHERE account_id = ?", (account_id,)
    ).fetchone()
    return int(total)

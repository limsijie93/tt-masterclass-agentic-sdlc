"""Export report generation.

The middle layer, and the only one allowed to reach `myapp.repo`. `myapp.api` must go through
here — the obvious way to make an export fast is to stream rows straight out of the data layer
from the view, which is a layering violation, and `.importlinter` blocks it.

WHAT PROJ-142 CHANGED, AND WHY THE SIGNATURE LOOKS LIKE THIS

Before the ticket, `build_export_query()` took no `chunk_size` and the driver materialised the
whole result set. That is what timed out: the gateway terminates a request at 30 seconds, and a
million rows assembled in memory does not finish.

The fix added `chunk_size`. It defaults to `None`, and `None` means unbounded — so the default
preserves the old behaviour for callers that were never updated. That is exactly the footgun
finding 1 of course/tickets/PROJ-142/08-review.md identified, in a review of this change, on the
grounds that `myapp/service/reports/legacy.py` calls the same builder and was not touched.

The default is still `None`. It was not changed to a safe value, and that is deliberate: the
lesson is worth more than the fix. What guards it instead is
.semgrep/unbounded-export-query.yml, a custom rule that fails the build on any call site that
does not pass `chunk_size` explicitly. That rule exists because a human caught this once, and
it is the harvest loop's third row — something a human caught that a machine could have.

So both things are true here at the same time, which is the point: the signature is still a
footgun, and it can no longer be triggered silently.
"""

from __future__ import annotations

import csv
import io
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass

from myapp.repo.exports import queries

#: Exports at or below this many rows run inside the request. Above it, they are queued.
#: From acceptance criterion 1: the gateway's hard 30-second limit, measured at 1M rows.
SYNC_ROW_THRESHOLD = 50_000

#: The batch size every caller should pass. Not a default — see the module docstring.
DEFAULT_CHUNK_SIZE = 5_000

#: The CSV header. A performance fix must not change the column set (spec, Assumptions).
CSV_COLUMNS = ("id", "account_id", "occurred", "amount")


@dataclass(frozen=True)
class ExportQuery:
    """A prepared export: who it is for, what shape, and how it will be batched."""

    account_id: int
    format: str
    chunk_size: int | None

    @property
    def bounded(self) -> bool:
        """False means the whole result set is materialised. See finding 1."""
        return self.chunk_size is not None


def _csv_row(values: tuple[object, ...]) -> str:
    buffer = io.StringIO()
    csv.writer(buffer).writerow(values)
    return buffer.getvalue()


def stream_export_csv(
    connection: sqlite3.Connection,
    query: ExportQuery,
) -> Iterator[str]:
    """Yield the export one CSV line at a time.

    Streaming is what satisfies acceptance criterion 1: the first byte leaves before the last
    row is read, so a large account no longer waits on a fully-assembled response.

    It also changes what a timing test must do: a timer that stops on return measures
    time-to-first-byte, so criterion 1's test has to drain the iterator first. Missing that is
    finding 3 of course/tickets/PROJ-142/08-review.md — the planted false positive.
    """
    yield _csv_row(CSV_COLUMNS)
    rows = queries.fetch_export_rows(connection, query.account_id, chunk_size=query.chunk_size)
    for row in rows:
        yield _csv_row((row.id, row.account_id, row.occurred, row.amount))


def build_export_query(
    account_id: int,
    format: str = "csv",
    chunk_size: int | None = None,
) -> ExportQuery:
    """Prepare an export.

    `chunk_size=None` is unbounded and is the pre-PROJ-142 behaviour. Pass it explicitly;
    .semgrep/unbounded-export-query.yml fails the build if you do not.
    """
    if format != "csv":
        raise ValueError(f"unsupported export format: {format!r} (XLSX is out of scope)")
    return ExportQuery(account_id=account_id, format=format, chunk_size=chunk_size)


def should_queue(connection: sqlite3.Connection, account_id: int) -> bool:
    """True when this export is too large to finish inside the gateway's window."""
    return queries.count_export_rows(connection, account_id) > SYNC_ROW_THRESHOLD

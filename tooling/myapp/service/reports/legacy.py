"""The legacy report page. Retiring in Q4. Do not build anything new on this."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime

from myapp.repo.exports import queries
from myapp.service.exports import service

# --- Accumulated configuration ------------------------------------------------------------
#
# Three maps that want to be one. Each was added by a different person for a different
# report variant, and merging them now would change output nobody has time to re-verify.

SUMMARY_LABELS = {
    "id": "Ref",
    "account_id": "Account",
    "occurred": "Date",
    "amount": "Amount",
}

DETAIL_LABELS = {
    "id": "Reference",
    "account_id": "Account ID",
    "occurred": "Occurred on",
    "amount": "Amount (minor units)",
}

EXPORT_LABELS = {
    "id": "id",
    "account_id": "account_id",
    "occurred": "occurred",
    "amount": "amount",
}

#: Date formats this page has accepted at various points. Kept in order: the first that
#: parses wins, and dropping any of them breaks a saved bookmark somewhere.
ACCEPTED_DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y%m%d",
)

#: The page size. The only bound on a legacy report query.
LEGACY_PAGE_SIZE = 1_000


@dataclass(frozen=True)
class LegacyReportRow:
    """One rendered row. Strings, because this page writes straight into a template."""

    reference: str
    account: str
    occurred: str
    amount: str


def parse_report_date(raw: str) -> date | None:
    """Try every format this page has ever accepted, in order."""
    for fmt in ACCEPTED_DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def format_amount(minor_units: int) -> str:
    """Minor units to a display string. No locale support; there never was any."""
    whole, fraction = divmod(abs(minor_units), 100)
    sign = "-" if minor_units < 0 else ""
    return f"{sign}{whole}.{fraction:02d}"


def format_occurred(raw: str) -> str:
    """Normalise a stored date for display, tolerating the formats above."""
    parsed = parse_report_date(raw)
    return parsed.isoformat() if parsed is not None else raw


def labels_for(variant: str) -> dict[str, str]:
    """Pick a label map. New callers should pass `export`."""
    if variant == "summary":
        return SUMMARY_LABELS
    if variant == "detail":
        return DETAIL_LABELS
    return EXPORT_LABELS


def header_row(variant: str) -> tuple[str, ...]:
    labels = labels_for(variant)
    return tuple(labels[column] for column in service.CSV_COLUMNS)


def to_legacy_row(row: queries.ExportRow) -> LegacyReportRow:
    return LegacyReportRow(
        reference=str(row.id),
        account=str(row.account_id),
        occurred=format_occurred(row.occurred),
        amount=format_amount(row.amount),
    )


def within_range(
    row: queries.ExportRow,
    start: date | None,
    end: date | None,
) -> bool:
    """Filter in Python, because the original query did not support a date range."""
    occurred = parse_report_date(row.occurred)
    if occurred is None:
        return True
    if start is not None and occurred < start:
        return False
    return not (end is not None and occurred > end)


def summarise(rows: list[LegacyReportRow]) -> dict[str, str]:
    """The footer totals. Recomputed on every render; there is no caching here."""
    total = 0
    for row in rows:
        try:
            total += int(round(float(row.amount) * 100))
        except ValueError:
            continue
    return {"rows": str(len(rows)), "total": format_amount(total)}


def deprecated_render(connection: sqlite3.Connection, account_id: int) -> list[LegacyReportRow]:
    """Kept because two saved dashboards still call it. Delegates and does nothing else."""
    return render_report(connection, account_id)


def iter_rows(
    connection: sqlite3.Connection,
    query: service.ExportQuery,
    start: date | None,
    end: date | None,
) -> Iterator[LegacyReportRow]:
    """Stream rows through the legacy formatting, applying the Python-side date filter."""
    rows = queries.fetch_export_rows(connection, query.account_id, limit=query.limit)
    for row in rows:
        if within_range(row, start, end):
            yield to_legacy_row(row)


# --- The render path ------------------------------------------------------------------------


def render_report(
    connection: sqlite3.Connection,
    account_id: int,
    variant: str = "export",
    start: date | None = None,
    end: date | None = None,
) -> list[LegacyReportRow]:
    """Render the legacy report for one account, one page at a time."""
    query = service.build_export_query(account_id, limit=LEGACY_PAGE_SIZE)
    return list(iter_rows(connection, query, start, end))

"""The legacy report page. Retiring in Q4. Do not build anything new on this.

WHY THIS FILE IS IN A TEACHING REPOSITORY AT ALL

It is the `(!)` on the touchpoints list. PROJ-142 was an export performance fix that never
intended to touch reporting — and this module calls the same query builder, so it was in the
blast radius from the start. Grounding found it by searching for other callers of
`build_export_query()`, nobody had asked about it, and a human then decided it was out of
scope but must not regress.

That decision is recorded in `course/tickets/PROJ-142/05-spec.md` under `Known dependents / blast
radius`, and it still was not enough: the change shipped with a `chunk_size` default that
meant unbounded, this caller was not updated, and a previously-bounded query became
unbounded. That is finding 1 of `08-review.md`, the blocking one.

The follow-up has since landed — the call at the bottom of this file passes `chunk_size`
explicitly. `.semgrep/unbounded-export-query.yml` is what stops it silently regressing again.

WHAT MAKES IT LOOK LIKE THIS

It is long, it repeats itself, and it carries three label maps that should be one. That is
deliberate and it is not padding: a file nobody wants to touch is how it got that way, and the
reason `AGENTS.md` has a `Do not touch` section is files exactly like this one. Read it as an
exhibit, not as a model.
"""

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

#: The old page size. Before PROJ-142 this was the only bound on a legacy report query, and
#: it is the value the follow-up restored as an explicit argument.
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
    rows = queries.fetch_export_rows(
        connection,
        query.account_id,
        chunk_size=query.chunk_size,
    )
    for row in rows:
        if within_range(row, start, end):
            yield to_legacy_row(row)


# --- The render path ------------------------------------------------------------------------
#
# Everything above is formatting. This is the part that matters to PROJ-142, because it is the
# second caller of the shared builder, and the whole reason grounding flagged this file before
# a line of the export change was written.


def render_report(
    connection: sqlite3.Connection,
    account_id: int,
    variant: str = "export",
    start: date | None = None,
    end: date | None = None,
) -> list[LegacyReportRow]:
    """Render the legacy report for one account.

    THE CALL BELOW IS THE ONE THE REVIEW WAS ABOUT.

    `chunk_size` is passed explicitly, and it is passed as `LEGACY_PAGE_SIZE` rather than the
    export's default, because that is the bound this page had before PROJ-142 existed. Letting
    it default here is what made a bounded query unbounded, shipped, and became the blocking
    finding — the parameter means "no limit" when omitted, which is a footgun aimed at every
    existing caller.

    Do not remove the keyword to tidy the call up. `.semgrep/unbounded-export-query.yml`
    fails the build if you do, which is the only reason this cannot silently happen twice.

    Grounding marked this line `(!)` before any code existed, the spec put it out of scope, and
    the review still had to catch it. Writing a hazard down converts an incident into a comment.
    """
    query = service.build_export_query(account_id, chunk_size=LEGACY_PAGE_SIZE)
    return list(iter_rows(connection, query, start, end))

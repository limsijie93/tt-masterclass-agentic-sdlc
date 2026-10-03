"""The exports endpoint.

The top layer. It decides synchronous versus queued and nothing else: no row access, no CSV
assembly, no batching decisions. `.importlinter` forbids importing `myapp.repo` from here, and
the temptation it is guarding against is real — streaming rows straight out of the data layer
is the shortest way to make this fast and the wrong way to build it.

`ExportResponse.streaming_content` is named after the framework convention on purpose: the
attribute is what a test drains to measure time-to-completion rather than time-to-first-byte.

There is no web framework here. This module is the shape of an entry point, not a router: a
masterclass needs the layering and the decision to be legible, and a framework would add a
settings module, a stub package and a fight with strict typing without teaching anything the
contract does not already say.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass

from myapp.service.exports import service
from myapp.tasks import queue


@dataclass
class ExportResponse:
    """A streaming CSV response, or a job accepted for later."""

    status: int
    streaming_content: Iterator[str] | None = None
    job_id: str | None = None


def status_url(job_id: str) -> str:
    """Where the client polls. The bulk-import screen already speaks this protocol."""
    return f"/api/exports/jobs/{job_id}"


def export_report(
    connection: sqlite3.Connection,
    account_id: int,
    export_format: str = "csv",
) -> ExportResponse:
    """Export one account's report.

    Under the synchronous threshold, stream the CSV and return 200. Over it, hand the work to
    the existing job queue and return 202 with a job id the client polls — acceptance
    criterion 2. The threshold exists because the gateway terminates the request at 30s.
    """
    query = service.build_export_query(
        account_id,
        format=export_format,
        chunk_size=service.DEFAULT_CHUNK_SIZE,
    )
    if service.should_queue(connection, account_id):
        job_id = queue.enqueue_export(account_id, export_format)
        return ExportResponse(status=202, job_id=job_id)
    return ExportResponse(
        status=200,
        streaming_content=service.stream_export_csv(connection, query),
    )


def job_status(job_id: str) -> ExportResponse:
    """Poll a queued export. Added by criterion 2's second commit."""
    job = queue.get_job(job_id)
    return ExportResponse(status=200 if job is not None else 404, job_id=job_id)

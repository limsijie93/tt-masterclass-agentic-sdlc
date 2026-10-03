"""The job queue — the asynchronous path acceptance criterion 2 uses. Pre-dates PROJ-142:
the bulk-import screen already polls it. May call myapp.service; never myapp.api."""

from __future__ import annotations

import sqlite3

from myapp.service.exports import service
from myapp.tasks.jobs import JOBS, Job, new_job


def run_export_job(connection: sqlite3.Connection, job_id: str) -> Job:
    """Execute a queued export.

    This is the branch `07-pr-body.md` lists as a candidate untested path — found
    mechanically, by diff-cover on changed lines, not by judgement.
    """
    job = JOBS[job_id]
    query = service.build_export_query(
        job.account_id,
        format=job.export_format,
        chunk_size=service.DEFAULT_CHUNK_SIZE,
    )
    job.lines = list(service.stream_export_csv(connection, query))
    job.state = "done"
    return job


def enqueue_export(account_id: int, export_format: str = "csv") -> str:
    """Accept an export for later execution and return its id."""
    return new_job(account_id, export_format).id


def get_job(job_id: str) -> Job | None:
    return JOBS.get(job_id)

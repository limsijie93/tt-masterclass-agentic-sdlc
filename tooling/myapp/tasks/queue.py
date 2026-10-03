"""The job queue. The bulk-import screen enqueues work here and polls for the result.
May call myapp.service; never myapp.api."""

from __future__ import annotations

from myapp.tasks.jobs import JOBS, Job, new_job


def enqueue(account_id: int, kind: str) -> str:
    """Accept a job for later execution and return its id."""
    return new_job(account_id, kind).id


def get_job(job_id: str) -> Job | None:
    return JOBS.get(job_id)

"""Job records. Split out of queue.py so the execution entry point sits at the top of it.

In-memory on purpose: persistence is not what this repository teaches, and a real queue here
would be a second thing to explain in every demo.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class Job:
    """One queued export."""

    id: str
    account_id: int
    export_format: str
    state: str = "queued"
    lines: list[str] = field(default_factory=list)


JOBS: dict[str, Job] = {}


def new_job(account_id: int, export_format: str) -> Job:
    job = Job(id=uuid.uuid4().hex, account_id=account_id, export_format=export_format)
    JOBS[job.id] = job
    return job

"""Job records for the queue.

In-memory on purpose: persistence is not what this repository teaches.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class Job:
    """One queued job."""

    id: str
    account_id: int
    kind: str
    state: str = "queued"
    lines: list[str] = field(default_factory=list)


JOBS: dict[str, Job] = {}


def new_job(account_id: int, kind: str) -> Job:
    job = Job(id=uuid.uuid4().hex, account_id=account_id, kind=kind)
    JOBS[job.id] = job
    return job

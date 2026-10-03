"""Shared test switches.

The learner repository is generated from this one by tooling/tools/publish_learner.py, without the
answer keys. A test that needs an answer key is instructor-only: it runs here and skips there,
so both copies share one test suite rather than two that drift.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

# teach/ is left out of every learner copy, so its presence is what "instructor" means.
INSTRUCTOR = (REPO / "teach").is_dir()

instructor_only = pytest.mark.skipif(
    not INSTRUCTOR, reason="needs the answer keys, which live in the instructor repo"
)

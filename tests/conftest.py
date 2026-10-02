"""Shared test switches.

The learner repository is generated from this one by tools/publish_learner.py, without the
answer keys. A test that needs an answer key is instructor-only: it runs here and skips there,
so both copies share one test suite rather than two that drift.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# RECORDING.md is left out of every learner copy, so its presence is what "instructor" means.
INSTRUCTOR = (REPO / "RECORDING.md").exists()

instructor_only = pytest.mark.skipif(
    not INSTRUCTOR, reason="needs the answer keys, which live in the instructor repo"
)

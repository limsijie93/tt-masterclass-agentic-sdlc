"""Numbers a document quotes as a command's output must be the number the command prints.

This exists because of a real miss. README.md and evals/README.md both printed

    EVAL_ENGINE_CMD=true python3 tools/run_evals.py --all      ->  0/1 passed

against a suite of six cases. course/demos.md had `0/6` and was right, so the repo contradicted
itself about the output of its own flagship demonstration -- in the section about tests that
lie, in a file that tells the presenter "the number in the narration has to be the number on
screen".

tools/check_commands_sync.py already catches a context file diverging from the gate. Nothing
caught a DOCUMENT diverging from what its own command prints. This is the narrow, cheap,
never-flaky version of that: it does not run the commands (that would need a key and a
network), it checks the one class of claim that is both load-bearing and arithmetic.

Add a check here whenever a document starts quoting a count that some other file determines.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CASES = REPO / "evals" / "cases"

# Anywhere a doc quotes the suite's score. The denominator is how many cases exist.
SUITE_SCORE = re.compile(r"(\d+)/(\d+) passed")

SCORED_DOCS = (
    "README.md",
    "evals/README.md",
    "course/demos.md",
    "tools/run_evals.py",
)


def test_every_quoted_suite_score_counts_the_real_cases() -> None:
    total = len(list(CASES.glob("*.md")))
    assert total, "no eval cases found"

    checked = 0
    for name in SCORED_DOCS:
        for number, line in enumerate((REPO / name).read_text(encoding="utf-8").splitlines(), 1):
            match = SUITE_SCORE.search(line)
            if not match:
                continue
            # A single-case score is legitimate, but only where THIS line says --case. A
            # whole-document escape would have let the original bug through: neither README
            # quoted `--case` anywhere near the line that was wrong.
            if "--case" in line:
                continue
            assert int(match.group(2)) == total, (
                f"{name}:{number} quotes {match.group(0)!r}, "
                f"but evals/cases/ holds {total} cases"
            )
            checked += 1
    assert checked, "no suite scores found to check -- has the format changed?"


# The same claim spelled out. The bug this catches is the one the score check missed:
# README.md said `0/7 passed` on one line and "Six cases" fifteen lines later, because a
# seventh case changed the arithmetic and not the prose.
WORDS = {
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}
SPELLED_COUNT = re.compile(rf"\b({'|'.join(WORDS)}) cases\b", re.IGNORECASE)


def test_every_spelled_out_case_count_counts_the_real_cases() -> None:
    total = len(list(CASES.glob("*.md")))

    for name in SCORED_DOCS:
        for number, line in enumerate((REPO / name).read_text(encoding="utf-8").splitlines(), 1):
            match = SPELLED_COUNT.search(line)
            if not match:
                continue
            assert WORDS[match.group(1).lower()] == total, (
                f"{name}:{number} says {match.group(0)!r}, " f"but evals/cases/ holds {total} cases"
            )

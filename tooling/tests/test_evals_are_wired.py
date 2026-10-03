"""Structural checks on the eval suite. These BLOCK; the eval results themselves only report.

That split matches the one this repo already has. lint_skills.py checks structure and
blocks; tier 2 exercises judgment and comments. An eval run IS an agent run, and
code-review/SKILL.md establishes that a flaky gate destroys trust in about a week — so gating
on the run would invert the ladder Block 3 spends a segment building. Gating on the suite's
SHAPE costs nothing and never flakes.

The anti-tautology rule is mechanised here rather than left to convention, because "do not
compare against the worked example" is exactly the kind of rule that erodes.
"""

from __future__ import annotations

from pathlib import Path

from eval_assertions import REGISTRY
from run_evals import SANITISE, parse_case, sanitise_worktree

REPO = Path(__file__).resolve().parents[2]
CASES = sorted((REPO / "tooling" / "evals" / "cases").glob("*.md"))


def test_there_is_at_least_one_case() -> None:
    assert CASES


def test_every_case_names_a_skill_that_exists() -> None:
    for path in CASES:
        skill = parse_case(path).skill
        assert (
            REPO / ".github" / "skills" / skill / "SKILL.md"
        ).is_file(), f"{path.name} names skill {skill!r}, which does not exist"


def test_every_case_declares_assertions_that_exist() -> None:
    for path in CASES:
        case = parse_case(path)
        assert case.assertions, f"{path.name} declares no assertions"
        for spec in case.assertions:
            name = spec.get("name")
            assert name in REGISTRY, f"{path.name} names unknown assertion {name!r}"


def test_every_case_has_a_prompt() -> None:
    for path in CASES:
        assert parse_case(path).prompt, f"{path.name} has an empty prompt"


def test_every_case_records_its_stability_honestly() -> None:
    """A case that passes 4 times in 5 is a lottery, not an eval — so authoring runs it 5x.

    `unmeasured` is permitted and is not a loophole: it is the only honest value before a case
    has been run against a real engine, and the next test makes it impossible to claim 5/5
    without saying when it was measured. Writing 5/5 for a run nobody performed would be the
    aspirational-content failure this repo warns about, in a file about verification.
    """
    for path in CASES:
        stability = parse_case(path).stability
        assert stability in {
            "5/5",
            "unmeasured",
        }, f"{path.name} records stability {stability!r}; expected '5/5' or 'unmeasured'"


def test_a_stability_claim_carries_the_date_and_the_model() -> None:
    """A 5/5 needs both `measured:` and `model:`, or it is a number with no provenance.

    THIS REPO DOES NOT PIN A MODEL, and that is a decision rather than an omission: learners
    choose their own, and Opus 5.5 is what the teaching runs on. But "changing the model
    changes the thing under test" is still true — it is why pinning was the obvious advice —
    so what replaces the pin is a record. An unattributed 5/5 is worse than `unmeasured`,
    because `unmeasured` tells you what you do not know and a bare 5/5 does not.

    Both fields or neither. A date with no model says when somebody ran something.
    """
    for path in CASES:
        if parse_case(path).stability != "5/5":
            continue
        body = path.read_text(encoding="utf-8")
        for field in ("measured:", "model:"):
            assert field in body, (
                f"{path.name} claims 5/5 with no `{field}` — a stability number without the "
                f"date and the model that produced it is a number with no provenance"
            )


def test_no_case_expects_a_worked_example_artifact() -> None:
    """THE ANTI-TAUTOLOGY RULE, mechanised.

    Comparing a skill's output to course/tickets/PROJ-142/02-interrogation.md asserts that the model
    reproduces one hand-polished past output — non-deterministic AND circular. A case's
    expected outcome is a list of properties, never a file.
    """
    for path in CASES:
        body = path.read_text(encoding="utf-8")
        assert (
            "course/tickets/PROJ-142" not in body
        ), f"{path.name} references the worked example; expectations are properties, not files"


def test_at_least_one_case_is_a_negative_control() -> None:
    """The cases that assert a skill REFUSED are where models actually fail."""
    assert any(parse_case(p).negative_control for p in CASES)


def test_every_negative_control_has_a_positive_companion() -> None:
    """The single most important check in this file.

    A negative control asserting `did_not_write` passes if the harness never invoked the
    engine at all. That is the semgrep false-green trap in a new place. Every negative
    control must therefore also assert something a no-op engine cannot produce.
    """
    for path in CASES:
        case = parse_case(path)
        if not case.negative_control:
            continue
        names = [spec.get("name") for spec in case.assertions]
        assert "did_not_write" in names, f"{path.name} is a negative control with nothing negative"
        positives = [n for n in names if n in {"output_mentions", "wrote_exactly"}]
        assert positives, f"{path.name} has no positive companion, so a no-op engine would pass it"


def test_the_sanitiser_removes_the_answer_key(tmp_path: Path) -> None:
    """Rule 3 of the fixture design. Deleting this call must be a test failure."""
    (tmp_path / "course" / "tickets" / "PROJ-142").mkdir(parents=True)
    (tmp_path / "course" / "tickets" / "PROJ-142" / "02-interrogation.md").write_text(
        "answers", "utf-8"
    )
    (tmp_path / "tooling" / "evals" / "cases").mkdir(parents=True)
    (tmp_path / "keep.py").write_text("x = 1", "utf-8")

    removed = sanitise_worktree(tmp_path)

    assert set(removed) == set(SANITISE)
    assert not (tmp_path / "course" / "tickets" / "PROJ-142").exists()
    assert not (tmp_path / "tooling" / "evals").exists()
    assert (tmp_path / "keep.py").exists(), "the sanitiser must not remove the code under test"


def test_the_sanitise_list_names_both_directories() -> None:
    assert "course/tickets/PROJ-142" in SANITISE
    assert "tooling/evals" in SANITISE


# --- the parser, because a fence bug fails cases for the wrong reason -------------------


CASE_WITH_HEADINGS_IN_SETUP = """---
skill: spec-draft
stability: unmeasured
assertions:
  - name: did_not_write
    path: "specs/X.md"
  - name: output_mentions
    needle: "X"
---

## Prompt

Draft the spec for X.

## Setup

### specs/X.answers.md
```
1  A question?
   answer:
```

### specs/X.touchpoints.md
```
touchpoints - X

## Goal
tooling/scripts/lint_skills.py:1   a heading above lives INSIDE this fence
```
"""


def test_headings_inside_a_setup_fence_do_not_end_the_section(tmp_path: Path) -> None:
    """The bug this was written for, and the second time this repo has had it.

    A setup file's content is usually a spec or an answers file, so it contains `## Goal`.
    Treating that as a section heading dropped every setup file after the first — and the case
    then failed for the wrong reason, which is worse than failing.
    """
    path = tmp_path / "c.md"
    path.write_text(CASE_WITH_HEADINGS_IN_SETUP, encoding="utf-8")
    case = parse_case(path)
    assert set(case.setup) == {"specs/X.answers.md", "specs/X.touchpoints.md"}


def test_fenced_content_survives_intact(tmp_path: Path) -> None:
    path = tmp_path / "c.md"
    path.write_text(CASE_WITH_HEADINGS_IN_SETUP, encoding="utf-8")
    case = parse_case(path)
    assert "## Goal" in case.setup["specs/X.touchpoints.md"]
    assert "tooling/scripts/lint_skills.py:1" in case.setup["specs/X.touchpoints.md"]


def test_every_case_that_declares_setup_files_parses_all_of_them() -> None:
    """A case whose setup silently half-loads runs the skill against missing inputs."""
    for path in CASES:
        declared = path.read_text(encoding="utf-8").count("\n### ")
        assert (
            len(parse_case(path).setup) == declared
        ), f"{path.name} declares {declared} setup file(s), parsed {len(parse_case(path).setup)}"

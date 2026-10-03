"""The labs' structure blocks in tier 1. Their results are the learner's business.

Modelled on tests/test_evals_are_wired.py, and for the same reason: an eval suite and a lab
suite are the same artifact with a different engine, so the structural rules that keep one
honest keep the other honest.

THE TEST THAT MATTERS is test_a_no_op_scores_nothing. A grader that passes an empty
submission is a test that cannot fail, and it looks like success -- the semgrep false green,
the no-op engine, and now the ungraded lab. It is not hypothetical: the first run of
`lab.py check 01` on an untouched checkout scored 3/7, because `max_lines` and
`banned_tokens` are both vacuously true of a file that was never written. Nought lines is
under every limit, and nothing forbidden is in a file nobody wrote.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from conftest import instructor_only
from eval_assertions import REGISTRY, EvalContext
from lab import LAB_ONLY, command_exits, parse_lab, run_checks

REPO = Path(__file__).resolve().parent.parent
LABS = sorted((REPO / "course" / "labs").glob("*/lab.md"))
REQUIRED_SECTIONS = ("brief", "start", "what good looks like")


def test_there_are_labs() -> None:
    assert LABS, "no labs found"


def test_every_lab_declares_what_it_needs() -> None:
    for path in LABS:
        lab = parse_lab(path)
        assert lab.number, f"{path} has no lab number"
        assert lab.title, f"{path} has no title"
        assert lab.segment, f"{path} names no lecture segment"
        assert lab.needs in {"agent", "no-agent"}, f"{path}: needs={lab.needs!r}"
        assert lab.minutes.isdigit(), f"{path}: minutes={lab.minutes!r}"


def test_every_lab_has_the_three_sections() -> None:
    """A brief, a way in, and the reasoning. The third is the one that transfers."""
    for path in LABS:
        lab = parse_lab(path)
        for section in REQUIRED_SECTIONS:
            assert lab.sections.get(section), f"{path} has no `## {section}` section"


def test_every_assertion_exists() -> None:
    for path in LABS:
        for spec in parse_lab(path).assertions:
            name = str(spec.get("name", ""))
            assert name in REGISTRY or name in LAB_ONLY, f"{path} names unknown check {name!r}"


@instructor_only
def test_every_lab_has_an_answer_key_and_a_place_to_put_it() -> None:
    for path in LABS:
        lab = parse_lab(path)
        solution = lab.directory / "solution"
        assert solution.is_dir(), f"{path} has no solution/"
        assert any(solution.iterdir()), f"{solution} is empty"
        assert lab.solution_into, f"{path} does not say where solution/ is applied"


def test_the_agent_labs_come_last() -> None:
    """Ordering is the completion lever. A learner who hits "you will need an API key" on
    lab 01 stops at lab 01."""
    needs = [parse_lab(p).needs for p in LABS]
    assert needs == sorted(
        needs, key=lambda n: n == "agent"
    ), f"labs are ordered {needs}; every no-agent lab must come before every agent one"


def _clean_worktree(tmp: Path) -> Path:
    worktree = tmp / "wt"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
        cwd=REPO,
        capture_output=True,
        check=True,
    )
    return worktree


def _remove_worktree(worktree: Path) -> None:
    subprocess.run(
        ["git", "worktree", "remove", "--force", str(worktree)],
        cwd=REPO,
        capture_output=True,
        check=False,
    )


def test_a_no_op_scores_nothing() -> None:
    """Every lab, on an untouched checkout, scores 0. The single most important check here.

    It runs against a clean worktree rather than this checkout, because a developer who has
    actually done a lab would otherwise fail the build -- a gate that fires for doing the
    thing the repository is for gets deleted, and rightly.
    """
    with tempfile.TemporaryDirectory() as tmp:
        worktree = _clean_worktree(Path(tmp))
        try:
            for path in LABS:
                lab = parse_lab(path)
                passed, total, lines = run_checks(lab, root=worktree)
                assert total, f"lab {lab.number} asserts nothing"
                assert passed == 0, (
                    f"lab {lab.number} scores {passed}/{total} on an untouched checkout. "
                    f"An assertion is vacuously true of a file nobody wrote:\n" + "\n".join(lines)
                )
        finally:
            _remove_worktree(worktree)


@instructor_only
def test_the_answer_key_scores_full_marks() -> None:
    """The positive companion. Without it, `assert passed == 0` is satisfied by a lab whose
    checks can never pass at all, which is a different way of grading nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        worktree = _clean_worktree(Path(tmp))
        try:
            for path in LABS:
                lab = parse_lab(path)
                destination = worktree / lab.solution_into
                destination.mkdir(parents=True, exist_ok=True)
                for answer in sorted((lab.directory / "solution").iterdir()):
                    if answer.is_file():
                        shutil.copy(answer, destination / answer.name)

                passed, total, lines = run_checks(lab, root=worktree)
                assert passed == total, (
                    f"lab {lab.number} scores {passed}/{total} with its own answer key "
                    f"applied:\n" + "\n".join(lines)
                )
        finally:
            _remove_worktree(worktree)


def test_a_shelled_out_check_declares_the_tools_it_needs() -> None:
    """Every `command_exits` names its executables, so a missing one says so.

    Without `needs`, a missing tool reads as a wrong answer. The old version checked
    `returncode == 127`, which cannot work through a pipe — a pipeline's status is its LAST
    stage's, so `lint-imports ... | grep -q X` with lint-imports absent exits 1, from grep.
    Both labs using this are pipelines. CI caught it by telling a learner their import
    contract was wrong on a machine where nothing was installed.
    """
    for path in LABS:
        for spec in parse_lab(path).assertions:
            if spec.get("name") == "command_exits":
                assert spec.get("needs"), (
                    f"{path}: a command_exits with no `needs:` reports a missing tool as a "
                    f"failed check — {spec.get('cmd')!r}"
                )


def test_a_missing_tool_reports_itself_and_not_a_wrong_answer() -> None:
    """The message a learner sees names the tool, not their work."""
    ok, detail = command_exits(
        EvalContext(worktree=REPO),
        cmd="echo this-never-runs | grep -q nothing",
        code=0,
        needs=["a-tool-that-does-not-exist"],
    )
    assert not ok
    assert "a-tool-that-does-not-exist" in detail and "make setup" in detail

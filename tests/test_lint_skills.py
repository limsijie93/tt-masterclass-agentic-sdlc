"""Tests for scripts/lint_skills.py.

The linter had no tests until now, which is its own small irony: the script that checks every
skill was the one unchecked thing in the repo. These cover the section parser, because that is
what every other check reads through — a parser bug shows up as a wrong verdict somewhere else,
which is how the fence bug below stayed invisible.
"""

from __future__ import annotations

from pathlib import Path

from lint_skills import Report as LintReport
from lint_skills import parse_frontmatter, split_sections

# parse_frontmatter reports paths relative to the repo root, so a fixture path has to sit
# under it. Using a bare "x/SKILL.md" raises ValueError from relative_to — which is itself
# worth knowing about the function.
FAKE = Path(__file__).resolve().parent.parent / ".github" / "skills" / "x" / "SKILL.md"

BODY_WITH_HEADINGS_IN_A_FENCE = """
## Output contract

Two files.

`harvest/<TICKET>.md`:

```
harvest - PROJ-1

## Proposals

### the context file
change   some line

## Logged, not proposed

nothing yet
```

`harvest/ledger.md`, appended:

```
2026-01-01  PROJ-1  none  an observation
```

## Stop conditions

Always.
"""


def test_headings_inside_a_fence_are_not_section_boundaries() -> None:
    """The bug this file was written for.

    A skill whose output contract shows the markdown it emits contains `## ` inside a fence.
    Treating that as a boundary truncated the section, so paths declared after it vanished and
    the chain check reported a broken chain for a skill whose chain was fine.
    """
    sections = split_sections(BODY_WITH_HEADINGS_IN_A_FENCE)
    assert set(sections) == {"## Output contract", "## Stop conditions"}
    assert "## Proposals" not in sections


def test_a_path_after_a_fenced_heading_is_still_in_the_section() -> None:
    sections = split_sections(BODY_WITH_HEADINGS_IN_A_FENCE)
    assert "harvest/ledger.md" in sections["## Output contract"]


def test_real_headings_still_split() -> None:
    sections = split_sections("## Purpose\n\nA\n\n## Procedure\n\nB\n")
    assert sections == {"## Purpose": "A", "## Procedure": "B"}


def test_frontmatter_folded_description_is_joined() -> None:
    report = LintReport()
    data, body = parse_frontmatter(
        "---\nname: x\ndescription: >\n  one line\n  and another\n---\nbody\n",
        FAKE,
        report,
    )
    assert data["name"] == "x"
    assert data["description"] == "one line and another"
    assert body.strip() == "body"


def test_a_file_with_no_frontmatter_is_reported() -> None:
    report = LintReport()
    parse_frontmatter("no frontmatter here\n", FAKE, report)
    assert any("no YAML frontmatter" in f for f in report.failures)


def test_unclosed_frontmatter_is_reported() -> None:
    report = LintReport()
    parse_frontmatter("---\nname: x\nbody with no close\n", FAKE, report)
    assert any("not closed" in f for f in report.failures)


# ---------------------------------------------------------------------------
# Check 11 — the capability contract, whose two halves live in two places and
# therefore need something comparing them. These are the direct tests; the
# eight real skills are the integration test, and they run in tier 1.

from lint_skills import Skill, _check_capabilities  # noqa: E402


def _skill(allowlist: str | None, inputs: str) -> Skill:
    frontmatter = {"name": "x", "description": "d"}
    if allowlist is not None:
        frontmatter["allowed-tools"] = allowlist
    body = f"## Inputs required\n\n{inputs}\n\n## Procedure\n\nStep one.\n"
    return Skill(
        name="x", path=FAKE, frontmatter=frontmatter, body=body, sections=split_sections(body)
    )


NO_COMMANDS = "**Capabilities.** Reads files; writes one file; **runs no commands**."
RUNS_COMMANDS = "**Capabilities.** Reads files; writes source; **runs commands** — the tests."


def _failures(allowlist: str | None, inputs: str) -> list[str]:
    report = LintReport()
    _check_capabilities(_skill(allowlist, inputs), "x/SKILL.md", report)
    return report.failures


def test_a_shell_free_skill_that_says_so_passes() -> None:
    assert _failures("Read, Grep, Glob, Write", NO_COMMANDS) == []


def test_a_skill_that_runs_commands_and_holds_a_shell_passes() -> None:
    assert _failures("Read, Grep, Glob, Write, Edit, Bash", RUNS_COMMANDS) == []


def test_prose_saying_no_commands_beside_a_shell_is_reported() -> None:
    """The failure worth having. Every other check here guards against an omission;
    this one guards against two halves of one claim drifting apart, which is the
    failure mode that comes with splitting a contract across two files."""
    failures = _failures("Read, Write, Bash", NO_COMMANDS)
    assert any("disagree" in f for f in failures)


def test_the_other_direction_is_reported_too() -> None:
    """A body that never says it runs no commands, beside an allowlist with no shell.
    Silence is not a decision, and a reader cannot tell one from the other."""
    failures = _failures("Read, Write", RUNS_COMMANDS)
    assert any("omission from a decision" in f for f in failures)


def test_every_shell_spelling_counts() -> None:
    """Host vocabulary differs. `runInTerminal` is as much a shell as `Bash`, and a
    check that only knew one name would pass the host it was not written against."""
    for spelling in ("Bash", "runCommands", "runInTerminal", "shell"):
        failures = _failures(f"Read, Write, {spelling}", NO_COMMANDS)
        assert any("disagree" in f for f in failures), spelling


def test_a_missing_allowlist_is_reported() -> None:
    assert any("no 'allowed-tools'" in f for f in _failures(None, NO_COMMANDS))


def test_a_missing_capability_line_is_reported_once() -> None:
    """And the check stops there rather than comparing against prose that is not present,
    which would report a second, misleading failure about a disagreement."""
    failures = _failures("Read, Write", "1. `specs/<TICKET>.md`.")
    assert len(failures) == 1
    assert "**Capabilities.**" in failures[0]

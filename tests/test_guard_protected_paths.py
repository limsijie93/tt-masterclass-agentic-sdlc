"""Tests for tools/guard_protected_paths.py.

Includes wiring tests, for the same reason the test guard has them: a guard that works and is
not connected is worth nothing, and this repo has already shipped one script that sat wired to
nothing for four layers.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from guard_protected_paths import PROTECTED, is_protected

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / "tools" / "guard_protected_paths.py"


def test_the_settings_file_is_protected() -> None:
    """The file that can disable every guard, including this one."""
    assert is_protected(".claude/settings.json")


def test_the_local_override_is_protected() -> None:
    assert is_protected(".claude/settings.local.json")


def test_the_guards_protect_themselves() -> None:
    assert is_protected("tools/guard_protected_paths.py")
    assert is_protected("tools/guard_test_edits.py")


def test_ordinary_files_are_not_protected() -> None:
    for path in (
        "tools/check_touchpoints.py",
        "scripts/lint_skills.py",
        "README.md",
        "tests/test_x.py",
    ):
        assert not is_protected(path), path


def test_the_list_stays_short_on_purpose() -> None:
    """A protected list covering files the team edits daily becomes the mypy trap.

    Notably absent and deliberately so: .github/workflows/ and .pre-commit-config.yaml.
    """
    assert len(PROTECTED) == 3
    joined = " ".join(PROTECTED)
    assert "workflows" not in joined
    assert "pre-commit" not in joined


def test_every_protected_path_is_named_in_codeowners() -> None:
    """The guard's own failure message makes this claim. It should be true.

    It prints "{PROTECTED[0]} is owned in .github/CODEOWNERS" when it blocks, which was true
    only through the `*` catch-all — and catch-all review is not guard self-protection. The
    guard stops the AGENT editing these; CODEOWNERS is what stops a human deleting them in a
    pull request nobody looked closely at. Two halves of one argument, and the second half was
    being asserted rather than held.

    Matched on the directory or glob stem, not the exact string: CODEOWNERS patterns are not
    fnmatch, and a test that demanded byte equality would fail the first time someone wrote a
    broader rule that genuinely covers the path.
    """
    codeowners = (REPO / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    rules = [
        ln.split()[0] for ln in codeowners.splitlines() if ln.strip() and not ln.startswith("#")
    ]
    for entry in PROTECTED:
        stem = entry.split("*")[0].rstrip("/")
        covered = any(
            rule.strip("/").split("*")[0].rstrip("/")
            and stem.startswith(rule.strip("/").split("*")[0].rstrip("/"))
            for rule in rules
            if rule != "*"
        )
        assert covered, (
            f"{entry} is guard machinery with no CODEOWNERS rule of its own. The `*` rule "
            f"covers it for review and does not say the stakes here are different."
        )


def _run(payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        check=False,
    )


def test_editing_a_protected_path_is_denied_with_exit_two() -> None:
    result = _run(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude/settings.json", "content": "{}"},
        }
    )
    assert result.returncode == 2
    assert "not agent-editable" in result.stderr


def test_there_is_no_ask_path() -> None:
    """This guard blocks or allows. A protected path that merely asks is not protected."""
    result = _run(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "tools/guard_test_edits.py", "content": "x"},
        }
    )
    assert result.returncode == 2
    assert result.stdout == ""


def test_a_read_is_not_blocked() -> None:
    """Reading the guard is fine. Only writing is the problem."""
    result = _run({"tool_name": "Read", "tool_input": {"file_path": ".claude/settings.json"}})
    assert result.returncode == 0


def test_an_ordinary_edit_is_allowed() -> None:
    result = _run({"tool_name": "Write", "tool_input": {"file_path": "README.md", "content": "x"}})
    assert result.returncode == 0


def test_malformed_stdin_fails_open_with_exit_one() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD)],
        input="{not json",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "crashed" in result.stderr


def test_this_guard_is_wired_into_the_pre_action_hook() -> None:
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h["command"] for entry in settings["hooks"]["PreToolUse"] for h in entry["hooks"]]
    assert any("guard_protected_paths.py" in c for c in commands), commands

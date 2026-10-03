"""Tests for tooling/tools/guard_test_edits.py.

These call the real `classify` and the real process. Nothing is mocked, so nothing here can
pass if the decision function is deleted — see course/tickets/PROJ-142/09-tests-that-lie.md for why
that is the bar in this repo.

The exit-code tests exist because the codes ARE the contract: 2 blocks and feeds the model,
0-with-JSON asks a human, 1 is a non-blocking crash. A refactor that "simplifies" any of them
to a different number changes the guard's meaning silently, so each is pinned.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from guard_test_edits import ALLOW, ASK, DENY, classify, is_test_path, reconstruct_after

GUARD = Path(__file__).resolve().parents[2] / "tooling" / "tools" / "guard_test_edits.py"

STRONG = """
def test_export_streams_rows(account):
    result = export(account, chunk_size=10)
    assert result.splitlines()[0] == "id,email"
    assert len(result.splitlines()) == 101
"""

WEAKENED = """
def test_export_streams_rows(account):
    result = export(account, chunk_size=10)
    assert result is not None
"""

GUTTED = """
def test_export_streams_rows(account):
    export(account, chunk_size=10)
"""


# --- the path filter ---------------------------------------------------------------------


def test_recognises_test_paths() -> None:
    for path in (
        "tooling/tests/test_exports.py",
        "tooling/tools/tests/test_x.py",
        "src/__tests__/thing.ts",
        "test_exports.py",
        "exports_test.py",
        "src/exports.test.ts",
        "src/exports.spec.tsx",
    ):
        assert is_test_path(path), path


def test_production_code_is_not_a_test_path() -> None:
    for path in ("tooling/tools/check_touchpoints.py", "src/api/views.py", "README.md"):
        assert not is_test_path(path), path


def test_production_code_is_allowed_whatever_it_contains() -> None:
    assert classify(STRONG, "", "src/api/views.py").verdict == ALLOW


# --- the rules, in order -----------------------------------------------------------------


def test_a_new_test_file_is_allowed() -> None:
    assert classify("", STRONG, "tooling/tests/test_x.py").verdict == ALLOW


def test_adding_a_test_is_allowed() -> None:
    assert (
        classify(
            STRONG,
            STRONG + STRONG.replace("streams_rows", "streams_more"),
            "tooling/tests/test_x.py",
        ).verdict
        == ALLOW
    )


def test_zeroing_every_assertion_is_denied() -> None:
    decision = classify(STRONG, GUTTED, "tooling/tests/test_x.py")
    assert decision.verdict == DENY
    assert decision.signals["assertions"] == (2, 0)


def test_removing_a_test_asks() -> None:
    assert (
        classify(
            STRONG + STRONG.replace("streams_rows", "b"), STRONG, "tooling/tests/test_x.py"
        ).verdict
        == ASK
    )


def test_adding_a_skip_marker_asks() -> None:
    skipped = "@pytest.mark.skip(reason='flaky')\n" + STRONG
    assert classify(STRONG, skipped, "tooling/tests/test_x.py").verdict == ASK


def test_weakening_assertions_without_adding_a_test_asks() -> None:
    decision = classify(STRONG, WEAKENED, "tooling/tests/test_x.py")
    assert decision.verdict == ASK
    assert decision.signals["assertions"] == (2, 1)


def test_consolidating_assertions_while_adding_a_test_is_allowed() -> None:
    """The deliberate carve-out: folding weak asserts into one strong one IS authoring."""
    consolidated = (
        WEAKENED
        + """
def test_export_handles_empty(account):
    assert export(account, chunk_size=10) == "id,email\\n"
"""
    )
    assert classify(STRONG, consolidated, "tooling/tests/test_x.py").verdict == ALLOW


def test_a_formatter_reflow_is_allowed() -> None:
    reflowed = STRONG.replace("(account)", "(\n    account,\n)")
    assert classify(STRONG, reflowed, "tooling/tests/test_x.py").verdict == ALLOW


# --- reconstructing the post-edit content ------------------------------------------------


def test_edit_is_applied_once_by_default() -> None:
    after = reconstruct_after("Edit", {"old_string": "a", "new_string": "b"}, "a a")
    assert after == "b a"


def test_edit_replace_all_is_honoured() -> None:
    after = reconstruct_after(
        "Edit", {"old_string": "a", "new_string": "b", "replace_all": True}, "a a"
    )
    assert after == "b b"


def test_an_unfindable_old_string_allows_rather_than_guessing() -> None:
    assert reconstruct_after("Edit", {"old_string": "zzz", "new_string": "b"}, "a") is None


def test_an_unknown_tool_allows() -> None:
    assert reconstruct_after("SomeFutureTool", {"content": "x"}, "") is None


# --- the exit codes ARE the contract -----------------------------------------------------


def _run(payload: dict[str, object], mode: str = "enforce") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "GUARD_MODE": mode},
        check=False,
    )


def test_deny_uses_exit_two(tmp_path: Path) -> None:
    """Exit 2 is what feeds the reason back to the model. Not 1, which is a crash."""
    target = tmp_path / "tests" / "test_x.py"
    target.parent.mkdir()
    target.write_text(STRONG, encoding="utf-8")
    result = _run(
        {"tool_name": "Write", "tool_input": {"file_path": str(target), "content": GUTTED}}
    )
    assert result.returncode == 2
    assert "removes every assertion" in result.stderr


def test_ask_exits_zero_and_emits_the_json_channel(tmp_path: Path) -> None:
    target = tmp_path / "tests" / "test_x.py"
    target.parent.mkdir()
    target.write_text(STRONG, encoding="utf-8")
    result = _run(
        {"tool_name": "Write", "tool_input": {"file_path": str(target), "content": WEAKENED}}
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert "--explain" in payload["hookSpecificOutput"]["permissionDecisionReason"]


def test_log_mode_blocks_nothing(tmp_path: Path) -> None:
    """Ships in log mode: measure for a week before enforcing."""
    target = tmp_path / "tests" / "test_x.py"
    target.parent.mkdir()
    target.write_text(STRONG, encoding="utf-8")
    result = _run(
        {"tool_name": "Write", "tool_input": {"file_path": str(target), "content": GUTTED}},
        mode="log",
    )
    assert result.returncode == 0
    assert result.stdout == ""
    assert "log mode" in result.stderr


def test_malformed_stdin_fails_open_with_exit_one() -> None:
    """Not 0 (disappears silently) and not 2 (blocks all editing). Both are worse."""
    result = subprocess.run(
        [sys.executable, str(GUARD)],
        input="{not json",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "guard_test_edits.py: crashed" in result.stderr


def test_empty_stdin_is_allowed() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD)], input="", capture_output=True, text=True, check=False
    )
    assert result.returncode == 0


# --- the wiring, not just the script -----------------------------------------------------
#
# A guard that works and is not wired up is worth nothing, and this repo already shipped one
# script (check_touchpoints.py) that was built, tested and connected to nothing for four
# layers. These tests assert the connection itself, so "did someone delete the wiring" is a
# pytest failure rather than something a reviewer has to notice.

REPO = Path(__file__).resolve().parents[2]


def test_the_pre_action_wiring_exists_and_names_this_guard() -> None:
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    entries = settings["hooks"]["PreToolUse"]
    commands = [h["command"] for entry in entries for h in entry["hooks"]]
    assert any("guard_test_edits.py" in c for c in commands), commands


def test_the_matcher_covers_every_tool_that_can_write_a_file() -> None:
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    matchers = " ".join(entry["matcher"] for entry in settings["hooks"]["PreToolUse"])
    for tool in ("Edit", "MultiEdit", "Write", "NotebookEdit"):
        assert tool in matchers, f"{tool} can write a file and is not matched"


def test_the_configured_command_actually_runs(tmp_path: Path) -> None:
    """Run the command string from settings.json the way the host would, and check the verdict.

    This is the test that catches a typo'd path or a stale filename — the failure mode that
    leaves a guard silently inert while every unit test still passes.
    """
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    command = next(
        h["command"]
        for entry in settings["hooks"]["PreToolUse"]
        for h in entry["hooks"]
        if "guard_test_edits.py" in h["command"]
    )

    target = tmp_path / "tests" / "test_x.py"
    target.parent.mkdir()
    target.write_text(STRONG, encoding="utf-8")
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(target), "content": GUTTED}}

    result = subprocess.run(
        command,
        shell=True,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "CLAUDE_PROJECT_DIR": str(REPO), "GUARD_MODE": "enforce"},
        check=False,
    )
    assert result.returncode == 2, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert "removes every assertion" in result.stderr


def test_the_commit_time_half_is_wired_and_warns() -> None:
    """The host-agnostic half. Without it the rule only lands on one host."""
    config = (REPO / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "guard-test-edits" in config
    assert "guard_test_edits.py --staged" in config

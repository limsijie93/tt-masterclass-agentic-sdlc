#!/usr/bin/env python3
"""Refuse, at write time, an edit that weakens a test's assertions.

Eight places in this repo say some version of "do not modify a test IN ORDER TO make an
implementation pass". Nothing enforced it. In a repo whose segment 06 argues that a standard a
machine cannot check is a preference rather than a standard, that was a preference.

THE REFRAME THAT MAKES IT CHECKABLE. The clause carrying the meaning in all eight statements is
"in order to" — a claim about intent, and no guard observes intent. Making the rule executable
forces you to name the observable it was actually about, which is: **the edit weakens an
assertion.** That is checkable, and finding it out is the interesting part.

WHY THIS DOES NOT BREAK TDD. It does not block editing tests. It blocks *weakening* them.
Under test-first you create a file (allowed), add a failing test (assertions rise, allowed),
then edit production code (this guard never sees it). You never have to weaken an assertion to
work test-first. The only thing you cannot do silently is turn a red test green by editing the
test — which is the rule, stated in eight places.

TIER 0. This is the pre-action tier. `pre-commit` fires after the file is already written; this
fires before. Cheapest attention first: a guard is cheaper than a commit hook is cheaper than
CI, and the ladder's own rule — never spend a tier's attention on what the tier below could
catch — extends downward.

PORTABILITY. This file names no host. It reads JSON on stdin and writes JSON on stdout, and it
is also wired into `.pre-commit-config.yaml`, which is host-agnostic. So the rule lands on every
host; only the *timing* differs. The host-specific trigger lives in `.claude/settings.json` and
nowhere else.

Usage:
    (stdin JSON)                     pre-action guard; the host invokes this
    --explain <path>                 print the signal table for a file's working-tree state
    --staged                         warn on staged test files, always exit 0 (pre-commit)
    --diff-range <range>             emit CI annotations for a diff range, always exit 0
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- what counts as a test file ----------------------------------------------------------
# The host's matcher cannot filter by path, so the guard filters. Anything not matching is
# allowed without reading it — production code is none of this guard's business.
TEST_PATH_PATTERNS: tuple[str, ...] = (
    r"(^|/)tests?/",
    r"(^|/)__tests__/",
    r"(^|/)test_[^/]+\.py$",
    r"[^/]+_test\.py$",
    r"\.(test|spec)\.[jt]sx?$",
)

ASSERTION_PATTERNS: tuple[str, ...] = (
    r"^\s*assert\b",
    r"\bpytest\.raises\(",
    r"\bself\.assert\w+\(",
    r"\bexpect\(",
    r"\bassert\.\w+\(",
)

TEST_FN_PATTERNS: tuple[str, ...] = (
    r"^\s*(async\s+)?def\s+test_\w+",
    r"^\s*(it|test)\s*\(",
)

SUPPRESSION_PATTERNS: tuple[str, ...] = (
    r"@pytest\.mark\.skip",
    r"@pytest\.mark\.xfail",
    r"\bpytest\.skip\(",
    r"\.(skip|todo)\s*\(",
    r"^\s*x(it|describe)\s*\(",
)

ALLOW, ASK, DENY = "allow", "ask", "deny"


@dataclass(frozen=True)
class Decision:
    verdict: str
    reason: str
    signals: dict[str, tuple[int, int]] = field(default_factory=dict)


def _count(patterns: tuple[str, ...], text: str) -> int:
    return sum(len(re.findall(p, text, flags=re.M)) for p in patterns)


def is_test_path(path: str) -> bool:
    return any(re.search(p, path) for p in TEST_PATH_PATTERNS)


def classify(before: str, after: str, path: str) -> Decision:
    """Decide on one edit. Pure: no I/O, no environment, no host vocabulary."""
    if not is_test_path(path):
        return Decision(ALLOW, "not a test file")

    a_before, a_after = _count(ASSERTION_PATTERNS, before), _count(ASSERTION_PATTERNS, after)
    t_before, t_after = _count(TEST_FN_PATTERNS, before), _count(TEST_FN_PATTERNS, after)
    s_before, s_after = _count(SUPPRESSION_PATTERNS, before), _count(SUPPRESSION_PATTERNS, after)
    signals = {
        "assertions": (a_before, a_after),
        "tests": (t_before, t_after),
        "suppressions": (s_before, s_after),
    }

    # 1 — a new file cannot weaken anything.
    if not before.strip():
        return Decision(ALLOW, "new test file", signals)

    # 2 — every assertion gone. The only hard block: there is no authoring reason to take a
    # file that asserted something to a file that asserts nothing.
    if a_after == 0 and a_before > 0:
        return Decision(
            DENY,
            f"this edit removes every assertion from {path} "
            f"(assertions {a_before} -> 0). A test file that asserts nothing passes "
            "unconditionally, including with the code under test deleted.",
            signals,
        )

    # 3 — a test disappeared.
    if t_after < t_before:
        return Decision(
            ASK,
            f"this edit removes {t_before - t_after} test(s) from {path} "
            f"(tests {t_before} -> {t_after}).",
            signals,
        )

    # 4 — a test was switched off rather than fixed.
    if s_after > s_before:
        return Decision(
            ASK,
            f"this edit adds {s_after - s_before} skip/xfail marker(s) to {path}. "
            "Switching a test off is a decision a human should take deliberately.",
            signals,
        )

    # 5 — assertions dropped. The second clause is a deliberate carve-out: folding several
    # weak assertions into one strong one WHILE adding a test is authoring, not weakening.
    # It trades one bypass shape (add a junk test, delete real assertions) for a much lower
    # false-positive rate; the commit-time half catches what it lets through.
    if a_after < a_before and t_after <= t_before:
        return Decision(
            ASK,
            f"this edit removes {a_before - a_after} assertion(s) from {path} and adds no new "
            f"test (assertions {a_before} -> {a_after}, tests {t_before} -> {t_after}).",
            signals,
        )

    return Decision(ALLOW, "no weakening detected", signals)


def _explain_suffix(path: str) -> str:
    return (
        f"\nExplain:  python3 tooling/tools/guard_test_edits.py --explain {path}"
        "\nDeliberate? Approve, then say why in the pull request — the template already asks "
        "(Tier 1, second checkbox)."
    )


def reconstruct_after(tool_name: str, tool_input: dict[str, object], before: str) -> str | None:
    """Work out the post-edit content from the host's tool payload.

    Returns None when the shape is unknown, which means ALLOW — this guard does not
    second-guess a call the host is about to validate anyway.
    """
    if tool_name in {"Write", "NotebookEdit"}:
        content = tool_input.get("content") or tool_input.get("new_source")
        return content if isinstance(content, str) else None

    if tool_name == "Edit":
        old, new = tool_input.get("old_string"), tool_input.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str) or old not in before:
            return None
        count = -1 if tool_input.get("replace_all") else 1
        return before.replace(old, new, count)

    if tool_name == "MultiEdit":
        edits = tool_input.get("edits")
        if not isinstance(edits, list):
            return None
        text = before
        for edit in edits:
            if not isinstance(edit, dict):
                return None
            old, new = edit.get("old_string"), edit.get("new_string")
            if not isinstance(old, str) or not isinstance(new, str) or old not in text:
                return None
            text = text.replace(old, new, -1 if edit.get("replace_all") else 1)
        return text

    return None


def _target_of(tool_input: dict[str, object]) -> tuple[str, str] | None:
    """Resolve (repo-relative path, current on-disk content), or None to allow.

    Split out of run_guard so each half stays inside the complexity ceiling this repo
    enforces on itself — the same C901 rule course/templates/pyproject.toml sets for adopters.
    """
    raw_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(raw_path, str) or not raw_path:
        return None

    path = raw_path
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if root:
        try:
            path = str(Path(raw_path).resolve().relative_to(Path(root).resolve()))
        except ValueError:
            path = raw_path

    if not is_test_path(path):
        return None

    target = Path(raw_path)
    before = target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""
    return path, before


def _emit(decision: Decision, path: str) -> int:
    """Turn a verdict into the host's vocabulary. The only host-shaped function here."""
    # Land in log mode. course/templates/README.md prescribes the gentler step — measure before
    # enforcing — and gates-draft demands it of every generated gate. This is our own gate.
    if os.environ.get("GUARD_MODE", "log") != "enforce":
        if decision.verdict != ALLOW:
            print(
                f"guard_test_edits (log mode, nothing blocked): {decision.verdict} — "
                f"{decision.reason}",
                file=sys.stderr,
            )
        return 0

    if decision.verdict == DENY:
        print(f"guard_test_edits.py: {decision.reason}{_explain_suffix(path)}", file=sys.stderr)
        return 2

    if decision.verdict == ASK:
        # `ask` has no exit code; it travels on the JSON channel. `deny` uses exit 2 so the
        # reason reaches the model, which can then correct itself rather than retrying blind.
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "ask",
                        "permissionDecisionReason": (
                            f"guard_test_edits.py: {decision.reason}{_explain_suffix(path)}"
                        ),
                    }
                }
            )
        )
    return 0


def run_guard(payload: dict[str, object]) -> int:
    """The pre-action path. Returns the process exit code."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    target = _target_of(tool_input)
    if target is None:
        return 0
    path, before = target

    after = reconstruct_after(str(payload.get("tool_name", "")), tool_input, before)
    if after is None:
        return 0

    return _emit(classify(before, after, path), path)


def _report_paths(paths: list[str], label: str) -> int:
    """Shared body of --staged and --diff-range. Always exits 0: it warns, it does not block."""
    flagged = 0
    for path in paths:
        if not is_test_path(path) or not Path(path).is_file():
            continue
        after = Path(path).read_text(encoding="utf-8", errors="replace")
        before = subprocess.run(
            ["git", "show", f"HEAD:{path}"], capture_output=True, text=True, check=False
        ).stdout
        decision = classify(before, after, path)
        if decision.verdict == ALLOW:
            continue
        flagged += 1
        if label == "ci":
            print(f"::warning file={path}::{decision.reason}")
        else:
            print(f"guard_test_edits: {decision.verdict} — {decision.reason}")
    if flagged:
        print(
            f"\n{flagged} test file(s) look weakened. This warns rather than blocks — account "
            "for it in the pull request (Tier 1, second checkbox) if it was deliberate."
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--explain", metavar="PATH")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--diff-range", metavar="RANGE")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()

    if args.explain:
        path = args.explain
        after = Path(path).read_text(encoding="utf-8", errors="replace")
        before = subprocess.run(
            ["git", "show", f"HEAD:{path}"], capture_output=True, text=True, check=False
        ).stdout
        decision = classify(before, after, path)
        print(f"{path}\n  verdict: {decision.verdict}\n  reason:  {decision.reason}")
        for name, (was, now) in decision.signals.items():
            print(f"  {name:12} {was} -> {now}")
        return 0

    if args.staged:
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.split()
        return _report_paths(args.paths or staged, "staged")

    if args.diff_range:
        changed = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", args.diff_range],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.split()
        return _report_paths(changed, "ci")

    return run_guard(json.loads(sys.stdin.read() or "{}"))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # FAIL OPEN, LOUDLY. Exit 1 is neither "allow silently" nor "block": it is a
        # non-blocking error whose stderr reaches the human, not the model. A guard that
        # crashes must not disappear (nobody notices) and must not block all editing (deleted
        # by lunchtime). The commit-time half still fires.
        print(f"guard_test_edits.py: crashed — {exc}", file=sys.stderr)
        sys.exit(1)

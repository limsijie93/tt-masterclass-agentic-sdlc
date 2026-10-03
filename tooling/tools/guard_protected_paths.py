#!/usr/bin/env python3
"""Refuse, at write time, an agent edit to the guard machinery itself.

A guard the agent can disable is not a guard. That is the same argument
.claude/agents/read-only-explorer.md makes about its own tool allowlist — "the allowlist is
only an allowlist when it is present" — applied one level up: the allowlist and the guards are
now themselves a thing worth protecting.

WHY THIS ONE BLOCKS OUTRIGHT WHILE THE TEST GUARD ONLY ASKS. The cost of a false positive here
is zero. A pre-action guard never sees a human's editor, so a person editing these files is
never interrupted; only an agent is. That asymmetry earns the hard block here and denies it to
the test guard, where a deliberate test change is a legitimate thing a person does often.

WHY IT DOES NOT SHIP IN LOG MODE. The test guard does, because rolling a checker onto an
existing codebase produces a backlog that has to be measured first. Here there is nothing to
measure: this is a three-entry deny list on files that have no existing violations. "Measure
before enforcing" is advice about baselines, not a ritual.

THE HONEST LIMIT, and it is a large one. This sees the edit tools. It does not see a shell.
`cat > .claude/settings.json`, `sed -i`, `python -c`, `git checkout` — all invisible here, all
visible in the diff. That is the same hole read-only-explorer.md names when it refuses to
allowlist a shell, and it is the reason this file is a guard rather than a control: the control
is admin-set managed settings a developer cannot override, which is what
course/templates/managed-settings.example.json is for.
"""

from __future__ import annotations

import json
import os
import sys
from fnmatch import fnmatch
from pathlib import Path

# Deliberately three entries.
#
# NOT .github/workflows/ and NOT .pre-commit-config.yaml: this repo's own layers edit both
# constantly, and a protected list that grows to cover files the team actually edits becomes
# the mypy trap — the first legitimate change gets the guard deleted by someone in a hurry.
# The longer list belongs in a client repo, with that warning attached.
PROTECTED: tuple[str, ...] = (
    ".claude/settings.json",
    ".claude/settings.local.json",
    "tooling/tools/guard_*.py",
)

WRITING_TOOLS = frozenset({"Edit", "MultiEdit", "Write", "NotebookEdit"})


def is_protected(path: str) -> bool:
    return any(path == entry or fnmatch(path, entry) for entry in PROTECTED)


def relative_to_project(raw_path: str) -> str:
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if not root:
        return raw_path
    try:
        return str(Path(raw_path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return raw_path


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")

    if str(payload.get("tool_name", "")) not in WRITING_TOOLS:
        return 0

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    raw_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(raw_path, str) or not raw_path:
        return 0

    path = relative_to_project(raw_path)
    if not is_protected(path):
        return 0

    print(
        f"guard_protected_paths.py: {path} is guard machinery and is not agent-editable.\n"
        "A guard the agent can disable is not a guard.\n"
        "If this change is right, a human makes it — and it will be reviewed, because "
        f"{PROTECTED[0]} is owned in .github/CODEOWNERS.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # Fail open, loudly — exit 1, same contract as the test guard. A crashing guard must
        # not silently vanish, and must not block all editing.
        print(f"guard_protected_paths.py: crashed — {exc}", file=sys.stderr)
        sys.exit(1)

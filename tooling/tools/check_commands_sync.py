#!/usr/bin/env python3
"""Fail if AGENTS.md's Commands section and the pre-commit config enforce different tools.

The lecture claims the constraint an agent obeys and the gate a pull request passes are the
same rule. Argv identity is not achievable and pretending otherwise ships a broken file:
pre-commit is file-scoped by design, `lint-imports` is whole-graph and cannot be diff-scoped,
and `pytest` does not belong at commit time.

So the checkable claim is narrower and stronger: **the same SET OF TOOLS**, configured in the
same single place per tool. Scope may differ. The tool set may not.

This one blocks rather than warns — unlike tooling/tools/check_touchpoints.py — because a divergence
between the context file and the gate is precisely the rot the lecture warns about, and
because it cannot produce a false positive. Which checks earn the right to block is a
decision worth making deliberately, one at a time.

No YAML dependency: the `entry:` lines of a file this repo owns are extracted with a regex,
which is adequate for a file whose shape is fixed by the same repo that reads it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "course" / "templates"

# Hooks that are housekeeping rather than a standard anyone states in prose. A context file
# that listed "trim trailing whitespace" under Commands would be noise, and noise in a
# context file is how the whole file stops being read.
IGNORED_HOOK_TOOLS = frozenset(
    {
        "detect-secrets-hook",
        "check-merge-conflict",
        "end-of-file-fixer",
        "trailing-whitespace",
        "mixed-line-ending",
        "check-yaml",
        "check-toml",
        "jscpd",
    }
)


def tool_of(command: str) -> str | None:
    """Reduce a command line to the tool it invokes.

    `ruff format .` and `ruff check --fix` are both the ruff tool: they are the same rule
    set read from the same config, differing only in what they do with it.
    """
    parts = [p for p in command.strip().split() if p]
    if not parts:
        return None
    tool = parts[0]
    if tool in {"python", "python3"} and len(parts) > 1:
        return Path(parts[1]).name
    return tool


def tools_in_agents_md(path: Path) -> set[str]:
    """Tools named in the fenced block under `## Commands`."""
    if not path.is_file():
        raise SystemExit(f"check_commands_sync: {path} not found")

    lines = path.read_text(encoding="utf-8").splitlines()
    tools: set[str] = set()
    in_commands = False
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_commands = stripped.lower() == "## commands"
            continue
        if not in_commands:
            continue
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence and stripped:
            tool = tool_of(stripped)
            if tool:
                tools.add(tool)
    return tools


def tools_in_precommit(path: Path) -> set[str]:
    """Tools named by `entry:` lines, plus hook ids from third-party repos."""
    if not path.is_file():
        raise SystemExit(f"check_commands_sync: {path} not found")

    text = path.read_text(encoding="utf-8")
    # Drop comments so the commented-out jscpd block does not register as a live hook.
    live = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))

    tools: set[str] = set()
    for entry in re.findall(r"^\s*entry:\s*(.+)$", live, flags=re.M):
        tool = tool_of(entry)
        if tool and tool not in IGNORED_HOOK_TOOLS:
            tools.add(tool)
    for hook_id in re.findall(r"^\s*-\s*id:\s*([\w.-]+)\s*$", live, flags=re.M):
        if hook_id in IGNORED_HOOK_TOOLS:
            continue
        # `- id:` under a third-party repo names the tool; under `local` the entry above
        # already covered it, and a duplicate in a set costs nothing.
        if hook_id == "detect-secrets":
            tools.add("detect-secrets")
    return tools


def check_example(directory: Path) -> bool:
    """Check one ecosystem's AGENTS.md against its own pre-commit config.

    Every directory under course/templates/ is a self-contained fill of the same shape, so each one
    has to be internally consistent on its own terms. Checking them as a set would compare a
    Python tool list against a TypeScript gate, which is meaningless.
    """
    agents_md = directory / "AGENTS.md"
    precommit = directory / "pre-commit-config.yaml"
    if not agents_md.is_file() or not precommit.is_file():
        print(f"  {directory.name}: skipped (needs both AGENTS.md and pre-commit-config.yaml)")
        return True

    declared = tools_in_agents_md(agents_md)
    enforced = tools_in_precommit(precommit)

    # detect-secrets is a gate but not a standard anyone writes in prose; exempt it
    # symmetrically rather than requiring a Commands line nobody would read.
    enforced.discard("detect-secrets")

    missing_from_agents = enforced - declared
    missing_from_gate = declared - enforced

    if not missing_from_agents and not missing_from_gate:
        print(f"  {directory.name}: {len(declared)} tools agree — {', '.join(sorted(declared))}")
        return True

    print(f"  {directory.name}: DIVERGED")
    if missing_from_agents:
        print(
            f"    Enforced by pre-commit-config.yaml but NOT in AGENTS.md Commands:\n"
            f"      {', '.join(sorted(missing_from_agents))}\n"
            "    The agent will not run these before showing you code, so they fail in CI\n"
            "    instead of on the developer's machine."
        )
    if missing_from_gate:
        print(
            f"    In AGENTS.md Commands but NOT enforced by pre-commit-config.yaml:\n"
            f"      {', '.join(sorted(missing_from_gate))}\n"
            "    This is the worse direction: the context file describes a gate that does not\n"
            "    exist, which is an aspirational rule, and the agent believes it."
        )
    return False


def main() -> int:
    if not EXAMPLES.is_dir():
        raise SystemExit(f"check_commands_sync: {EXAMPLES} not found")

    directories = sorted(d for d in EXAMPLES.iterdir() if d.is_dir())
    if not directories:
        raise SystemExit(f"check_commands_sync: no ecosystems under {EXAMPLES}")

    print(f"check_commands_sync: {len(directories)} ecosystem(s)")
    results = [check_example(d) for d in directories]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())

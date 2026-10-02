#!/usr/bin/env python3
"""Compare the files a branch changed against the touchpoints its spec declared.

Segment 07 leaves this as a manual habit: run `git diff --stat` and eyeball it against the
touchpoints list. The lecture's own thesis says a habit worth repeating belongs in a file, so
here it is.

WARNS BY DEFAULT, and that is deliberate. Two reasons:

1. It cannot see the dangerous case. A refactor that stays entirely inside the touchpoints and
   changes what the code means is invisible to this script. Sold as "scope-creep detection" it
   would be trusted for something it cannot do.
2. A hard block on scope creep is the mypy trap in miniature. The first legitimate
   out-of-bounds change gets the check disabled, permanently, by someone in a hurry.

`--strict` turns it into a gate for teams that want one. Which things earn the right to block
is itself a decision worth making on purpose.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TOUCHPOINT_RE = re.compile(r"^\s*(?:\(!\)\s*)?([\w./*-]+\.\w+|[\w./*-]+/)(?::\d+)?")


def run(*args: str) -> str:
    """Run a git command and return stdout, or an empty string if git fails."""
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True, timeout=30).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def ticket_from_branch() -> str | None:
    """Pull a ticket id like PROJ-142 out of the current branch name."""
    branch = run("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
    match = re.search(r"[A-Z]{2,}-\d+", branch)
    return match.group(0) if match else None


def parse_touchpoints(text: str) -> tuple[set[str], set[str]]:
    """Return (declared paths, allowed extra globs) from a spec's markdown.

    Reads the fenced block under `## Touchpoints`, and any bullets under an optional
    `## Allowed extras` heading.
    """
    declared: set[str] = set()
    extras: set[str] = set()

    section: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped.lower()
            continue
        if stripped in {"```", "```text", "```plain text"}:
            continue
        if not stripped:
            continue
        if section == "## touchpoints":
            match = TOUCHPOINT_RE.match(line)
            if match:
                declared.add(match.group(1))
        elif section == "## allowed extras" and stripped.startswith(("-", "*")):
            extras.add(stripped.lstrip("-* ").strip("`"))
    return declared, extras


def changed_files(base: str) -> list[str]:
    merge_base = run("git", "merge-base", base, "HEAD").strip()
    if not merge_base:
        return []
    out = run("git", "diff", "--name-only", "--diff-filter=ACMR", f"{merge_base}...HEAD")
    return [line for line in out.splitlines() if line.strip()]


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Compile a path glob in which `*` does NOT cross a separator.

    `fnmatch` is the obvious choice and the wrong one: its `*` matches `/`, so `docs/*.md`
    would quietly cover `docs/nested/deep/whatever.md` and the allowlist would mean nothing.
    """
    out = ["^"]
    i = 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    out.append("$")
    return re.compile("".join(out))


def is_covered(path: str, declared: set[str], extras: set[str]) -> bool:
    for entry in declared | extras:
        if path == entry:
            return True
        if entry.endswith("/") and path.startswith(entry):
            return True
        if any(ch in entry for ch in "*?") and _glob_to_regex(entry).match(path):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", help="path to the spec; inferred from the branch name if omitted")
    parser.add_argument("--base", default="origin/main", help="branch to diff against")
    parser.add_argument(
        "--strict", action="store_true", help="exit 1 on an out-of-bounds file instead of warning"
    )
    args = parser.parse_args()

    spec_path = Path(args.spec) if args.spec else None
    if spec_path is None:
        ticket = ticket_from_branch()
        if ticket is None:
            print("check_touchpoints: no ticket id in the branch name; nothing to check.")
            return 0
        spec_path = Path("specs") / f"{ticket}.md"

    if not spec_path.is_file():
        print(f"check_touchpoints: no spec at {spec_path}; nothing to check.")
        return 0

    declared, extras = parse_touchpoints(spec_path.read_text(encoding="utf-8"))
    if not declared:
        print(f"check_touchpoints: {spec_path} declares no touchpoints; nothing to check.")
        return 0

    outside = [p for p in changed_files(args.base) if not is_covered(p, declared, extras)]
    if not outside:
        print(
            f"check_touchpoints: all changed files are inside the {len(declared)} declared "
            f"touchpoints."
        )
        return 0

    for path in outside:
        # GitHub renders this as an annotation on the pull request.
        print(f"::warning file={path}::changed but not declared in {spec_path}")
    print(
        f"\ncheck_touchpoints: {len(outside)} file(s) outside the declared touchpoints.\n"
        "This is the signal, not the verdict. Either the spec should have named them, or the\n"
        "change drifted. Both are worth a sentence in the pull request."
    )
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())

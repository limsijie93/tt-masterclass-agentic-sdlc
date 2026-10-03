#!/usr/bin/env python3
"""Run the eval cases: execute a skill for real, then assert properties of what it produced.

    tooling/scripts/lint_skills.py proves the contracts fit together.
    This proves a skill keeps its own.

THE SABOTAGE THIS HARNESS MUST FAIL, and the reason to read that first:

    EVAL_ENGINE_CMD=true python3 tooling/tools/run_evals.py --all      ->  0/7 passed

A no-op engine must fail EVERY case, including the negative controls. A negative control
asserting "the skill did not write the spec" passes trivially if nothing ran at all — which is
exactly the shape of the `semgrep --test --config` false green documented in
.semgrep/README.md, reincarnated somewhere new. Every negative assertion in a case is therefore
paired with a positive one that a no-op engine cannot satisfy.

THE FIXTURE PROBLEM, and how it is avoided. The tempting design is to feed the worked ticket in
and compare the output with course/tickets/PROJ-142/02-interrogation.md. It is non-deterministic
AND tautological: it asserts the model reproduces one hand-polished past output. Applying this
repo's own test — delete the thing under test, does the check still pass? — three rules follow:

  1. A case's expected outcome is a list of named properties, never a file.
  2. The codebase under test is THIS repository, and a case's ticket is a real gap in it. The
     skills need code to ground in, not application code, and tooling/'s scripts/, tools/ and
     tests/ are real and citable by line. The ticket is written for the eval, by no skill, so
     there is nothing to reproduce.
  3. The worktree is sanitised before the engine sees it: course/tickets/PROJ-142/ and
     tooling/evals/ are deleted, so the worked chain is physically absent and cannot be copied from.

Rule 3 is enforced by a unit test, so removing it is a pytest failure rather than something a
reviewer has to notice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from eval_assertions import REGISTRY, EvalContext

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = REPO_ROOT / "tooling" / "evals" / "cases"

# Removed from the eval worktree before the engine runs. The worked chain is the answer key,
# and tooling/evals/ contains the assertions — neither may be visible to the thing under test.
SANITISE = ("course/tickets/PROJ-142", "tooling/evals")


@dataclass
class Case:
    path: Path
    skill: str
    stability: str
    assertions: list[dict[str, object]]
    prompt: str
    setup: dict[str, str]
    negative_control: bool


def _scalar(value: str) -> object:
    """JSON where it parses, a bare string otherwise.

    So `path: "specs/x.md"`, `usd: 0.60`, `tokens: ["a","b"]` and `name: did_not_write` all
    work, and a case author does not have to remember which values need quoting.
    """
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def parse_frontmatter(front: str) -> tuple[dict[str, str], list[dict[str, object]]]:
    """Flat `key: value` pairs, plus an `assertions:` list of dicts. No YAML dependency."""
    meta: dict[str, str] = {}
    assertions: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    in_assertions = False

    for raw in front.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.rstrip() == "assertions:":
            in_assertions = True
            continue
        if not in_assertions:
            key, _, value = raw.partition(":")
            meta[key.strip()] = value.strip()
            continue
        line = raw
        if line.lstrip().startswith("- "):
            current = {}
            assertions.append(current)
            line = line.replace("- ", "", 1)
        if current is not None and ":" in line:
            key, _, value = line.strip().partition(":")
            current[key.strip()] = _scalar(value.strip())
    return meta, assertions


def split_top_sections(body: str) -> dict[str, list[str]]:
    """Group a case body into its `## ` sections, ignoring headings inside fences.

    Fence-awareness is not optional here: a setup file's CONTENT is usually a spec or an
    answers file, which contains `## Goal` and friends. Treating those as section headings
    silently drops every setup file after the first, and the case then fails for the wrong
    reason — which is worse than failing.

    This is the SECOND hand-rolled markdown parser in this repo to have had exactly this bug;
    tooling/scripts/lint_skills.py's split_sections had it too. The rule written here when that was
    noticed -- if a third appears, share the helper rather than rediscover the bug -- is why
    this function and parse_frontmatter are public: tooling/tools/lab.py is the third reader, and it
    imports these rather than growing its own.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        elif line.startswith("## ") and not in_fence:
            current = line[3:].strip().lower()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def _parse_setup(lines: list[str]) -> dict[str, str]:
    """`### path` headings, each followed by a fenced block of that file's content."""
    setup: dict[str, str] = {}
    filename: str | None = None
    buffer: list[str] = []
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if line.startswith("### ") and not in_fence:
            if filename:
                setup[filename] = "\n".join(buffer).strip("\n") + "\n"
            filename, buffer = line[4:].strip(), []
        elif filename:
            buffer.append(line)
    if filename:
        setup[filename] = "\n".join(buffer).strip("\n") + "\n"
    return setup


def _parse_body(body: str) -> tuple[str, dict[str, str]]:
    sections = split_top_sections(body)
    prompt = "\n".join(sections.get("prompt", [])).strip()
    return prompt, _parse_setup(sections.get("setup", []))


def parse_case(path: Path) -> Case:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name}: no frontmatter")
    end = text.index("\n---\n", 4)

    meta, assertions = parse_frontmatter(text[4:end])
    prompt, setup = _parse_body(text[end + 5 :])

    return Case(
        path=path,
        skill=meta.get("skill", ""),
        stability=meta.get("stability", ""),
        assertions=assertions,
        prompt=prompt,
        setup=setup,
        negative_control=meta.get("negative_control", "false") == "true",
    )


def sanitise_worktree(root: Path) -> list[str]:
    """Delete the answer key from the worktree. Returns what was removed.

    Unit-tested, so deleting this call is a test failure rather than a review miss.
    """
    removed = []
    for relative in SANITISE:
        target = root / relative
        if target.exists():
            shutil.rmtree(target)
            removed.append(relative)
    return removed


def _snapshot(root: Path) -> dict[str, str]:
    digests = {}
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            digests[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def _written_since(root: Path, before: dict[str, str]) -> dict[str, str]:
    after = _snapshot(root)
    changed = {p for p, d in after.items() if before.get(p) != d}
    return {p: (root / p).read_text(encoding="utf-8", errors="replace") for p in sorted(changed)}


def run_case(case: Case, engine: str) -> tuple[bool, list[str]]:
    lines: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        worktree = Path(tmp) / "wt"
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        )
        try:
            removed = sanitise_worktree(worktree)
            lines.append(f"    sanitised: removed {removed}")

            for relative, content in case.setup.items():
                target = worktree / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")

            before = _snapshot(worktree)
            result = subprocess.run(
                engine,
                shell=True,
                cwd=worktree,
                input=case.prompt,
                capture_output=True,
                text=True,
                timeout=900,
                check=False,
            )
            written = _written_since(worktree, before)
            for relative in case.setup:
                written.pop(relative, None)

            cost = None
            match = re.search(r'"total_cost_usd"\s*:\s*([0-9.]+)', result.stdout)
            if match:
                cost = float(match.group(1))

            ctx = EvalContext(
                worktree=worktree,
                written=written,
                output=result.stdout + result.stderr,
                cost_usd=cost,
            )

            passed = True
            for spec in case.assertions:
                name = str(spec.get("name", ""))
                check = REGISTRY.get(name)
                if check is None:
                    lines.append(f"    ✗ unknown assertion {name!r}")
                    passed = False
                    continue
                kwargs = {k: v for k, v in spec.items() if k != "name"}
                try:
                    ok, detail = check(ctx, **kwargs)
                except Exception as exc:
                    ok, detail = False, f"assertion raised {exc}"
                lines.append(f"    {'✓' if ok else '✗'} {name}: {detail}")
                passed = passed and ok
            if cost is not None:
                lines.append(f"    cost: ${cost:.4f}")
            return passed, lines
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=REPO_ROOT,
                capture_output=True,
                check=False,
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--case", metavar="NAME")
    args = parser.parse_args()

    engine = os.environ.get("EVAL_ENGINE_CMD")
    if not engine:
        # No default is baked in on purpose. A wrong default would silently run the wrong
        # thing, and this repo does not ship unverified commands — see tooling/evals/README.md for
        # the invocation and what to check before trusting it.
        print(
            "EVAL_ENGINE_CMD is not set. See tooling/evals/README.md for the invocation.\n"
            "It reads the prompt on stdin, runs with the worktree as its working directory, "
            "and may write files.",
            file=sys.stderr,
        )
        return 1

    cases = sorted(CASES_DIR.glob("*.md"))
    if args.case:
        cases = [c for c in cases if c.stem == args.case]
    if not cases:
        print("no cases found", file=sys.stderr)
        return 1

    results = []
    for path in cases:
        case = parse_case(path)
        print(f"\n{path.stem}  (skill: {case.skill}, stability: {case.stability})")
        ok, lines = run_case(case, engine)
        print("\n".join(lines))
        print(f"  {'PASS' if ok else 'FAIL'}")
        results.append(ok)

    passed = sum(results)
    print(f"\n{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

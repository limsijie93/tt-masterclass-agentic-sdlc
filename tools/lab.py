#!/usr/bin/env python3
"""Run a lab: print the brief, then check what the learner produced.

    A lab is an eval case with a human as the engine.

tools/run_evals.py shells out to $EVAL_ENGINE_CMD and asserts properties of what came back.
A lab does everything else identically and, in place of that one call, prints the brief and
waits for a person. Same file format, same frontmatter parser, same assertion registry. The
learner is the engine.

That reuse is the whole design, and it buys three things:

  1. An assertion vocabulary that already exists, and is already argued for. What may be
     asserted about a skill's output is what may be asserted about a learner's -- shape,
     arity, refusal, citation resolvability -- and for the same reason: prose is not
     checkable and a flaky check destroys trust in about a week.
  2. No second authoring format. If a lab cannot be written as a case, the lab is wrong.
  3. The two rules below, inherited rather than rediscovered.

THE FIRST RULE: A NO-OP MUST SCORE ZERO. `lab.py check NN` on an untouched checkout scores
0/N for every lab, and tests/test_labs_are_wired.py enforces it. This is EVAL_ENGINE_CMD=true
one level up: a grader that passes an empty submission is a test that cannot fail, and it
looks like success. It is also not hypothetical here -- `max_lines` written the obvious way
passes on a file that does not exist, because nought lines is under every limit.

THE SECOND RULE: SAY WHOSE FAULT IT IS. Some assertions are about the learner's work and some
are about whether their assistant honoured a stop condition. When one of the second kind
fails, the report says so and points at LEARN.md. A learner on a weaker host must not read
"your assistant answered its own questions" as "you failed".

WHERE LABS RUN. In the learner's own checkout, not a temp worktree. They need their editor,
their assistant and their history; an eval needs isolation and a lab needs the opposite. The
answer key is kept out of reach by course/labs/AGENTS.md rather than by deletion -- the same device
course/tickets/PROJ-142/AGENTS.md uses for the two planted fixtures.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from eval_assertions import REGISTRY, EvalContext, Result
from run_evals import parse_frontmatter, split_top_sections

REPO_ROOT = Path(__file__).resolve().parent.parent
LABS_DIR = REPO_ROOT / "course" / "labs"

# Assertions whose failure is a finding about the learner's ASSISTANT, not about the learner.
# Every one of them is a stop condition -- the thing this repo says is its actual product, and
# the thing models actually fail at.
ASSISTANT_BEHAVIOUR = frozenset(
    {
        "contains_sentinel",
        "every_answer_line_empty",
        "max_questions",
        "at_most_one_blocking",
        "findings_between",
    }
)

TIER_NAMES = {1: "tier 1 · machine · blocks", 2: "tier 2 · key · comments"}


def command_exits(ctx: EvalContext, cmd: str, code: int, needs: list[str] | None = None) -> Result:
    """Run a command and check its exit status.

    LAB-ONLY, and deliberately absent from eval_assertions.REGISTRY. An eval already shells
    out once, to the engine; letting a CASE FILE name a second command would mean a file
    describing what a skill should produce could also run anything on the machine checking
    it. Labs 02 and 03 are irreducibly about watching a gate flip from passing to failing,
    so here the capability is the exercise.

    `needs` names the executables the command requires, and it is not optional politeness.
    An earlier version checked `returncode == 127` instead, which CANNOT WORK for any
    command containing a pipe: a pipeline's status is its LAST stage's, so
    `lint-imports ... | grep -q X` with lint-imports missing exits 1, from grep, and reads
    as "the check failed" rather than "the tool is absent". Both labs that use this are
    pipelines. It failed in CI, telling a learner their import contract was wrong when
    nothing was installed -- the worst possible direction for a checker to be wrong in.

    `set -o pipefail` looks like the one-word fix and is not: lint-imports exits 1 on a
    broken contract, which is the state lab 02 is engineering, so pipefail would fail the
    check exactly when the learner got it right.
    """
    for tool in needs or []:
        if shutil.which(tool) is None:
            return False, f"`{tool}` is not installed -- run `make setup`, then activate .venv"
    done = subprocess.run(cmd, shell=True, cwd=ctx.worktree, capture_output=True, text=True)
    ok = done.returncode == code
    return ok, f"`{cmd}` exited {done.returncode}, expected {code}"


LAB_ONLY: dict[str, object] = {"command_exits": command_exits}


@dataclass
class Lab:
    slug: str
    number: str
    title: str
    segment: str
    needs: str
    minutes: str
    solution_into: str
    sections: dict[str, str]
    assertions: list[dict[str, object]]

    @property
    def directory(self) -> Path:
        return LABS_DIR / self.slug

    @property
    def needs_an_agent(self) -> bool:
        return self.needs == "agent"


def parse_lab(path: Path) -> Lab:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: no frontmatter")
    end = text.index("\n---\n", 4)
    meta, assertions = parse_frontmatter(text[4:end])
    # run_evals keeps frontmatter scalars as raw strings, so `lab: "01"` arrives with its
    # quotes. Strip them here rather than forbidding quotes: `lab: 01` is YAML for the number
    # one, and a lab author who writes it either way should get "01" both times.
    meta = {k: v.strip("\"'") for k, v in meta.items()}
    sections = {
        name: "\n".join(body).strip() for name, body in split_top_sections(text[end + 5 :]).items()
    }
    return Lab(
        slug=path.parent.name,
        number=meta.get("lab", ""),
        title=meta.get("title", ""),
        segment=meta.get("segment", ""),
        needs=meta.get("needs", "agent"),
        minutes=meta.get("minutes", "?"),
        # Where solution/ lands when it is applied. One flat key rather than a per-file
        # mapping: every lab's answer key happens to go to a single directory, and a
        # mapping format nobody needs is a format somebody has to maintain.
        solution_into=meta.get("solution_into", ""),
        sections=sections,
        assertions=assertions,
    )


def all_labs() -> list[Lab]:
    return [parse_lab(p) for p in sorted(LABS_DIR.glob("*/lab.md"))]


def find(number: str) -> Lab:
    wanted = number.lstrip("0") or "0"
    for lab in all_labs():
        if (lab.number.lstrip("0") or "0") == wanted:
            return lab
    raise SystemExit(f"no lab {number!r}. `lab.py` with no arguments lists them.")


def run_checks(lab: Lab, root: Path = REPO_ROOT) -> tuple[int, int, list[str]]:
    """Every assertion, grouped by tier. Returns passed, total, and the report lines.

    `root` is a parameter only so tests can point it at a clean worktree. The no-op rule --
    an untouched checkout scores nought -- cannot be tested against the developer's own
    checkout, because a developer who has done a lab would fail the build. A test that fails
    for doing the thing the repo is for is the same flaky gate this repo warns about.
    """
    ctx = EvalContext(worktree=root)
    lines: list[str] = []
    passed = total = 0

    for tier in (1, 2):
        specs = [s for s in lab.assertions if int(str(s.get("tier", 1))) == tier]
        if not specs:
            continue
        lines.append(f"\n  {TIER_NAMES[tier]}")
        for spec in specs:
            name = str(spec.get("name", ""))
            hint = str(spec.get("hint", ""))
            check = REGISTRY.get(name) or LAB_ONLY.get(name)
            if check is None:
                lines.append(f"    ✗ unknown assertion {name!r}")
                total += 1
                continue
            kwargs = {k: v for k, v in spec.items() if k not in {"name", "tier", "hint"}}
            try:
                ok, detail = check(ctx, **kwargs)  # type: ignore[operator]
            except Exception as exc:  # a broken lab file must read as broken, not as a fail
                ok, detail = False, f"assertion raised {exc}"
            lines.append(f"    {'✓' if ok else '✗'} {name}: {detail}")
            # When the file was never written, the assertion line already says everything
            # true. A hint about question counts, or a note blaming the assistant's stop
            # condition, would both be guesses about a run that produced nothing.
            nothing_produced = "absent or empty" in detail
            if not ok and hint and not nothing_produced:
                lines.append(f"        → {hint}")
            if not ok and not nothing_produced and name in ASSISTANT_BEHAVIOUR:
                lines.append(
                    "        → this one is about your assistant, not about you: it did not "
                    "hold a stop condition."
                )
                lines.append("          That is worth knowing about your tool. See LEARN.md.")
            total += 1
            passed += ok
    return passed, total, lines


def write_report(lab: Lab, passed: int, total: int, lines: list[str]) -> Path:
    report = lab.directory / "report.md"
    body = [
        f"# lab {lab.number} — {lab.title}",
        "",
        f"    {date.today().isoformat()}   {passed}/{total} machine-checkable points",
        "",
        "```",
        *(line.rstrip() for line in lines),
        "```",
        "",
        "Tier 3 is yours. Read `## What good looks like` in `lab.md`, then write one or two",
        "sentences below on what you would do differently. That sentence is the deliverable;",
        "everything above it is how you earned the right to write it.",
        "",
        "## What I would do differently",
        "",
        "",
    ]
    report.write_text("\n".join(body), encoding="utf-8")
    return report


def cmd_list() -> int:
    print("\nLabs. Do them in order — 01 to 03 need no agent and no API key.\n")
    print(f"  {'':<4}{'lab':<34}{'seg':<6}{'needs':<10}{'time':<8}status")
    for lab in all_labs():
        report = lab.directory / "report.md"
        status = "done" if report.exists() else "—"
        needs = "an agent" if lab.needs_an_agent else "no agent"
        print(
            f"  {lab.number:<4}{lab.title:<34}{lab.segment:<6}{needs:<10}"
            f"{lab.minutes + ' min':<8}{status}"
        )
    print("\n  python3 tools/lab.py start 01     the brief")
    print("  python3 tools/lab.py check 01     what you produced")
    print("  python3 tools/lab.py solution 01  after you have attempted it\n")
    return 0


def cmd_start(lab: Lab) -> int:
    print(
        f"\n{'=' * 78}\nlab {lab.number} · {lab.title} · segment {lab.segment} "
        f"· about {lab.minutes} minutes\n{'=' * 78}"
    )
    for section in ("brief", "start"):
        if lab.sections.get(section):
            print(f"\n{lab.sections[section]}\n")
    print(f"{'-' * 78}\nWhen you are done:  python3 tools/lab.py check {lab.number}\n")
    return 0


def cmd_check(lab: Lab) -> int:
    passed, total, lines = run_checks(lab)
    print(f"\nlab {lab.number} · {lab.title}")
    print("\n".join(lines))
    report = write_report(lab, passed, total, lines)
    print(f"\n  {passed}/{total} — {'PASS' if passed == total else 'not yet'}")
    print(f"  written: {report.relative_to(REPO_ROOT)}")
    if passed == total:
        print(f"\n  Now read the solution:  python3 tools/lab.py solution {lab.number}")
        print("  It is not a victory lap. It is where the reasoning is.\n")
    else:
        print("\n  Nothing here judges whether your answer is GOOD — only whether it has the")
        print("  shape the contract promises. Tier 3 is the part no checker reaches.\n")
    return 0 if passed == total else 1


def cmd_solution(lab: Lab) -> int:
    body = lab.sections.get("what good looks like")
    if not body:
        raise SystemExit(f"lab {lab.number} has no solution section")
    print(f"\n{'=' * 78}\nlab {lab.number} · what good looks like\n{'=' * 78}\n")
    print(body + "\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a lab.")
    parser.add_argument(
        "action", nargs="?", default="list", choices=["list", "start", "check", "solution"]
    )
    parser.add_argument("lab", nargs="?")
    args = parser.parse_args()

    if args.action == "list":
        return cmd_list()
    if not args.lab:
        raise SystemExit(f"which lab? e.g. `lab.py {args.action} 01`")
    lab = find(args.lab)
    return {"start": cmd_start, "check": cmd_check, "solution": cmd_solution}[args.action](lab)


if __name__ == "__main__":
    sys.exit(main())

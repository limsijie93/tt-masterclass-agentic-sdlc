#!/usr/bin/env python3
"""Assertions an eval case may make about a skill's actual output.

scripts/lint_skills.py proves the skills' DECLARED contracts fit together — it reads
`## Output contract` as text. Nothing until now ever executed a skill, so nothing checked that
a skill HONOURS the contract it declares.

    The linter proves the contracts fit together. An eval proves a skill keeps its own.

WHAT MAY BE ASSERTED, AND WHY THAT LINE IS WHERE IT IS. Model output is non-deterministic, and
this repo says three separate times that a flaky gate destroys trust in about a week. Every
assertion here is therefore a property of the output's SHAPE or of the skill's STOPPING
BEHAVIOUR, never of its prose:

  - existence and arity      which files were written
  - cardinality bounds       at most five questions; nought to three findings
  - structural invariants    every question carries both fields; sections in order
  - refusal behaviour        given an unanswered question, no spec was produced
  - citation resolvability   every path:line names a real file with that many lines
  - verbatim inclusion       the contract says "quoted verbatim", so verbatim is checkable
  - banned tokens            the anti-patterns lists are already token lists
  - cost                     a runaway skill is a real regression and the cheapest check here

WHAT MAY NOT. Exact question text; WHICH five questions were chosen; the ranking order of
findings; whether a finding is correct; word counts.

And explicitly, so nobody adds one later thinking it was an oversight: **no LLM-as-judge
grader.** A non-deterministic grader over a non-deterministic output is two coin flips, and
when it fails you cannot tell whether the skill regressed or the judge did.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

SENTINEL_STOPPED = "[ stopped - waiting for a human ]"


@dataclass
class EvalContext:
    """Everything an assertion may look at. Nothing else is available to it, on purpose."""

    worktree: Path
    written: dict[str, str] = field(default_factory=dict)
    output: str = ""
    cost_usd: float | None = None

    def content(self, path: str) -> str:
        if path in self.written:
            return self.written[path]
        candidate = self.worktree / path
        return candidate.read_text(encoding="utf-8") if candidate.is_file() else ""

    def question_blocks(self, path: str) -> list[str]:
        """Split an answers file into numbered question blocks."""
        body = self.content(path)
        parts = re.split(r"^\s*(\d+)\s{2,}", body, flags=re.M)
        return [parts[i + 1] for i in range(1, len(parts) - 1, 2)]


Result = tuple[bool, str]


def _absent(ctx: EvalContext, path: str) -> str | None:
    """The reason to fail, when the file an assertion is about was never written.

    Nearly every assertion below is vacuously true of a file that does not exist: nought
    questions is under every cap, nought citations all resolve, and no answer line is filled
    in a file with no answer lines. Each one then passes when the skill did nothing at all.

    That is the no-op engine and the semgrep false green a third time, and it was not
    theoretical -- it was found by running `lab.py check` on an untouched checkout and
    getting 3/7. Every assertion whose case contracts the skill to WRITE the path it names
    starts with this. `did_not_write` is the deliberate exception: absence is its pass.
    """
    return None if ctx.content(path).strip() else f"{path} is absent or empty"


# --- existence and arity -----------------------------------------------------------------


def did_not_write(ctx: EvalContext, path: str) -> Result:
    """The highest-value class of assertion: a skill refusing to produce something.

    ALWAYS pair this with a positive assertion in the same case. On its own, a harness that
    never invoked the engine passes it — which is exactly the shape of the semgrep
    false-green trap this repo documents in .semgrep/README.md.
    """
    present = path in ctx.written or (ctx.worktree / path).is_file()
    return (not present, f"{path} {'was written' if present else 'was correctly not written'}")


def wrote_exactly(ctx: EvalContext, paths: list[str]) -> Result:
    expected, actual = set(paths), set(ctx.written)
    if expected == actual:
        return True, f"wrote exactly {sorted(expected)}"
    return False, f"expected {sorted(expected)}, wrote {sorted(actual)}"


def output_mentions(ctx: EvalContext, needle: str) -> Result:
    return (
        needle in ctx.output,
        f"output {'mentions' if needle in ctx.output else 'omits'} {needle!r}",
    )


def cost_under(ctx: EvalContext, usd: float) -> Result:
    if ctx.cost_usd is None:
        return True, "no cost reported by the engine"
    return ctx.cost_usd <= usd, f"cost ${ctx.cost_usd:.4f} against a ${usd:.2f} ceiling"


def max_lines(ctx: EvalContext, path: str, limit: int) -> Result:
    """At most `limit` lines -- and the file has to exist, which is the whole subtlety.

    An absent file has nought lines, and nought is under every limit. Written the obvious
    way, this assertion passes when the learner or the skill did nothing at all: the
    semgrep false green and the no-op engine, a third time, in three lines of code.
    """
    body = ctx.content(path)
    if not body.strip():
        return False, f"{path} is absent or empty"
    count = len(body.splitlines())
    return count <= limit, f"{count} line(s), limit {limit}"


def file_mentions(ctx: EvalContext, path: str, needles: list[str]) -> Result:
    """Every needle appears in the file. The must-contain twin of banned_tokens.

    Substring, not word-boundary: the needles are usually a `path:line` or a heading, and
    a word-boundary match does not do what you want next to a dot or a colon.
    """
    body = ctx.content(path)
    if not body.strip():
        return False, f"{path} is absent or empty"
    missing = sorted(n for n in needles if n not in body)
    return not missing, f"missing: {missing}" if missing else f"all {len(needles)} present"


# --- cardinality -------------------------------------------------------------------------


def max_questions(ctx: EvalContext, path: str, limit: int) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    count = len(ctx.question_blocks(path))
    return count <= limit, f"{count} question(s), limit {limit}"


def exactly_n_questions(ctx: EvalContext, path: str, count: int) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    found = len(ctx.question_blocks(path))
    return found == count, f"{found} question(s), expected exactly {count}"


def max_citations(ctx: EvalContext, path: str, limit: int) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    found = len(re.findall(r"[\w./-]+\.\w+:\d+", ctx.content(path)))
    return found <= limit, f"{found} citation(s), limit {limit}"


def findings_between(ctx: EvalContext, path: str, low: int, high: int) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    found = len(re.findall(r"^###\s+\d+\s+·", ctx.content(path), flags=re.M))
    return low <= found <= high, f"{found} finding(s), allowed {low}-{high}"


def at_most_one_blocking(ctx: EvalContext, path: str) -> Result:
    """0-3 findings and AT MOST one blocking. Requiring exactly one forces the skill to
    manufacture a blocking finding on clean code, which is how a review bot gets muted."""
    if reason := _absent(ctx, path):
        return False, reason
    found = len(re.findall(r"blocking:", ctx.content(path)))
    return found <= 1, f"{found} blocking marker(s), at most 1 allowed"


def min_entries(ctx: EvalContext, path: str, section: str, count: int) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    body = ctx.content(path)
    if section not in body:
        return False, f"{section} is absent"
    block = body.split(section, 1)[1].split("\n## ", 1)[0]
    found = len([ln for ln in block.splitlines() if ln.strip().startswith(("-", "*"))])
    return found >= count, f"{found} entr(ies) under {section}, need {count}"


# --- structure ---------------------------------------------------------------------------


def every_question_has(ctx: EvalContext, path: str, fields: list[str]) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    blocks = ctx.question_blocks(path)
    if not blocks:
        return False, "no question blocks found"
    missing = [f for f in fields for b in blocks if f not in b]
    return not missing, f"{len(blocks)} block(s); missing fields: {sorted(set(missing))}"


def every_answer_line_empty(ctx: EvalContext, path: str) -> Result:
    """A skill that answers its own questions produces a confident artifact built on guesses."""
    if reason := _absent(ctx, path):
        return False, reason
    filled = [ln for ln in ctx.content(path).splitlines() if re.match(r"\s*answer:\s*\S", ln)]
    return not filled, f"{len(filled)} answer line(s) already filled"


def contains_sentinel(ctx: EvalContext, path: str, text: str = SENTINEL_STOPPED) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    present = text in ctx.content(path)
    return present, f"stop sentinel {'present' if present else 'MISSING'}"


def sections_in_order(ctx: EvalContext, path: str, sections: list[str]) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    body = ctx.content(path)
    positions = [body.find(s) for s in sections]
    missing = [s for s, p in zip(sections, positions, strict=True) if p == -1]
    if missing:
        return False, f"missing section(s): {missing}"
    return positions == sorted(
        positions
    ), f"order {'holds' if positions == sorted(positions) else 'is wrong'}"


def no_section_empty(ctx: EvalContext, path: str, sections: list[str]) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    body = ctx.content(path)
    empty = []
    for section in sections:
        if section not in body:
            continue
        block = body.split(section, 1)[1].split("\n## ", 1)[0]
        if not block.strip():
            empty.append(section)
    return not empty, f"empty section(s): {empty}"


def footer_verbatim(ctx: EvalContext, path: str, text: str) -> Result:
    if reason := _absent(ctx, path):
        return False, reason
    present = text in ctx.content(path)
    return present, f"fixed footer {'present verbatim' if present else 'MISSING or reworded'}"


# --- content the contract calls verbatim -------------------------------------------------


def citations_resolve(ctx: EvalContext, path: str) -> Result:
    """A deterministic hallucination check. It does not judge whether the citation is apt."""
    if reason := _absent(ctx, path):
        return False, reason
    bad = []
    for cited, line in re.findall(r"([\w./-]+\.\w+):(\d+)", ctx.content(path)):
        target = ctx.worktree / cited
        if not target.is_file():
            bad.append(f"{cited} (no such file)")
        elif len(target.read_text(encoding="utf-8", errors="replace").splitlines()) < int(line):
            bad.append(f"{cited}:{line} (file is shorter)")
    return not bad, f"unresolvable: {bad}" if bad else "every citation resolves"


def strings_carried_forward(ctx: EvalContext, source: str, target: str, pattern: str) -> Result:
    """Every match of `pattern` in `source` must appear verbatim in `target`.

    Covers two contract clauses at once: touchpoints copied "unchanged", and acceptance
    criteria "quoted verbatim". Verbatim is the one prose property that IS deterministic.
    """
    wanted = set(re.findall(pattern, ctx.content(source)))
    if not wanted:
        return False, f"pattern found nothing in {source}"
    body = ctx.content(target)
    missing = sorted(w for w in wanted if w not in body)
    return (
        not missing,
        f"missing from {target}: {missing}" if missing else f"all {len(wanted)} carried forward",
    )


def banned_tokens(ctx: EvalContext, path: str, tokens: list[str], section: str = "") -> Result:
    """No banned token appears. The file has to exist -- see max_lines for why.

    "Nothing forbidden is in this file" is trivially true of a file that was never written,
    so on its own this assertion passes when the skill did nothing. Every case here names a
    path the skill is contracted to produce, which makes absence a failure rather than a
    vacuous pass. A missing SECTION inside a present file is a different thing and is still
    allowed: not every contract requires every section.
    """
    body = ctx.content(path)
    if not body.strip():
        return False, f"{path} is absent or empty"
    if section:
        if section not in body:
            return True, f"{section} absent, nothing to check"
        body = body.split(section, 1)[1].split("\n## ", 1)[0]
    found = sorted(t for t in tokens if re.search(rf"\b{re.escape(t)}\b", body, flags=re.I))
    return not found, f"banned token(s) present: {found}" if found else "no banned tokens"


REGISTRY: dict[str, Callable[..., Result]] = {
    "at_most_one_blocking": at_most_one_blocking,
    "banned_tokens": banned_tokens,
    "citations_resolve": citations_resolve,
    "contains_sentinel": contains_sentinel,
    "cost_under": cost_under,
    "did_not_write": did_not_write,
    "every_answer_line_empty": every_answer_line_empty,
    "every_question_has": every_question_has,
    "exactly_n_questions": exactly_n_questions,
    "file_mentions": file_mentions,
    "findings_between": findings_between,
    "footer_verbatim": footer_verbatim,
    "max_citations": max_citations,
    "max_lines": max_lines,
    "max_questions": max_questions,
    "min_entries": min_entries,
    "no_section_empty": no_section_empty,
    "output_mentions": output_mentions,
    "sections_in_order": sections_in_order,
    "strings_carried_forward": strings_carried_forward,
    "wrote_exactly": wrote_exactly,
}

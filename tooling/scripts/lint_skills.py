#!/usr/bin/env python3
"""Enforce the rules chapter 1.1 teaches, on the files that teach them.

The lecture claims four things make a skill portable: no vendor names in the body, no
absolute paths, declared inputs, and a fixed output shape. Claims in a slide rot. This
script turns them into a build failure, which is the lecture's own thesis applied to the
lecture's own artifacts.

The highest-value check is the chain check (7): every path a skill declares as an input
must be produced as an output by another skill. It is the only automated proof that the
skills compose rather than merely coexist, and it is what fails when someone renames
`answers.md` in one file and not the other.

Check 11 is the newest and the one most likely to rot: a skill's capability contract lives
in two files' worth of vocabulary — prose in the body, an allowlist in the frontmatter — and
nothing but this comparison stops them drifting apart.

Usage:
    python3 tooling/scripts/lint_skills.py                # lint the skills
    python3 tooling/scripts/lint_skills.py --check-agents # also compare the read-only agent twins
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
AGENT_FILES = (
    REPO_ROOT / ".github" / "agents" / "read-only-explorer.agent.md",
    REPO_ROOT / ".claude" / "agents" / "read-only-explorer.md",
)

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Purpose",
    "## When to use / when not to",
    "## Inputs required",
    "## Procedure",
    "## Output contract",
    "## Stop conditions",
    "## Anti-patterns",
)

DESCRIPTION_MAX_CHARS = 320
BODY_MAX_LINES = 200

# A skill body that names one host stops being portable, and portability is the entire
# point for a team split across three assistants. Bare tool names used as verbs are the
# subtle half of this: "use Grep to search" reads as neutral and is not.
VENDOR_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bClaude\b", "names a host (Claude)"),
    (r"\bCursor\b", "names a host (Cursor)"),
    (r"\bCopilot\b", "names a host (Copilot)"),
    (r"\bCodex\b", "names a host (Codex)"),
    (r"\bVS ?Code\b", "names a host (VS Code)"),
    (r"\bWindsurf\b", "names a host (Windsurf)"),
    (r"@workspace", "uses a host-specific chat directive"),
    (r"\bComposer\b", "names a host feature (Composer)"),
    (r"`(Read|Grep|Glob|Edit|Write|Bash|codebase_search)`", "names a host tool as a verb"),
)

ABSOLUTE_PATH_PATTERNS: tuple[str, ...] = (r"/Users/", r"/home/", r"[A-Z]:\\\\", r"~/")

# Paths a skill may declare as an input without another skill producing them. Deliberately
# narrow: listing "<TICKET>" here would exempt every parameterised path and silently defeat
# the chain check, which is the whole point of this script.
EXTERNAL_INPUTS: tuple[str, ...] = ("the diff", "the ticket")

# Check 11's vocabulary. The same four tokens check_agents uses, for the same reason: a shell
# can write ('>', tee, sed -i, python -c), so "no shell" and "no commands" are one claim.
SHELL_TOKENS: tuple[str, ...] = ("Bash", "runCommands", "runInTerminal", "shell")
CAPABILITY_MARKER = "**Capabilities.**"

PATH_RE = re.compile(r"`([^`\s]*?<TICKET>[^`\s]*?|[\w./-]+/[\w./-]+\.\w+)`")


@dataclass
class Skill:
    """One canonical SKILL.md, parsed into the parts the checks need."""

    name: str
    path: Path
    frontmatter: dict[str, str]
    body: str
    sections: dict[str, str]

    def declared(self, heading: str) -> set[str]:
        """Repo-relative paths mentioned under one heading, ticket ids normalised."""
        text = self.sections.get(heading, "")
        found: set[str] = set()
        for match in PATH_RE.findall(text):
            found.add(re.sub(r"PROJ-\d+", "<TICKET>", match))
        return found


@dataclass
class Report:
    failures: list[str] = field(default_factory=list)
    checked: int = 0

    def fail(self, where: str, message: str) -> None:
        self.failures.append(f"{where}: {message}")


def parse_frontmatter(text: str, path: Path, report: Report) -> tuple[dict[str, str], str]:
    """Split YAML frontmatter from the body without taking a YAML dependency.

    Only flat `key: value` pairs and `key: >` folded blocks are supported, which is all a
    skill's frontmatter is allowed to contain.
    """
    if not text.startswith("---\n"):
        report.fail(str(path.relative_to(REPO_ROOT)), "no YAML frontmatter at the top of the file")
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        report.fail(str(path.relative_to(REPO_ROOT)), "frontmatter is not closed with ---")
        return {}, text
    raw, body = text[4:end], text[end + 5 :]

    data: dict[str, str] = {}
    key: str | None = None
    for line in raw.splitlines():
        match = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if match:
            key = match.group(1)
            data[key] = match.group(2).strip().lstrip(">").strip()
        elif key and line.strip():
            data[key] = (data[key] + " " + line.strip()).strip()
    return data, body


def split_sections(body: str) -> dict[str, str]:
    """Map each `## Heading` to the text beneath it, up to the next `## `.

    Fenced blocks are skipped when looking for headings. A skill whose `## Output contract`
    shows the markdown it emits will contain `## ` inside a fence, and treating that as a
    section boundary silently truncates the section — which made the chain check report a
    broken chain for a skill whose chain was fine. Found by the harvest skill, which is the
    first one whose output is itself a document with headings.
    """
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            if current is not None:
                buffer.append(line)
            continue
        if line.startswith("## ") and not in_fence:
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = line.strip()
            buffer = []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def load_skills(report: Report) -> list[Skill]:
    skills: list[Skill] = []
    if not SKILLS_DIR.is_dir():
        report.fail(".github/skills", "directory does not exist")
        return skills
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        name = skill_md.parent.name
        if name.startswith("_"):
            continue
        text = skill_md.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text, skill_md, report)
        skills.append(
            Skill(
                name=name,
                path=skill_md,
                frontmatter=frontmatter,
                body=body,
                sections=split_sections(body),
            )
        )
    return skills


def _check_frontmatter(skill: Skill, where: str, report: Report) -> None:
    """Check 1 — the only part of a skill that is always in context."""
    if skill.frontmatter.get("name") != skill.name:
        report.fail(
            where,
            f"frontmatter name {skill.frontmatter.get('name')!r} "
            f"does not match directory {skill.name!r}",
        )
    description = skill.frontmatter.get("description", "")
    if not description:
        report.fail(where, "frontmatter has no description; it is what loads at startup")
    elif len(description) > DESCRIPTION_MAX_CHARS:
        report.fail(
            where,
            f"description is {len(description)} chars, over the {DESCRIPTION_MAX_CHARS} budget "
            "(it is always in context)",
        )


def _check_structure(skill: Skill, where: str, report: Report) -> None:
    """Checks 2 and 3 — all seven headings, in order, none empty."""
    present = [h for h in REQUIRED_HEADINGS if h in skill.sections]
    for heading in REQUIRED_HEADINGS:
        if heading not in skill.sections:
            report.fail(where, f"missing section {heading!r}")
    order = [skill.body.find(h) for h in present]
    if order != sorted(order):
        report.fail(where, "sections are out of order; keep the template's order")
    for heading in present:
        if not skill.sections[heading]:
            report.fail(where, f"section {heading!r} is empty")


def _check_portability(skill: Skill, where: str, report: Report) -> None:
    """Checks 4, 5 and 6 — the three rules that make a body reusable in any host."""
    # The description is checked too: it is always in context, so a host name there is at
    # least as visible as one in the body.
    scanned = {"body": skill.body, "description": skill.frontmatter.get("description", "")}
    for label, text in scanned.items():
        for pattern, why in VENDOR_PATTERNS:
            if re.search(pattern, text):
                report.fail(where, f"{label} {why}; say the capability instead")
    for pattern in ABSOLUTE_PATH_PATTERNS:
        if re.search(pattern, skill.body):
            report.fail(where, f"body contains an absolute path matching {pattern!r}")
    if not skill.declared("## Output contract"):
        report.fail(where, "'## Output contract' names no repo-relative path")


def _check_paste_first(skill: Skill, where: str, report: Report) -> None:
    """Checks 8 and 9 — the body must work pasted into a chat with nothing installed."""
    lines = len(skill.body.strip().splitlines())
    if lines > BODY_MAX_LINES:
        report.fail(
            where,
            f"body is {lines} lines, over the {BODY_MAX_LINES}-line paste-first budget",
        )
    if "references/" in skill.sections.get("## Procedure", ""):
        report.fail(
            where,
            "'## Procedure' reaches a references/ file; the body must work pasted into a chat "
            "with nothing installed",
        )


def _check_capabilities(skill: Skill, where: str, report: Report) -> None:
    """Check 11 — the prose contract and the host's allowlist have to agree.

    Decision 2 of the 24 September set put the capability claim in the body, in host-neutral
    prose, and the enforceable allowlist in frontmatter where the host-name ban does not
    reach. Two halves of one claim in two places is a divergence waiting to happen, and this
    repo has the scar: `demos.md` and `deck-divergences.md` gave opposite statuses for five
    demos for a week. So the halves get compared.
    """
    allowlist = skill.frontmatter.get("allowed-tools", "")
    if not allowlist:
        report.fail(
            where,
            "frontmatter has no 'allowed-tools'; an allowlist is only an allowlist when "
            "present, and without it the skill inherits every tool the host has",
        )

    prose = skill.sections.get("## Inputs required", "")
    if CAPABILITY_MARKER not in prose:
        report.fail(
            where,
            f"'## Inputs required' has no {CAPABILITY_MARKER} line; the allowlist is one "
            "host's spelling and the prose is the contract, so the contract cannot be absent",
        )
        return

    claims_no_commands = "runs no commands" in prose
    has_shell = any(token.lower() in allowlist.lower() for token in SHELL_TOKENS)
    if claims_no_commands and has_shell:
        report.fail(
            where,
            f"body says 'runs no commands' but 'allowed-tools' grants a shell ({allowlist!r}); "
            "a shell can write, so the two halves disagree",
        )
    if not claims_no_commands and not has_shell:
        report.fail(
            where,
            "body does not say 'runs no commands' and 'allowed-tools' grants no shell; say "
            "which it is, because a reader cannot tell an omission from a decision",
        )


def check_skill(skill: Skill, report: Report) -> None:
    where = str(skill.path.relative_to(REPO_ROOT))
    _check_frontmatter(skill, where, report)
    _check_structure(skill, where, report)
    _check_portability(skill, where, report)
    _check_paste_first(skill, where, report)
    _check_capabilities(skill, where, report)
    report.checked += 1


def check_chain(skills: list[Skill], report: Report) -> None:
    """Check 7 — every declared input is some skill's declared output, or external."""
    produced: set[str] = set()
    for skill in skills:
        produced |= skill.declared("## Output contract")

    for skill in skills:
        where = str(skill.path.relative_to(REPO_ROOT))
        for path in sorted(skill.declared("## Inputs required")):
            if path in produced:
                continue
            if any(token in path for token in EXTERNAL_INPUTS):
                continue
            report.fail(
                where,
                f"declares input {path!r}, which no skill produces as an output "
                "(the chain is broken, or the path is misspelled)",
            )


def check_agents(report: Report) -> None:
    """Check 10 — the twins say the same thing, and neither is handed a shell."""
    bodies: list[str] = []
    for path in AGENT_FILES:
        if not path.is_file():
            report.fail(str(path.relative_to(REPO_ROOT)), "agent file is missing")
            continue
        text = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text, path, report)

        tools = frontmatter.get("tools", "")
        if not tools:
            report.fail(
                str(path.relative_to(REPO_ROOT)),
                "no 'tools:' key — the allowlist is only an allowlist when present, and "
                "without it the agent inherits everything",
            )
        for shell in ("Bash", "runCommands", "runInTerminal", "shell"):
            if shell.lower() in tools.lower():
                report.fail(
                    str(path.relative_to(REPO_ROOT)),
                    f"allowlists {shell!r}; a shell can write ('>', tee, sed -i, python -c) "
                    "so it is not read-only",
                )
        # Compare instructions only: the frontmatter differs by design, the body must not.
        bodies.append(re.sub(r"<!--.*?-->", "", body, flags=re.S).strip())

    if len(bodies) == 2 and bodies[0] != bodies[1]:
        report.fail(
            "agents",
            "the two read-only-explorer files have drifted; their instructions must match "
            "(only the frontmatter may differ)",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-agents",
        action="store_true",
        help="also compare the two read-only-explorer files",
    )
    args = parser.parse_args()

    report = Report()
    skills = load_skills(report)
    for skill in skills:
        check_skill(skill, report)
    check_chain(skills, report)
    if args.check_agents:
        check_agents(report)

    for failure in report.failures:
        print(f"FAIL {failure}")

    if report.failures:
        print(f"\n{len(report.failures)} problem(s) across {report.checked} skill(s).")
        return 1
    print(f"OK — {report.checked} skill(s) pass all checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

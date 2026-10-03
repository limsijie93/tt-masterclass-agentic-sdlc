"""Every link, anchor and written path in the repository points at something that exists.

LEARN.md is a walkthrough made almost entirely of links. A broken one sends a learner who just
watched the lecture to a 404, which is the worst possible first impression of a repo whose
thesis is that everything in it is real. This is cheap, deterministic, and never flakes.

The written-path check exists because the links were not where the rot was. After three
reorganisations every link resolved, and six plain-text mentions still named files where they
used to be. A path in prose is a claim like any other.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from conftest import SOLVED

REPO = Path(__file__).resolve().parents[2]


def _git(*args: str, stdin: str | None = None) -> list[str]:
    result = subprocess.run(
        ["git", *args], cwd=REPO, input=stdin, capture_output=True, text=True, check=False
    )
    return result.stdout.split("\n")


TRACKED = [f for f in _git("ls-files") if f]
# Every tracked doc. Tracked only, so a learner's own gitignored lab work (pruned.md, report.md)
# never fails the check; teach/ simply matches nothing in the learner copy.
# teach/start/ holds files that resolve at their published paths; the start copy checks them.
DOCS = tuple(f for f in TRACKED if f.endswith(".md") and not f.startswith("teach/start/"))

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
FENCE = re.compile(r"```.*?```", re.DOTALL)


def _relative_links(doc: str) -> list[str]:
    body = (REPO / doc).read_text(encoding="utf-8")
    return [
        target
        for target in LINK.findall(body)
        if not target.startswith(("http://", "https://", "mailto:"))
    ]


def _anchors(doc: Path) -> set[str]:
    """GitHub's heading ids: lowercase, formatting and punctuation dropped, spaces to hyphens,
    and -1, -2 appended to repeats."""
    seen: dict[str, int] = {}
    anchors = set()
    for heading in HEADING.findall(FENCE.sub("", doc.read_text(encoding="utf-8"))):
        slug = re.sub(r"[^\w\- ]", "", re.sub(r"[`*]", "", heading).strip().lower())
        slug = slug.replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def test_every_relative_link_resolves() -> None:
    broken = []
    for doc in DOCS:
        base = (REPO / doc).parent
        for target in _relative_links(doc):
            path = target.split("#", 1)[0]
            if path and not (base / path).exists():
                broken.append(f"{doc} -> {target}")
    assert not broken, f"broken links: {broken}"


def test_every_anchor_names_a_heading() -> None:
    """A link to a heading that was renamed still opens the page, at the top. Nothing else
    notices."""
    broken = []
    for doc in DOCS:
        base = (REPO / doc).parent
        for target in _relative_links(doc):
            path, _, anchor = target.partition("#")
            destination = (base / path) if path else REPO / doc
            if anchor and destination.suffix == ".md" and destination.is_file():
                if anchor not in _anchors(destination):
                    broken.append(f"{doc} -> {target}")
    assert not broken, f"anchors that name no heading: {broken}"


# A repo path written as text, rooted at one of the folders that hold the course. A glob or
# placeholder ends the claim at the folder before its first `*`, `<` or `{`.
WRITTEN_PATH = re.compile(r"(?<![\w./-])((?:course|teach|tooling)/[A-Za-z0-9_./-]*)")
# Fixtures whose paths are made up on purpose, and the copy-me fills, whose paths describe a
# learner's own repository rather than this one, and the start overlay (see DOCS).
NOT_SCANNED = re.compile(
    r"^(tooling/tests/.*\.py|course/templates/(python|typescript)/.*|teach/start/.*)$"
)


SOLUTION_ONLY = (
    "course/tickets/PROJ-142/",
    "course/tickets/PROJ-207/",
    "course/labs/06-implement-one-criterion",
)


def test_every_written_path_exists() -> None:
    claims: dict[str, set[str]] = {}
    for name in TRACKED:
        path = REPO / name
        if NOT_SCANNED.match(name) or path.is_symlink() or not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in WRITTEN_PATH.finditer(body):
            written = match.group(1).rstrip(".")
            if body[match.end() : match.end() + 1] in ("*", "<", "{"):
                written = written.rsplit("/", 1)[0]  # guard_*.py: only the folder is a claim
            if not (REPO / written).exists():
                claims.setdefault(written, set()).add(name)
    # A learner's own lab output is named in the briefs and gitignored; it is allowed to be absent.
    ignored = set(_git("check-ignore", "--stdin", stdin="\n".join(claims)))
    # On the learner main branch the worked answers are not there yet: docs describe them as
    # being on the solution branch, and that is where the path resolves.
    on_solution = () if SOLVED else SOLUTION_ONLY
    missing = {
        p: sorted(where)
        for p, where in claims.items()
        if p not in ignored and not p.startswith(on_solution)
    }
    assert not missing, f"written paths that do not exist: {missing}"


def test_the_learner_path_exists_and_is_routed_to() -> None:
    """A second entry point only works if the first one points at it."""
    assert (REPO / "LEARN.md").is_file()
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert (
        "LEARN.md" in readme.split("\n## ", 1)[0]
    ), "README must route to LEARN.md above the first section, or nobody finds it"


def test_the_learner_path_covers_every_file_in_the_worked_chain() -> None:
    """The walkthrough's 'what to notice' table must not silently fall behind the chain."""
    learn = (REPO / "LEARN.md").read_text(encoding="utf-8")
    chain = sorted(p.name for p in (REPO / "course" / "tickets" / "PROJ-142").glob("*.md"))
    missing = [
        name for name in chain if name not in {"README.md", "AGENTS.md"} and name not in learn
    ]
    assert not missing, f"LEARN.md does not mention: {missing}"

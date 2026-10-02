"""Every relative link in the reader-facing documents resolves.

LEARN.md is a walkthrough made almost entirely of links. A broken one sends a learner who just
watched the lecture to a 404, which is the worst possible first impression of a repo whose
thesis is that everything in it is real. This is cheap, deterministic, and never flakes.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# RECORDING.md is instructor-only; the learner copy has no such file to check.
DOCS = tuple(
    doc
    for doc in (
        "README.md",
        "RECORDING.md",
        "TEACH.md",
        "docs/demos.md",
        "docs/storyboard.md",
        "LEARN.md",
        "example/PROJ-142/README.md",
        "templates/README.md",
        "examples/README.md",
        "evals/README.md",
        "labs/README.md",
        ".devcontainer/README.md",
        ".semgrep/README.md",
    )
    if (REPO / doc).exists()
)

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _relative_links(doc: str) -> list[str]:
    body = (REPO / doc).read_text(encoding="utf-8")
    return [
        target
        for target in LINK.findall(body)
        if not target.startswith(("http://", "https://", "#", "mailto:"))
    ]


def test_every_relative_link_resolves() -> None:
    broken = []
    for doc in DOCS:
        base = (REPO / doc).parent
        for target in _relative_links(doc):
            path = target.split("#", 1)[0]
            if not path:
                continue
            if not (base / path).exists():
                broken.append(f"{doc} -> {target}")
    assert not broken, f"broken links: {broken}"


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
    chain = sorted(p.name for p in (REPO / "example" / "PROJ-142").glob("*.md"))
    missing = [
        name for name in chain if name not in {"README.md", "AGENTS.md"} and name not in learn
    ]
    assert not missing, f"LEARN.md does not mention: {missing}"

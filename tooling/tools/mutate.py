#!/usr/bin/env python3
"""A diff-scoped mutation gate for `tooling/myapp/`, baselined.

WHY THIS EXISTS

`course/tickets/PROJ-142/09-tests-that-lie.md` ends with a human noticing that a test asserts on its
own mock. That is tier 2 — a person read carefully — in a repository whose argument is that a
standard a machine cannot check is a preference. Test quality was therefore a preference. This
is the sensor that moves it to tier 1.

WHY NOT mutmut

`course/labs/03-the-test-that-lies/lab.md` says the production version of that lab's hand-rolled
`mutate.sh` is mutmut, and for a team adopting mutation testing generally that is still the
right advice. It is not the right tool for this gate, for two reasons that are about the gate
rather than about mutmut: the decision recorded on 24 September was `myapp/` only, diff-scoped
and baselined first, and mutmut gives neither diff scoping nor a baseline without wrapping it
in about as much code as is below. Adding a dependency to then work around it is worse than
100 lines of `ast`, which is in the standard library and cannot drift from a pinned version.

The trade: five operators, not mutmut's catalogue. This catches boundary, comparison, boolean
and constant errors. It does not catch everything, and a gate that claimed to would be the
aspirational content this repo warns about. What it has to be is fast, deterministic and
never flaky, because a flaky gate destroys trust in about a week.

WHY BASELINED

Turning this on repo-wide on day one produces a list of surviving mutants nobody asked for, and
the list gets ignored, and then the gate gets removed. Same failure as any checker switched on
against a codebase that predates it. `myapp/.mutation-baseline.txt` records the survivors that
existed when the gate landed; the build fails on a NEW survivor only. Deleting a line from the
baseline is how you pay one down, and nothing stops you adding to it — a baseline you cannot
add to is a baseline people route around by not writing the test at all.

Usage:
    python3 tooling/tools/mutate.py                  # everything under myapp/, against the baseline
    python3 tooling/tools/mutate.py --since origin/main  # only files the branch touched
    python3 tooling/tools/mutate.py --write-baseline     # record current survivors as accepted
"""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGET = REPO / "tooling" / "myapp"
BASELINE = TARGET / ".mutation-baseline.txt"
# The suite that has to kill the mutants. Narrow on purpose: this gate is about the tests that
# cover myapp/, and running the whole suite would time the repo's own meta-tests over and over.
SUITE = ("tooling/tests/test_exports.py",)

COMPARE_SWAPS: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
}


@dataclass(frozen=True)
class Mutant:
    """One mutation, identified by where it is and what it did."""

    path: Path
    line: int
    col: int
    what: str
    source: str

    @property
    def ident(self) -> str:
        # The column is in the identity, not decoration. `chunk_size: int | None = None` puts
        # two mutable constants on one line, and a baseline keyed on line alone would accept a
        # new survivor because an unrelated one at the same line was already accepted.
        try:
            where = self.path.relative_to(REPO)
        except ValueError:
            # A path outside the repository — a temporary file under test. Baselines only
            # ever hold repo-relative paths, so this branch never reaches one; it exists so
            # that naming a mutant cannot raise.
            where = self.path
        return f"{where}:{self.line}:{self.col} {self.what}"


def _annotations(tree: ast.AST) -> set[int]:
    """Nodes inside a type annotation, which this file does not mutate.

    `myapp/` uses `from __future__ import annotations`, so annotations are strings at runtime
    and mutating one changes nothing a test could ever catch. Every such mutant survives, and
    a gate whose output is mostly guaranteed survivors teaches people to skim it.
    """
    skip: set[int] = set()
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.AnnAssign | ast.arg):
            targets.append(node.annotation)
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            targets.append(node.returns)
        for annotation in targets:
            if annotation is not None:
                skip.update(id(sub) for sub in ast.walk(annotation))
    return skip


def _mutate(node: ast.AST) -> str | None:
    """Apply one operator to one node, in place. Returns what it did, or None if it did not.

    Five operators. Boundary and comparison errors are what the export code actually gets
    wrong — `should_queue` turns on a single `>` — and the None operator is here because
    `chunk_size=None` meaning unbounded is the footgun the worked review is built around.
    """
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        op = type(node.ops[0])
        if op in COMPARE_SWAPS:
            new = COMPARE_SWAPS[op]
            node.ops = [new()]
            return f"compare {op.__name__} -> {new.__name__}"
        return None
    if isinstance(node, ast.BoolOp):
        new_op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        was = type(node.op).__name__
        node.op = new_op
        return f"boolop {was} -> {type(new_op).__name__}"
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            was_bool = node.value
            node.value = not node.value
            return f"constant {was_bool} -> {not was_bool}"
        if isinstance(node.value, int):
            was_int = node.value
            node.value = was_int + 1
            return f"constant {was_int} -> {was_int + 1}"
        if node.value is None:
            node.value = 0
            return "constant None -> 0"
    return None


def _mutants(path: Path) -> list[Mutant]:
    """Every mutation of one file, as rewritten source."""
    original = path.read_text(encoding="utf-8")
    found: list[Mutant] = []

    # Re-parse per mutation: mutating a shared tree in place would compound the edits, and a
    # mutant carrying two changes tells you nothing about which one the tests missed.
    for index in range(len(list(ast.walk(ast.parse(original))))):
        tree = ast.parse(original)
        nodes = list(ast.walk(tree))
        if index >= len(nodes):
            break
        node = nodes[index]
        if id(node) in _annotations(tree):
            continue
        line = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0)
        what = _mutate(node)
        if what is None:
            continue
        found.append(
            Mutant(
                path=path,
                line=line,
                col=col,
                what=what,
                source=ast.unparse(ast.fix_missing_locations(tree)),
            )
        )
    return found


def _tests_pass() -> bool:
    """Run the suite against whatever is currently on disk.

    PYTHONDONTWRITEBYTECODE is not tidiness. CPython validates a cached `.pyc` against the
    source's size and its mtime IN WHOLE SECONDS, and this loop rewrites the same path dozens
    of times per second with sources that are frequently the same length — `>` to `>=` and
    `None` to `0` both round-trip through ast.unparse at sizes that collide. When the cache
    is believed, the interpreter runs the PREVIOUS mutant, and the verdict lands on the wrong
    line. Caught by running the gate three times on an unchanged tree and getting 35, 36 and
    37 survivors. A gate that answers differently each run is worse than no gate, so this is
    the one line that makes the rest of the file trustworthy.
    """
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-qx", "--no-header", "-p", "no:cacheprovider", *SUITE],
        cwd=REPO,
        capture_output=True,
        env=env,
    )
    return result.returncode == 0


def _survivors(paths: list[Path]) -> list[Mutant]:
    """A mutant survives when the suite still passes with it applied. That is the finding:
    the tests do not depend on the line that changed."""
    alive: list[Mutant] = []
    for path in paths:
        original = path.read_text(encoding="utf-8")
        try:
            for mutant in _mutants(path):
                path.write_text(mutant.source, encoding="utf-8")
                if _tests_pass():
                    alive.append(mutant)
        finally:
            path.write_text(original, encoding="utf-8")
    return alive


def _changed_since(ref: str) -> list[Path]:
    result = subprocess.run(
        # Two-dot, not three: this compares the WORKING TREE against the ref, so the gate
        # sees the edit you have not committed yet. Three-dot would compare commit to commit
        # and a pre-commit hook would pass on the change it was installed to check.
        ["git", "diff", "--name-only", ref, "--", "tooling/myapp"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"mutate: cannot diff against {ref!r}; falling back to every file")
        return sorted(TARGET.rglob("*.py"))
    names = [n for n in result.stdout.split() if n.endswith(".py")]
    return [REPO / n for n in names if (REPO / n).is_file()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", help="only files changed since this ref (diff-scoped)")
    parser.add_argument(
        "--write-baseline", action="store_true", help="record current survivors as accepted"
    )
    args = parser.parse_args()

    paths = _changed_since(args.since) if args.since else sorted(TARGET.rglob("*.py"))
    paths = [p for p in paths if p.name != "__init__.py"]
    if not paths:
        print("mutate: no tooling/myapp/ files in scope — nothing to do")
        return 0

    alive = _survivors(paths)

    if args.write_baseline:
        BASELINE.write_text(
            "# Survivors accepted when the gate landed. Delete a line to pay one down.\n"
            + "".join(f"{m.ident}\n" for m in sorted(alive, key=lambda m: m.ident)),
            encoding="utf-8",
        )
        print(f"mutate: baseline written with {len(alive)} survivor(s)")
        return 0

    accepted = set()
    if BASELINE.is_file():
        accepted = {
            line.strip()
            for line in BASELINE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }

    new = [m for m in alive if m.ident not in accepted]
    scope = f"{len(paths)} file(s)"
    if not new:
        print(f"mutate: OK — {scope}, {len(alive)} survivor(s), all baselined")
        return 0

    print(f"mutate: {len(new)} NEW surviving mutant(s) in {scope}\n")
    for mutant in new:
        print(f"  {mutant.ident}")
    print(
        "\nA surviving mutant means the suite passes with that line changed, so nothing is "
        "testing it.\nWrite the assertion, or accept it with: python3 tooling/tools/mutate.py "
        "--write-baseline"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

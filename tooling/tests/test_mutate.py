"""Tests for tooling/tools/mutate.py — the operators and the identity, not the subprocess.

Running the real gate takes twenty-six seconds because it runs the suite once per mutant,
and a meta-test that slow would be the thing people skip. So this covers the parts that
decide WHAT gets mutated and HOW a survivor is named, which is where the bugs were:

  - mutating inside a type annotation, which with `from __future__ import annotations`
    produces a mutant that no test could ever kill;
  - an identity keyed on line alone, which let a new survivor hide behind a baselined one
    on the same line.

The third bug found while building it — stale `.pyc` reuse making the whole gate
non-deterministic — cannot be covered here, because it lives in the subprocess this file
deliberately does not run. It is pinned by a comment in `_tests_pass` instead, and by the
gate's own output being stable across runs in CI.
"""

from __future__ import annotations

import ast

from mutate import _annotations, _mutants, _mutate


def _apply(source: str) -> set[str]:
    """Every mutation of a snippet, as descriptions."""
    found = set()
    for index in range(len(list(ast.walk(ast.parse(source))))):
        tree = ast.parse(source)
        target = list(ast.walk(tree))[index]
        what = _mutate(target)
        if what:
            found.add(what)
    return found


def test_the_five_operators() -> None:
    assert "compare Gt -> GtE" in _apply("x = a > b")
    assert "boolop And -> Or" in _apply("x = a and b")
    assert "constant True -> False" in _apply("x = True")
    assert "constant 50000 -> 50001" in _apply("x = 50000")
    assert "constant None -> 0" in _apply("x = None")


def test_a_string_constant_is_not_mutated() -> None:
    """Docstrings are constants too, and mutating one changes no behaviour while producing a
    survivor on every function in the file."""
    assert _apply('x = "csv"') == set()


def test_annotations_are_skipped(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """tooling/myapp/ uses `from __future__ import annotations`, so an annotation is a string at
    runtime. Every mutant inside one survives, and a report that is mostly guaranteed
    survivors is a report people learn to skim."""
    source = (
        "from __future__ import annotations\n\n"
        "def f(chunk_size: int | None = None) -> bool:\n"
        "    return chunk_size is None\n"
    )
    tree = ast.parse(source)
    skipped = _annotations(tree)
    annotated = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value is None]
    # Three `None`s: one inside the annotation, one the default, one in the body's
    # `is None`. Only the annotation's is skipped — the other two are real behaviour.
    assert len(annotated) == 3
    assert sum(1 for n in annotated if id(n) in skipped) == 1


def test_the_default_is_still_mutated(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The other half of the previous test, and the operator that matters most here:
    `chunk_size=None` meaning unbounded is the footgun the worked review is built around."""
    path = tmp_path / "m.py"
    path.write_text(
        "from __future__ import annotations\n\n"
        "def f(chunk_size: int | None = None) -> bool:\n"
        "    return chunk_size is None\n"
    )
    assert any(m.what == "constant None -> 0" for m in _mutants(path))


def test_identities_on_one_line_are_distinct(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The bug a baseline keyed on `path:line` would have: two mutants on one line, one
    accepted, and the second silently accepted with it."""
    path = tmp_path / "m.py"
    path.write_text("def f(a=None, b=None):\n    return a, b\n")
    idents = [m.ident for m in _mutants(path) if m.what == "constant None -> 0"]
    assert len(idents) == 2
    assert len(set(idents)) == 2


def test_every_mutant_is_valid_python(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """A mutant that does not parse makes the suite fail for the wrong reason, and the gate
    would score it as killed — a false negative that looks like coverage."""
    path = tmp_path / "m.py"
    path.write_text(
        "def f(n=None):\n    if n is not None and n > 10:\n        return True\n    return False\n"
    )
    mutants = _mutants(path)
    assert mutants
    for mutant in mutants:
        ast.parse(mutant.source)


def test_a_mutant_actually_differs_from_the_original(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "m.py"
    original = "def f(a, b):\n    return a > b\n"
    path.write_text(original)
    for mutant in _mutants(path):
        assert mutant.source.strip() != original.strip()

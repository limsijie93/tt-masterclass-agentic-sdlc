"""Tests for tools/check_touchpoints.py.

These assert on the parser, not on a mock of the parser — see
course/tickets/PROJ-142/09-tests-that-lie.md for why that distinction is the whole point.
"""

from __future__ import annotations

from check_touchpoints import is_covered, parse_touchpoints

SPEC = """
# specs/PROJ-142.md

## Goal
Fast exports.

## Touchpoints

```
myapp/api/exports/views.py:41           entry point
myapp/service/exports/service.py:88     query builder
myapp/tasks/queue.py:12                 async path
tests/test_exports.py                   3 tests exist

(!) myapp/service/reports/legacy.py:210
    shares the same query - out of scope,
    but will break
```

## Allowed extras
- `docs/*.md`

## Done when
Exports finish.
"""


def test_parses_declared_paths_and_strips_line_numbers() -> None:
    declared, _ = parse_touchpoints(SPEC)
    assert "myapp/api/exports/views.py" in declared
    assert "myapp/service/exports/service.py" in declared
    assert "tests/test_exports.py" in declared


def test_parses_the_hazard_line_despite_its_marker() -> None:
    declared, _ = parse_touchpoints(SPEC)
    assert "myapp/service/reports/legacy.py" in declared


def test_ignores_paths_outside_the_touchpoints_section() -> None:
    declared, _ = parse_touchpoints(SPEC)
    assert not any("specs/" in d for d in declared)


def test_parses_allowed_extras() -> None:
    _, extras = parse_touchpoints(SPEC)
    assert extras == {"docs/*.md"}


def test_declared_file_is_covered() -> None:
    declared, extras = parse_touchpoints(SPEC)
    assert is_covered("myapp/api/exports/views.py", declared, extras)


def test_undeclared_file_is_not_covered() -> None:
    declared, extras = parse_touchpoints(SPEC)
    assert not is_covered("myapp/api/accounts/views.py", declared, extras)


def test_glob_in_allowed_extras_matches() -> None:
    declared, extras = parse_touchpoints(SPEC)
    assert is_covered("docs/exports.md", declared, extras)
    assert not is_covered("docs/nested/exports.md", declared, extras)


def test_empty_spec_declares_nothing() -> None:
    declared, extras = parse_touchpoints("# nothing here\n")
    assert declared == set()
    assert extras == set()

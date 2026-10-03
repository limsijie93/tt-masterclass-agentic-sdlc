"""Tests for tooling/tools/check_commands_sync.py.

Each test writes real files to a tmp_path and runs the real parser over them. Nothing is
mocked, so nothing here can pass if the parser is deleted — see
course/tickets/PROJ-142/09-tests-that-lie.md for why that is the bar.
"""

from __future__ import annotations

from pathlib import Path

from check_commands_sync import tool_of, tools_in_agents_md, tools_in_precommit

AGENTS = """# AGENTS.md

## Commands

```
ruff format .
ruff check . --fix
mypy myapp
lint-imports
pytest -q
```

## Architecture

Not a command: `pytest` mentioned in prose here must be ignored.
"""

PRECOMMIT = """
repos:
  - repo: local
    hooks:
      - id: ruff-format
        entry: ruff format
      - id: mypy
        entry: mypy --follow-imports=silent
      - id: lint-imports
        entry: lint-imports
      - id: pytest
        entry: pytest -q
      - id: trailing-whitespace
        entry: trailing-whitespace
  # - id: jscpd
  #   entry: jscpd
"""


def test_tool_of_reduces_a_command_to_its_tool() -> None:
    assert tool_of("ruff check . --fix") == "ruff"
    assert tool_of("lint-imports") == "lint-imports"
    assert tool_of("") is None


def test_tool_of_unwraps_a_python_script() -> None:
    assert tool_of("python3 tooling/tools/check_touchpoints.py --strict") == "check_touchpoints.py"


def test_reads_only_the_fenced_block_under_commands(tmp_path: Path) -> None:
    path = tmp_path / "AGENTS.md"
    path.write_text(AGENTS, encoding="utf-8")
    assert tools_in_agents_md(path) == {"ruff", "mypy", "lint-imports", "pytest"}


def test_prose_mentions_outside_the_fence_are_not_commands(tmp_path: Path) -> None:
    path = tmp_path / "AGENTS.md"
    path.write_text("# x\n\n## Architecture\n\nWe run `pytest` sometimes.\n", encoding="utf-8")
    assert tools_in_agents_md(path) == set()


def test_reads_entry_lines_and_skips_housekeeping(tmp_path: Path) -> None:
    path = tmp_path / "pc.yaml"
    path.write_text(PRECOMMIT, encoding="utf-8")
    assert tools_in_precommit(path) == {"ruff", "mypy", "lint-imports", "pytest"}


def test_commented_out_hooks_are_not_live(tmp_path: Path) -> None:
    path = tmp_path / "pc.yaml"
    path.write_text(PRECOMMIT, encoding="utf-8")
    assert "jscpd" not in tools_in_precommit(path)


def test_the_two_sides_agree_on_the_fixture(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text(AGENTS, encoding="utf-8")
    pc = tmp_path / "pc.yaml"
    pc.write_text(PRECOMMIT, encoding="utf-8")
    assert tools_in_agents_md(agents) == tools_in_precommit(pc)


def test_a_divergence_is_detected(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text(AGENTS.replace("lint-imports\n", ""), encoding="utf-8")
    pc = tmp_path / "pc.yaml"
    pc.write_text(PRECOMMIT, encoding="utf-8")
    assert tools_in_precommit(pc) - tools_in_agents_md(agents) == {"lint-imports"}


def test_a_missing_file_is_a_clear_error(tmp_path: Path) -> None:
    try:
        tools_in_agents_md(tmp_path / "nope.md")
    except SystemExit as exc:
        assert "not found" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected SystemExit")


def test_each_ecosystem_is_checked_on_its_own_terms(tmp_path: Path) -> None:
    """Comparing a Python tool list against a TypeScript gate would be meaningless."""
    from check_commands_sync import check_example

    py = tmp_path / "python"
    py.mkdir()
    (py / "AGENTS.md").write_text(AGENTS, encoding="utf-8")
    (py / "pre-commit-config.yaml").write_text(PRECOMMIT, encoding="utf-8")
    assert check_example(py) is True

    ts = tmp_path / "typescript"
    ts.mkdir()
    (ts / "AGENTS.md").write_text(
        "# x\n\n## Commands\n\n```\neslint --fix\ntsc --noEmit\n```\n", encoding="utf-8"
    )
    (ts / "pre-commit-config.yaml").write_text(
        "repos:\n  - repo: local\n    hooks:\n"
        "      - id: eslint\n        entry: eslint --fix\n"
        "      - id: tsc\n        entry: tsc --noEmit\n",
        encoding="utf-8",
    )
    assert check_example(ts) is True


def test_a_directory_missing_either_file_is_skipped_not_failed(tmp_path: Path) -> None:
    from check_commands_sync import check_example

    empty = tmp_path / "rust"
    empty.mkdir()
    assert check_example(empty) is True


def test_divergence_in_one_ecosystem_does_not_pass(tmp_path: Path) -> None:
    from check_commands_sync import check_example

    ts = tmp_path / "typescript"
    ts.mkdir()
    (ts / "AGENTS.md").write_text(
        "# x\n\n## Commands\n\n```\neslint --fix\n```\n", encoding="utf-8"
    )
    (ts / "pre-commit-config.yaml").write_text(
        "repos:\n  - repo: local\n    hooks:\n"
        "      - id: eslint\n        entry: eslint --fix\n"
        "      - id: tsc\n        entry: tsc --noEmit\n",
        encoding="utf-8",
    )
    assert check_example(ts) is False

"""Each skill zips the way the Claude Desktop / claude.ai upload expects: `<name>/SKILL.md`."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from lint_skills import Report, load_skills
from package_skills import package


def test_one_zip_per_skill_with_the_skill_directory_at_the_top() -> None:
    names = {skill.name for skill in load_skills(Report())}
    with tempfile.TemporaryDirectory() as tmp:
        archives = package(Path(tmp))
        assert {a.stem for a in archives} == names
        for archive in archives:
            members = zipfile.ZipFile(archive).namelist()
            assert f"{archive.stem}/SKILL.md" in members, archive.name
            assert "SKILL.md" not in members, f"{archive.name}: SKILL.md at the root is not a skill"
            assert all(m.startswith(f"{archive.stem}/") for m in members), archive.name

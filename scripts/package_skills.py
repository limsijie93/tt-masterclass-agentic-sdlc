#!/usr/bin/env python3
"""Zip each skill for upload to Claude Desktop or claude.ai (Customize > Skills).

One ZIP per skill, because that is the unit the upload takes. The archive's top level is the
skill's own directory, `<name>/SKILL.md`: a SKILL.md at the root of the ZIP is not recognised
as a skill. Name and description limits are already enforced by scripts/lint_skills.py, which
also supplies the skill list, so `_template` is skipped here for the same reason it is there.

Usage:
    python3 scripts/package_skills.py [OUT_DIR]     default: dist/skills/
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from lint_skills import REPO_ROOT, Report, load_skills

DEFAULT_OUT = REPO_ROOT / "dist" / "skills"
JUNK = {".DS_Store"}


def package(out_dir: Path) -> list[Path]:
    report = Report()
    skills = load_skills(report)
    if not skills:
        raise SystemExit("no skills found under .github/skills/")
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for skill in skills:
        root = skill.path.parent
        archive = out_dir / f"{skill.name}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in sorted(root.rglob("*")):
                if file.is_file() and file.name not in JUNK:
                    zf.write(file, f"{skill.name}/{file.relative_to(root).as_posix()}")
        written.append(archive)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("out_dir", nargs="?", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    for archive in package(args.out_dir):
        print(archive)
    return 0


if __name__ == "__main__":
    sys.exit(main())

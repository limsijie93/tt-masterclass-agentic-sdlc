#!/usr/bin/env bash
# LAB 03 — the delete-the-code test, mechanised.
#
#   ./mutate.sh blunt   test_yours.py
#   ./mutate.sh default test_yours.py
#
# Breaks exporter.py in one named way, runs the test file you name, restores the original,
# and exits with the test run's status. So:
#
#   exit 1  the test FAILED under mutation  -- good, it is actually testing something
#   exit 0  the test PASSED under mutation  -- it does not depend on the code it claims to
#
# This is `pytest` run against a deliberately broken subject, which is all mutation testing
# is. The production version of this idea is mutmut (Python) or Stryker (JS/TS); the
# fifteen lines below are here so you can read the whole thing.
set -u

mutation="${1:?usage: ./mutate.sh <blunt|default> <test file>}"
testfile="${2:?usage: ./mutate.sh <blunt|default> <test file>}"
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here" || exit 2

[ -f "$testfile" ] || { echo "no such test file: $testfile"; exit 2; }

cp exporter.py .exporter.orig
restore() { mv .exporter.orig exporter.py; }
trap restore EXIT

case "$mutation" in
  # Blunt: the function returns nothing at all. Any test that touches the real function
  # fails. A test that only touches a mock does not notice.
  blunt)
    python3 - <<'PY'
import pathlib
p = pathlib.Path("exporter.py")
body = p.read_text()
body = body.replace('    if not rows:\n        return []\n', '    return []\n', 1)
p.write_text(body)
PY
    ;;
  # Subtle: the documented "no limit" default silently becomes a limit of 1000. Every
  # small-input test still passes. Only a test that pins the DOCUMENTED behaviour fails.
  default)
    python3 - <<'PY'
import pathlib
p = pathlib.Path("exporter.py")
body = p.read_text()
body = body.replace('        return [list(rows)]', '        size = 1000', 1)
p.write_text(body)
PY
    ;;
  *) echo "unknown mutation: $mutation (blunt|default)"; exit 2 ;;
esac

python3 -m pytest -q "$testfile" >/dev/null 2>&1

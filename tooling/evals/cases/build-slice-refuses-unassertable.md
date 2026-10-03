---
skill: build-slice
stability: unmeasured
max_cost_usd: 0.70
negative_control: true
assertions:
  - name: did_not_write
    path: "specs/EVAL-107.drift.md"
  - name: output_mentions
    needle: "EVAL-107"
  - name: output_mentions
    needle: "2"
  - name: cost_under
    usd: 0.70
---

## Prompt

Use the build-slice skill to implement ticket EVAL-107.

The spec and the touchpoints file are both in the repository already.

## Setup

### specs/EVAL-107.md
```
# specs/EVAL-107.md   ·   PR #401

## Goal

The skill linter reports which of its checks was the slow one.

## Acceptance criteria

1. `tooling/scripts/lint_skills.py` prints a per-check duration in milliseconds when run with
   `--timings`, one line per check, in the order the checks ran.
2. The linter feels responsive on a large repository.

## Out of scope

- Making any check faster. This ticket measures; it does not optimise.
- Timing the `--check-agents` pass, which is one check and reports its own total.
- Any output format other than the existing plain text.

## Touchpoints

tooling/scripts/lint_skills.py:246         where each check is dispatched
tooling/scripts/lint_skills.py:90          the report object that collects output
tooling/tests/test_lint_skills.py:1        existing coverage

## Open questions

- Whether `--timings` should also be available through the pre-commit hook. Non-blocking.

## Done when

`python3 tooling/scripts/lint_skills.py --timings` prints a duration for every check.
```

### specs/EVAL-107.touchpoints.md
```
touchpoints - EVAL-107

tooling/scripts/lint_skills.py:246         where each check is dispatched
tooling/scripts/lint_skills.py:90          the report object that collects output
tooling/tests/test_lint_skills.py:1        existing coverage
```

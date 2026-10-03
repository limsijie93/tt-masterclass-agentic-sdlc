---
skill: spec-draft
stability: unmeasured
max_cost_usd: 0.60
negative_control: true
assertions:
  - name: did_not_write
    path: "specs/EVAL-102.md"
  - name: output_mentions
    needle: "EVAL-102"
  - name: output_mentions
    needle: "answer"
  - name: cost_under
    usd: 0.60
---

## Prompt

Use the spec-draft skill to draft the spec for ticket EVAL-102.

The ticket, the answers file and the touchpoints file are all in the repository already.

## Setup

### specs/EVAL-102.answers.md
```
spec-interrogate EVAL-102

1  Should the warning fire on the whole file or only on changed lines?
   blocks   whether this can run as a commit hook at all
   assumes  whole file
   answer:  Whole file. The budget is a property of the file, not of a diff.

2  What should happen when a skill is exactly at the budget?
   blocks   the comparison operator, and every borderline case
   assumes  at the budget is fine, over it is not
   answer:

3  Should the warning block, or only report?
   blocks   whether this is a gate or an annotation
   assumes  report only
   answer:  Report only, for now.

[ stopped - waiting for a human ]
```

### specs/EVAL-102.touchpoints.md
```
touchpoints - EVAL-102

tooling/scripts/lint_skills.py:45          the budget constant
tooling/scripts/lint_skills.py:217         where it is checked
.pre-commit-config.yaml:60         where the check is wired
```

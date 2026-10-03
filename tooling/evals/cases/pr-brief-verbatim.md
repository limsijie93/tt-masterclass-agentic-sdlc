---
skill: pr-brief
stability: unmeasured
assertions:
  - name: wrote_exactly
    paths: ["specs/EVAL-105.pr.md"]
  - name: sections_in_order
    path: "specs/EVAL-105.pr.md"
    sections: ["## Description", "## Acceptance criteria", "## Read order", "## Candidate untested paths"]
  - name: strings_carried_forward
    source: "specs/EVAL-105.md"
    target: "specs/EVAL-105.pr.md"
    pattern: "^\\\\d\\\\. \\\\*\\\\*(.+)\\\\*\\\\*$"
  - name: banned_tokens
    path: "specs/EVAL-105.pr.md"
    tokens: ["LGTM", "approve", "blocking", "severity"]
  - name: cost_under
    usd: 0.80
---

## Prompt

/pr-brief

Write the reviewer's brief for ticket EVAL-105. The spec and touchpoints are in the
repository, and the change is already committed on this branch.

## Setup

### specs/EVAL-105.md
```
# specs/EVAL-105.md · PR #401

## Goal
A broken host symlink is caught at commit time rather than discovered by the next reader.

## Acceptance criteria
1. **sync-skills --check exits 1 when a host link is missing**
2. **The failure names the command that repairs it**

## Out of scope
- Content equality between a copy and its canonical source — that is --copy's job.
- Creating missing host directories automatically.
- Any change to which hosts are synced.

## Touchpoints
tooling/scripts/sync-skills.sh:130
.pre-commit-config.yaml:61

## Open questions
None.

## Done when
A missing link fails the commit with a repair instruction.
```

### specs/EVAL-105.touchpoints.md
```
touchpoints - EVAL-105

tooling/scripts/sync-skills.sh:130            the --check branch
.pre-commit-config.yaml:61            where --check is wired
```

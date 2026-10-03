---
skill: spec-draft
stability: unmeasured
assertions:
  - name: wrote_exactly
    paths: ["specs/EVAL-104.md"]
  - name: sections_in_order
    path: "specs/EVAL-104.md"
    sections: ["## Goal", "## Acceptance criteria", "## Out of scope", "## Touchpoints", "## Open questions", "## Done when"]
  - name: no_section_empty
    path: "specs/EVAL-104.md"
    sections: ["## Goal", "## Acceptance criteria", "## Out of scope", "## Touchpoints", "## Done when"]
  - name: min_entries
    path: "specs/EVAL-104.md"
    section: "## Out of scope"
    count: 3
  - name: banned_tokens
    path: "specs/EVAL-104.md"
    section: "## Acceptance criteria"
    tokens: ["properly", "performant", "robust", "user-friendly"]
  - name: strings_carried_forward
    source: "specs/EVAL-104.touchpoints.md"
    target: "specs/EVAL-104.md"
    pattern: "\\\\(!\\\\) ([\\\\w./-]+\\\\.py)"
  - name: cost_under
    usd: 0.80
---

## Prompt

/spec-draft

Draft the spec for ticket EVAL-104. Its answers and touchpoints are already in the repository.

## Setup

### specs/EVAL-104.answers.md
```
spec-interrogate EVAL-104

1  Should the symlink check run on every commit, or only when a skill changes?
   blocks   whether it belongs at pre-commit or pre-push
   assumes  every commit
   answer:  Every commit. It is fast, and a broken symlink is confusing enough that
            finding out late is worse than the cost of checking.

2  What should happen when a host directory is missing entirely?
   blocks   whether a fresh clone fails or self-heals
   assumes  fail with an instruction
   answer:  Fail, and print the command that fixes it.

3  Should --check also verify the link target's contents?
   blocks   how much work the check does
   assumes  no, resolution only
   answer:  No. Resolution only. Content equality is the --copy mode's problem.
```

### specs/EVAL-104.touchpoints.md
```
touchpoints - EVAL-104

tooling/scripts/sync-skills.sh:130            the --check branch
tooling/scripts/sync-skills.sh:95             the link-target helper
.pre-commit-config.yaml:61            where --check is wired

(!) tooling/tools/check_commands_sync.py
    also walks a directory of expected files - out of scope,
    but shares the assumption that the tree is well formed
```

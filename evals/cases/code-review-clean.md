---
skill: code-review
stability: unmeasured
assertions:
  - name: wrote_exactly
    paths: ["reviews/EVAL-106.review.md"]
  - name: findings_between
    path: "reviews/EVAL-106.review.md"
    low: 0
    high: 3
  - name: at_most_one_blocking
    path: "reviews/EVAL-106.review.md"
  - name: footer_verbatim
    path: "reviews/EVAL-106.review.md"
    text: "Advisory — not a merge gate."
  - name: banned_tokens
    path: "reviews/EVAL-106.review.md"
    tokens: ["score", "grade", "LGTM", "approved"]
  - name: cost_under
    usd: 0.90
---

## Prompt

/code-review

Review the change for ticket EVAL-106 against its spec. The spec and touchpoints are in the
repository. Treat the current state of `tools/check_commands_sync.py` and its tests as the
change under review.

Note for the assertion set, not for you: this case exists to pin the OUTPUT SHAPE — nought to
three findings, at most one blocking, the footer verbatim, no scores. It does not assert that
any particular finding is correct, and it does not assert zero findings. Whether a genuinely
clean diff reliably produces zero is a question for the authoring runs, and the case will be
tightened to `zero_findings` only if it turns out to be 5/5 stable.

## Setup

### specs/EVAL-106.md
```
# specs/EVAL-106.md · PR #402

## Goal
Each ecosystem's context file and its hook config are checked against each other, so a
divergence fails the build rather than rotting quietly.

## Acceptance criteria
1. **Every directory under examples/ is checked on its own terms**
2. **A directory missing either file is skipped rather than failed**

## Out of scope
- Checking the root AGENTS.md, which needs its own ignore-list decision.
- Comparing tool sets across ecosystems, which would be meaningless.
- Any change to what the tools themselves enforce.

## Touchpoints
tools/check_commands_sync.py:1
tests/test_check_commands_sync.py:1

## Open questions
None.

## Done when
Two ecosystems pass independently and a divergence in one fails only that one.
```

### specs/EVAL-106.touchpoints.md
```
touchpoints - EVAL-106

tools/check_commands_sync.py:1        the checker
tests/test_check_commands_sync.py:1   its tests
```

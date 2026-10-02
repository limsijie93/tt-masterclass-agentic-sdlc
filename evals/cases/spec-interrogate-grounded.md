---
skill: spec-interrogate
stability: unmeasured
assertions:
  - name: wrote_exactly
    paths: ["specs/EVAL-101.answers.md", "specs/EVAL-101.touchpoints.md"]
  - name: max_questions
    path: "specs/EVAL-101.answers.md"
    limit: 5
  - name: every_question_has
    path: "specs/EVAL-101.answers.md"
    fields: ["blocks", "assumes"]
  - name: every_answer_line_empty
    path: "specs/EVAL-101.answers.md"
  - name: contains_sentinel
    path: "specs/EVAL-101.answers.md"
  - name: max_citations
    path: "specs/EVAL-101.touchpoints.md"
    limit: 10
  - name: citations_resolve
    path: "specs/EVAL-101.touchpoints.md"
  - name: cost_under
    usd: 0.80
---

## Prompt

/spec-interrogate

Ticket EVAL-101 — "The skill linter is slow on a big repo"

Someone reported that the pre-commit hook feels sluggish once a repository has a lot of
skills. Can we make the linter faster? It would also be good if it told you which check was
the slow one.

## Setup

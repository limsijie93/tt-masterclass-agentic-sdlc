---
skill: spec-interrogate
stability: unmeasured
assertions:
  - name: exactly_n_questions
    path: "specs/EVAL-103.answers.md"
    count: 1
  - name: contains_sentinel
    path: "specs/EVAL-103.answers.md"
  - name: output_mentions
    needle: "EVAL-103"
  - name: cost_under
    usd: 0.60
---

## Prompt

/spec-interrogate

Ticket EVAL-103 — "Billing webhooks are being retried forever"

The retry backoff on the billing webhook consumer looks wrong; a failed delivery seems to
retry indefinitely instead of giving up. Please fix.

## Setup

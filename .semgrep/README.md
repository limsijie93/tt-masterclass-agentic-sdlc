# .semgrep/ — custom rules, with tests

> **Not course material.** It lives at the root rather than in [`tooling/`](../tooling/) because
> the tools that read it expect this path. You don't edit it for a lab.


## The rules

**`api/no-orm-above-service`** (Python) — the executable half of one line in `AGENTS.md`: "no
data-layer calls above `myapp.service`". The import-linter contract catches this when it
crosses a module boundary as an *import*; this catches the other half, where the object
arrived by another route and the *call* is the violation. Two tools, one rule, neither
sufficient alone.

The rules a review produces arrive with the fix. Work the tickets, then compare with the
`solution` branch, where the two rules born from this repo's reviews live.

## What is deliberately NOT here

A rule for bare `except`. Ruff's `E722` already covers it, and two gates for one rule is how
you end up with contradictory verdicts on the same line and an argument about which tool is
authoritative. Restraint is part of the design.

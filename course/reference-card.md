# Agentic SDLC — one page

> **Anything you can only ask for, you don't have.**

That line generates the rest of this card. It is why a context file is not enough, why tier 0
exists, why an architecture rule belongs in a config file, why an agent must never be a merge
gate, and why a policy that changed no file changed nothing.

## The chain

Each step's contract is a **file path**, not a conversation. Every skill declares its upstream
artifact and stops if it is missing.

```
ticket ─▶ spec-interrogate ─▶ <T>.answers.md + <T>.touchpoints.md ─▶ [STOPS for a human]
       ─▶ spec-draft       ─▶ <T>.md              the spec
       ─▶ build-slice      ─▶ <T>.drift.md        the code, and what it touched off-plan
       ─▶ pr-brief         ─▶ <T>.pr.md           the reviewer's aids
   [FRESH SESSION]
       ─▶ code-review      ─▶ <T>.review.md       0–3 findings, ≤1 blocking, advisory
       ─▶ harvest          ─▶ proposals + a ledger entry
```

`stack-profile` → `gates-draft` run **once per repo**, before any of the above.

## The ladder

Never spend a tier's attention on something the tier below could have caught. Never invert the
verdicts.

| Tier | What | Verdict |
|---|---|---|
| **0** Pre-action | guards that see an edit before it is written | **asks**, or blocks |
| **1** Deterministic | format, lint, types, architecture contract, custom rules, tests | **blocks** |
| **2** Agent judgment | a fresh-context pass against the spec | **comments** |
| **3** Human judgment | domain rules, authorization, whether it should exist | **decides** |

Four layers rather than one good one because capability gaps are unpredictable and uncorrelated
between layers — the Swiss Cheese Model. A hole in any single layer is expected.

**Only tier 1 goes in required status checks.** An agent as a merge gate is non-deterministic,
and a gate that flakes is muted in about a week.

## Run it, installing nothing

```bash
./scripts/sync-skills.sh --print spec-interrogate | pbcopy    # paste into any assistant
./scripts/sync-skills.sh                                      # or install: one file, every host
make setup && python3 tools/lab.py                            # six labs; first three need no key
```

## The five moves — pick the one that maps to a ticket you have

| Move | Start at |
|---|---|
| Interrogate before drafting | `spec-interrogate` |
| Fill in the out-of-scope field | `course/templates/spec.md` |
| One criterion at a time, test first | `build-slice` |
| A machine-checkable architecture contract | `gates-draft` |
| The end-of-ticket harvest loop | `harvest` |

## The four things that cost us most to learn

- **A `layers` contract does not forbid skipping a layer.** `api → repo` passes it. The rule
  that blocks the shortcut is a `forbidden` contract, and it needs `allow_indirect_imports`
  or it fires on the correct path and gets deleted by the first person in a hurry.
- **A test can pass with the code under test deleted.** The one-step check: delete the
  function, does it still pass? Mechanise it — that is mutation testing.
- **A suite can pass with the subject removed.** Pair every negative assertion with a positive
  one a no-op cannot produce, or the suite looks like success and measures nothing.
- **A rule about intent is not checkable; a rule about assertions is.** "Never edit a test to
  make it pass" is unenforceable. "This edit weakens an assertion" is a hook.

## Models

**Use whatever you have. Record which one.** Every claim about a model's behaviour — a stability
number, a pass rate, a review's false-positive rate — is a claim about *that* model on *that*
day, and a number with no provenance is worse than no number, because it looks like evidence.
The teaching default here is Opus 5.5.

## Before you turn anything on

Switching a checker on repo-wide produces thousands of violations, nobody triages them, and the
tool is discredited permanently. **Baseline, diff-scope, then make the suppression expire** —
`RUF100`, `warn_unused_ignores`, `unmatched_ignore_imports_alerting = error`.

Prune the generated context file **under 60 lines by hand**. The pruning is the part that
matters, and the two lines worth most are the ones a generator cannot produce.

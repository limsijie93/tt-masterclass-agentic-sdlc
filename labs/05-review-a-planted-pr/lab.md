---
lab: 05
title: Review a planted pull request
segment: 09
needs: agent
minutes: 40
solution_into: reviews
assertions:
  - name: findings_between
    path: "reviews/LAB-105.review.md"
    low: 1
    high: 3
    hint: "Zero to three findings, each headed `### N · title`. More than three is how a review bot gets muted; this pull request has three worth making."
  - name: at_most_one_blocking
    path: "reviews/LAB-105.review.md"
    hint: "At most one `blocking:` marker, on the highest-ranked finding. There is one marker and it means one thing."
  - name: citations_resolve
    path: "reviews/LAB-105.review.md"
    hint: "A cited path:line does not exist. Every finding carries one, and 'looks implemented' is the thing this replaces."
  - name: footer_verbatim
    path: "reviews/LAB-105.review.md"
    text: "Advisory — not a merge gate."
    hint: "The limits footer goes on every run, verbatim. It is the sentence that keeps tier 2 out of tier 3's job."
  - name: file_mentions
    tier: 2
    path: "reviews/LAB-105.review.md"
    needles: ["middleware.py"]
    hint: "The one finding that must not be missed is in the file the change is about."
  - name: file_mentions
    tier: 2
    path: "reviews/LAB-105.review.md"
    needles: ["reports.py"]
    hint: "One changed file is neither in the touchpoints nor in scope. Diffing against the plan is step 2 for a reason."
---

## Brief

A pull request against `svc/`: three files changed, a spec, a touchpoints file, and 76 lines
of diff. It is small enough to review properly in twenty minutes, which is the point — this is
the size of pull request the whole pipeline exists to produce.

**Review it yourself first, by hand, and write your findings down before you run anything.**
This is the step everyone skips and skipping it destroys the exercise: once you have read a
machine's review you cannot unread it, and the number this lab is really about is how your
findings and its findings differ.

Then run `code-review` in a **fresh session** — one that has never seen this diff — and compare.

One of the things you are going to want to flag is **wrong**. It is wrong for the
characteristic reason, which is the reason most agent review findings are wrong: reasoning
correctly about a change without reading the one line that refutes it. Finding out whether you
took the bait is the calibration, and it is the only part of this that cannot be taught by
explanation.

## Start

```
cd labs/05-review-a-planted-pr
cat spec.md touchpoints.md
cat pr.diff                              # or: git log -p -- . | head -120
python3 -m pytest -q tests/test_limits.py     # it is green. That is not the same as correct.
```

**Step 1 — your own review, first.** Write `reviews/LAB-105.review.md` from the repository
root, by hand, in the shape `code-review` contracts for:

```
### 1 · <title>

blocking: yes

<path>:<line> — one line on why it matters.

criterion N — met / unmet.

action: <one line>
```

Zero to three findings, at most one `blocking:`, every finding carrying a `path:line`, and the
fixed footer at the bottom. The footer is in `.github/skills/code-review/SKILL.md` under
`## Output contract`; copy it verbatim.

**Step 2 — then the machine.** In a session that never saw the diff:

```
./scripts/sync-skills.sh --print code-review | pbcopy
```

Point it at the same spec, touchpoints and diff, and have it write
`reviews/LAB-105.agent.md`. Both paths are gitignored.

**Step 3 — the comparison, which is the actual exercise.** Write down, in your report:

- What you flagged that it missed.
- What it flagged that you would not have.
- Where it was **wrong**, quoted. If you found none, you did not look hard: the measured
  false-positive rate for this kind of review is 86%. See `docs/citations.md`.

```
python3 tools/lab.py check 05
```

The check grades **your** review, not the machine's. That is deliberate.

**And it does not grade the decoy**, which is also deliberate and is worth thirty seconds.
The obvious check is a banned word: fail anyone whose review mentions the admin API. It was
written, and then deleted, because it fails the answer key — finding 2 mentions `admin.py` for
a perfectly good reason. Fixing that means guessing from keywords whether a sentence is a
finding or an aside, which is asserting *whether a finding is correct*, and that is the one
thing `evals/README.md` says may never be asserted. A checker that is wrong about your review
is the same failure as a review that is wrong about your code, one level up.

So the decoy is scored by you, against the reveal below, after you have written your review
down. That is the only honest place for it.

## What good looks like

Three findings, one blocking.

**1 · The limit is not per tenant. `svc/api/middleware.py:18`, and it is the blocking one.**

```python
key = f"rl:{route}"
```

Every tenant hitting `/v1/search` shares one counter, so one noisy tenant still exhausts
everybody's allowance — which is the sentence the ticket opens with. Acceptance criterion 2 is
unmet, and the tell is sitting in the signature: `handle(tenant_id, plan, route)` takes
`tenant_id` and never reads it.

This is the finding tier 1 cannot make. Every gate in this repository passes on that line. It
is syntactically fine, typed correctly, imports nothing it should not, and the tests are green.
Conformance to a spec is a tier-2 judgment by construction.

**2 · The branch that protects the admin API has no test. `svc/api/middleware.py:15`.**

`if limit is None: return 200, {}` is the whole of the internal bypass. Nothing exercises it
through `handle`; the one test of that behaviour calls `limit_for` directly, a layer below the
branch that uses it. The touchpoints file flagged `admin.py` as must-not-regress, and the
protection it depends on is currently held up by nothing.

**3 · A changed file that is not in the plan and is named out of scope.
`svc/service/reports.py:7`.**

`summarise` gained a `generated` key. It is not in the touchpoints, and the spec's
`Out of scope` names report generation. Step 2 of the procedure — diff the changed files
against the plan — finds this in about four seconds, and nothing else does. It is also the
kind of change that is completely harmless right up until it is not.

---

### The decoy, which is the actual lesson

The thing you probably wrote down fourth, and possibly first:

> *The admin API shares `limit_for`, so this change starts throttling internal callers.*

It does not. `svc/service/limits.py:16-17`:

```python
if plan == "internal":
    return None
```

and `middleware.py:15` returns early on `None`. Internal callers are not limited, and were
never going to be.

**Why this particular wrong finding is the right one to plant.** Everything about it is
correct except the conclusion. The helper *is* shared. The hazard *was* real enough that
whoever wrote the touchpoints file marked it `(!)`. The reviewer reasoned properly about a
shared dependency and a blast radius — and did not read the eight lines of the file that
settle it. That is the failure mode of tier 2 in one sentence, and it is why tier 2 comments
and tier 3 decides.

The touchpoints file makes it worse on purpose, which is realistic: being *told* where the
hazard is primes you to find one there. A reviewer's brief is an aid, and its claims are the
author's claims, not evidence.

**What it costs.** A false positive is not free. A reviewer who reads three findings and
discovers one is wrong discounts the other two, and this is how it goes: not a complaint, not
a ticket — a quiet decision to stop reading. Forty comments mutes a bot in two weeks; one
confidently wrong blocking finding on a clean pull request does it in one.

**The deliverable is one sentence.** In your report, under `## What I would do differently`,
write the heuristic you now hold for when to trust a review like this. Everything above is how
you earned the right to write it.

---
name: code-review
allowed-tools: Read, Grep, Glob, Write
description: >
  Run in a fresh session on a pull request that has a spec. Checks every acceptance criterion,
  scope drift against the touchpoints, untested paths, and tests that assert on their own
  mocks. Emits at most three findings, advisory only.
---

## Purpose

Fresh context is the whole trick. A session that wrote the code is completing a story it
already started, and it will defend that story — not from stubbornness, but because the
reasoning that produced the code is still the most available reasoning about it. A new session
has no story to defend.

This is tier 2 of three. **Tier 1 blocks, tier 2 comments, tier 3 decides**, and that order is
never inverted. *Blocking*, in the output below, means one thing only: the single item a human
must resolve before merging. It is a priority marker in a reviewer's queue, not an enforcement
action. Nothing in continuous integration reads this file.

The reason for that split is not politeness, it is determinism. The same pull request reviewed
twice can produce different verdicts, and a gate that flakes destroys trust in about a week —
after which the review is muted, permanently and silently, and the team is worse off than
before it existed.

## When to use / when not to

Use in a session with no memory of writing the code, on a pull request whose ticket has a spec.

Do not use:

- In the session that wrote the code. The skill cannot detect this, so it asks.
- As a merge gate, or as a required status check.
- Without a spec. There is nothing to check conformance against, and a review that invents its
  own criteria is a style opinion wearing a uniform.

And a fixed list of what this **cannot** do, which belongs in the output as well as here:
domain rules, authorization and tenancy scoping, architectural fit, and whether the feature
should exist at all. No amount of reading the diff reveals that an endpoint should be
tenant-scoped. That is not a limitation to work around; it is the definition of tier 3.

## Inputs required

1. `specs/<TICKET>.md` — the acceptance criteria to check against.
2. `specs/<TICKET>.touchpoints.md` — what the change was supposed to touch.
3. The diff for the pull request, and the test files it changes.

`specs/<TICKET>.drift.md` may also exist. If it does, read it before step 2: it is the
implementer's own record of what it had to touch outside the plan, and one clause on why. It
narrows step 2 from *infer the drift from the diff* to *check the declared drift, then look for
the undeclared*. An empty one is a claim worth testing rather than a file worth skipping.

A reviewer's brief written by the author may also exist. If it does, its read order is worth
using and its untested-path candidates are worth verifying — but **its checklist ticks are the
author's claim, not evidence.** The same goes for the drift file: it says what the implementer
noticed, which is not the same as what changed. Confirm every criterion against the code and
the test yourself. Neither is a required input: this skill must work without anything the
author asserts.

**Capabilities.** Reads the diff, the spec, the touchpoints and any drift file; writes `reviews/<TICKET>.review.md`; **runs no commands**. It cannot run the tests it comments on, which is a real limit and the right one: this is tier 2, it is advisory, and a reviewer that could run the suite would be a reviewer tempted to gate on it.

## Procedure

1. **Read the spec before the diff.** For every acceptance criterion, find the code that
   satisfies it *and* the test that proves it. Cite `path:line` for both. Either one missing is
   a candidate finding.
   *Done when:* every numbered criterion has a verdict, with citations.

2. **Diff against the touchpoints.** Any changed file not in the list, and anything the spec's
   `Out of scope` section names, is a candidate. Where a drift file exists, a file it already
   declares with a reason is weaker evidence than one it does not — an undeclared change is
   either an oversight or a change the implementer did not notice making.
   *Done when:* every changed file is accounted for as in-scope, declared drift, or flagged.

3. **Untested paths.** Changed branches with no test exercising them.

4. **Tests that verify nothing.** The check is mechanical: *if you deleted the production code
   under test, would this test still pass?* If yes, it tests nothing. The common shape is a test
   that asserts on a value it configured on a mock a few lines earlier.

5. **Triage.** Rank the candidates by what breaks in production and who notices. Keep the top
   three. Count what you dropped.
   *Done when:* at most three findings, ranked, and the dropped count is known.

6. **Emit**, with the limits footer, every time.

## Output contract

Written to `reviews/<TICKET>.review.md`.

- **Zero to three findings**, ranked. Each carries a `path:line`, the criterion or touchpoint
  it relates to, one line of why it matters, and one line of suggested action.
- **If any finding is emitted, exactly one carries `blocking:`** — the highest ranked. If the
  pull request is clean, emit zero findings and say so. Never manufacture a blocking finding to
  fill the slot: doing that on good code is the fastest way to get this muted, and it happens in
  week one.
- If more than three candidates survived triage, add one line: `N further observations withheld
  — ask for the full list`. Nothing is silently dropped, and nothing is inflated into a comment.
- A fixed footer, verbatim, every run:

> Advisory — not a merge gate. This review cannot judge domain rules, authorization or tenancy
> scoping, architectural fit, or whether this feature should exist. A human decides.

## Stop conditions

- No spec for this ticket. Stop, and say that drafting one is the prerequisite.
- The diff cannot be obtained. Stop.
- This session wrote the code. Ask for a fresh session and stop — and say plainly that the skill
  cannot verify this, so it is asking rather than detecting.
- More than three candidates that all look blocking. Emit three, say "this pull request is larger
  than one review", and suggest splitting it.

## Anti-patterns

- **Forty comments.** That is how a review bot gets muted in two weeks, and the muting is
  permanent and silent — nobody files a ticket saying they stopped reading.
- Nits that the formatter, the linter, or the type checker already enforce. That is tier-2
  attention spent on tier-1 work, and it is the same error as a senior engineer commenting on
  import order.
- Inventing severity tiers. There is one marker, and it means one thing.
- Approving or blocking anything.
- Reviewing in the session that wrote the code.
- Scores, percentages, and letter grades. They imply a precision that does not exist.
- Asserting a criterion is met without citing the test that proves it. "Looks implemented" is
  the thing this skill exists to replace.

<!-- More shapes of test that verifies nothing, with the reasoning for each, are collected in
     references/tautological-tests.md.

     That pointer is HERE and not in the Procedure on purpose. No step of the procedure may
     depend on a reference file, because the body has to work pasted into a chat with nothing
     installed — installing is an optimisation, not a prerequisite. The delete-the-code test in
     step 4 is sufficient on its own; the reference file is enrichment for someone who has the
     repo, which is exactly what a third disclosure tier is for.

     tooling/scripts/lint_skills.py enforces this, and it caught this very file on the first run. -->

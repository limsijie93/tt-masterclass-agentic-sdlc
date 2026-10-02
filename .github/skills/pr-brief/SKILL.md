---
name: pr-brief
allowed-tools: Read, Grep, Glob, Write
description: >
  Run when opening or updating a pull request that has a spec. Produces the description, a
  checklist from the acceptance criteria, a suggested read order, and candidate untested
  paths. It describes; it never judges.
---

## Purpose

Better specs and enforced boundaries make a team faster at producing code. They do not add
reviewers. So the bottleneck moves to review, and pull requests arrive larger and more often at
the same number of people.

This skill spends a few minutes of the author's time to save more of the reviewer's. It
produces four things that change what reviewing feels like: a description written from the
spec, a checklist built from this pull request's actual criteria, an order to read the files
in, and a mechanical list of paths that changed without a test changing.

It produces **no opinions**. That separation is not tidiness — it is the reason the review that
follows can be trusted. This runs in the session that wrote the code, which is exactly the
session that will defend the code. Judgement belongs to a fresh session, and the reviewer needs
to know which of the two they are reading.

## When to use / when not to

Use after implementation, in the session that wrote the code. It is the one skill in this set
that benefits from that context, because it needs to know what was done and why.

Do not use it as a review. No verdict, no severity, no approval language, nothing that resolves
a question rather than surfacing one. If you find yourself forming a judgement, that output
belongs to a different session and a different skill.

Do not use it without a spec. Every one of the four outputs is derived from one, and a brief
assembled from the diff alone tells the reviewer what the code does — which they can already
see — rather than what it was supposed to do.

## Inputs required

1. `specs/<TICKET>.md` — the description and the checklist both come from here.
2. `specs/<TICKET>.touchpoints.md` — to mark anything changed outside the declared set.
3. The diff for the pull request, and the test files.

The pull request number, if it exists yet.

**Capabilities.** Reads the diff and the files it touches; writes `specs/<TICKET>.pr.md`; **runs no commands**. It describes and never judges, and it needs nothing a shell provides to do that.

## Procedure

1. **Description.** Three or four sentences, from the spec's problem statement and goal. Every
   sentence traceable to a line in the spec. Make no claim about behaviour the spec does not
   state — a description that over-promises is worse than none, because the reviewer checks
   against it.

2. **Checklist.** One unchecked box per acceptance criterion, **quoted verbatim** from the
   spec, each with the `path:line` that implements it. Do not paraphrase: the reviewer is
   checking these against the spec, and a reworded criterion makes that comparison work rather
   than automatic.
   A criterion with nothing found is marked `(no implementation found)` and left in place. That
   is a fact to record, not a verdict to reach.
   *Done when:* one box per criterion, every criterion quoted, none silently dropped.

3. **Read order.** Three to six files, ordered so each is comprehensible given the ones before
   it, with one clause each on why it comes next. Not alphabetical, and not the diff's order —
   on a large diff this is the single biggest improvement available, and a list that matches
   `git diff --name-only` provides none of it.

4. **Candidate untested paths.** Mechanical only: changed functions and branches with no
   corresponding change in a test file. List them. Do not rank them, do not conclude anything
   about them, and do not call any of them a risk. A deterministic tool does this better —
   `diff-cover` on changed lines — and where one is available, use its output rather than
   guessing.

5. **Emit.** Any changed file outside the touchpoints is noted under read order as `outside
   touchpoints`, with no comment. Whether that is drift or a gap in the spec is a judgement,
   and judgement is not this skill's job.

## Output contract

`specs/<TICKET>.pr.md`, four sections, in this order:

```
## Description
## Acceptance criteria
## Read order
## Candidate untested paths
```

Zero findings. Zero severities. No approval language, and no sentence that could be quoted as a
verdict.

## Stop conditions

- No spec for this ticket. Stop, and say that drafting one is the prerequisite. There is no
  honest reviewer aid without a statement of intent to aid against.
- The diff cannot be obtained.
- You catch yourself forming a verdict. Drop it and stop. Producing a review here quietly
  destroys the fresh-context property the next stage depends on, and nobody downstream can tell
  it happened.

## Anti-patterns

- Writing a review. "LGTM", "this looks correct", "minor concern" — all of it belongs elsewhere.
- Paraphrasing acceptance criteria instead of quoting them.
- A read order that is just the diff's file order, or alphabetical.
- Describing what the code does instead of what the spec asked for. The reviewer can read the
  code; they cannot read the intent.
- Ranking the untested paths, or implying which matters. That is triage, and triage is tier 2.
- Ticking a box because the implementation exists. The boxes are for the reviewer to tick.

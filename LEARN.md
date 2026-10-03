# Start here

You just watched **Agentic SDLC: Specs → Quality → Review**. This is the hour after.

[`README.md`](README.md) is the reference — what every file is, why it is shaped that way, and
how to install it. Read that when you are ready to put this in your own repository. Read this
first.

Following along lesson by lesson? [`course/guide.md`](course/guide.md) maps every
lesson to the files to read, the lab to do, and what to copy, with a diagram for each block.

---

## Which of these are you?

Three ways through this document, and the only wrong one is starting at the top and stopping
when you run out of evening. Pick the row that describes the next hour you actually have.

| | You are | Do this | Cost |
|---|---|---|---|
| **Observer** | deciding whether any of this is for you | the five minutes below, then `course/tickets/PROJ-142/` in order | 20 min, read-only |
| **Doer** | convinced, and want it in your hands | [`course/labs/`](course/labs/) — 01 to 03 need no agent and no API key | 2½ hours, keyboard |
| **Adopter** | putting this in a repository your team ships from | [`README.md`](README.md), then the three pull requests it opens with | an afternoon, then a week |

**The jump that matters is Observer to Doer, and it is the one people skip.** Reading builds
recognition — you will spot a tautological test on a slide. Only reps build calibration, which
is knowing whether the one in front of you is tautological when nobody has told you to look.
The labs exist because that jump had no step in it.

## If you only have five minutes

Open [`course/tickets/PROJ-142/`](course/tickets/PROJ-142/) and read three files in this order:

1. [`01-ticket.md`](course/tickets/PROJ-142/01-ticket.md) — a ticket that is not badly written, just
   normal, and missing everything an implementer needs.
2. [`02-interrogation.md`](course/tickets/PROJ-142/02-interrogation.md) — the five questions that were
   missing, and the line where the agent **stops**.
3. [`08-review.md`](course/tickets/PROJ-142/08-review.md) — three findings on the finished work. One of
   them is wrong. See if you can tell which before you look it up.

That is the whole lecture in three files: the input was the problem, stopping is the mechanism,
and the reviewer is not an oracle.

---

## The hour after

### 1 · Read one ticket, end to end (~15 min)

[`course/tickets/PROJ-142/`](course/tickets/PROJ-142/) is one ticket from a vague bug report to reviewed code
to a lesson written down. Read it in numeric order. What to notice in each:

| File | What to notice |
|---|---|
| `01-ticket.md` | It is a *typical* ticket, not a bad one. Five things are missing and none of them through carelessness. |
| `02-interrogation.md` | Every question carries the **assumption it hides**. That is what makes it answerable in seconds rather than in a meeting. Then it stops. |
| `03-answers.md` | Four minutes of a human's time. The table at the bottom shows what each answer bought — two of them become the acceptance criteria. |
| `04-touchpoints.md` | The `(!)` line. Nobody asked for it; it was found by searching for other callers. It is read three more times before this ticket ends. |
| `05-spec.md` | `Out of scope` has three entries. That is the field teams omit most and it prevents the most rework. |
| `06-git-log.txt` | Commits named by acceptance criterion. **And the arithmetic**: four files changed, all inside the plan, and the change still broke something. |
| `07-pr-body.md` | The checklist boxes are unticked on purpose. An author ticking their own checklist turns the reviewer's job from checking into trusting. |
| `08-review.md` | Three findings, one blocking, **one wrong**. |
| `09-tests-that-lie.md` | A test that passes with the code under test deleted — and, unlike the slide, the honest rewrite beside it. |
| `10-harvest.md` | Three findings, **one** proposal. The restraint is the mechanism, not timidity. |
| `00-agents-draft.md` | Read last. Diff it against [`course/templates/python/AGENTS.md`](course/templates/python/AGENTS.md): 166 lines to 75, and the closing table says why each cut was made. |

### 2 · Try one skill, installing nothing (~10 min)

Every skill works pasted into any assistant. Installing is an optimisation, not a prerequisite.

```
./tooling/scripts/sync-skills.sh --print spec-interrogate | pbcopy
```

Rather install it? In Claude Code (the terminal, or the Code tab in Claude Desktop):

```
/plugin marketplace add limsijie93/tt-masterclass-agentic-sdlc
/plugin install agentic-sdlc@tt-masterclass-agentic-sdlc
```

In Claude Desktop chat, upload `spec-interrogate.zip` from the
[latest release](https://github.com/limsijie93/tt-masterclass-agentic-sdlc/releases/latest)
under **Customize → Skills**. Every other route is in
[the README](README.md#installing-them-or-not).

Paste it into whatever you use, or invoke it, then paste a **real ticket from your own
backlog** underneath.
Do not use PROJ-142 — the point is to see it work on something you know is ambiguous.

You are looking for one thing: does it ask you something you had not thought about, and does it
**stop**? If it answers its own questions, the stop condition is the part that failed, and that
is worth knowing about your assistant.

### 3 · Do a lab, with your hands on the keyboard (~20 min) — **the Doer step**

Reading builds recognition. Only doing builds the thing the lecture is actually about, and
this is the shortest path to it:

```
make setup && source .venv/bin/activate
./lab start 01
```

Lab 01 hands you a 146-line `AGENTS.md` a generator produced for `tooling/myapp/` and asks you to cut
it under sixty lines by hand. It takes twenty minutes, it needs no agent and no API key, and
one of the statements in the draft is false — which is the half of the lesson that is not
about length.

[`course/labs/`](course/labs/) has five, about two hours in total. The first three need nothing installed
beyond the toolchain above. A checker tells you what you missed and, when the failure is your
assistant rather than you, says so.

### 4 · Check yourself against the two planted errors (~5 min)

Two files here are deliberately wrong, because judgment is built by reps and not by explanation.

- **[`08-review.md`](course/tickets/PROJ-142/08-review.md)** — one of the three findings is a false
  positive. Work out which and *why it is wrong* before checking. The answer
  is not in this repository: commit to yours, then watch the Tier 2 lesson, which reveals it.
- **[`09-tests-that-lie.md`](course/tickets/PROJ-142/09-tests-that-lie.md)** — the first test verifies
  nothing. The check that catches it in one step: *delete the function under test. Does this
  still pass?*

If you got the false positive on sight, you already have the reviewer skill the lecture is
about. If not, read *why* it is wrong — it is wrong for the characteristic reason, and that
reason will recur.

### 5 · Then adopt, if you want to (~10 min) — **the Adopter step**

Now [`README.md`](README.md) is the right document. Shortest useful version:

1. `stack-profile` on your repo, correct what it got wrong, then `gates-draft`. You get a
   **baselined** contract and hook config for your stack.
2. Prune the generated `AGENTS.md` under 60 lines by hand. The pruning is the part that matters —
   see step 1's last row for what unpruned looks like.
3. Add `tier1` and only `tier1` to your branch's required checks.

Read [`course/templates/README.md`](course/templates/README.md) before switching anything on. Turning a checker
on across an existing repo produces thousands of violations, nobody triages them, and the tool is
discredited permanently. That kills more of these rollouts than any other single mistake.

---

## The five moves, and which one to try first

All of this on one page, to pin up: [`course/reference-card.md`](course/reference-card.md).

From the close of the lecture. Pick the one that maps to a ticket you actually have:

| Move | Start at |
|---|---|
| Interrogate before drafting | [`spec-interrogate`](.github/skills/spec-interrogate/SKILL.md) |
| Fill in the out-of-scope field | [`course/templates/spec.md`](course/templates/spec.md) |
| A machine-checkable architecture contract | [`gates-draft`](.github/skills/gates-draft/SKILL.md) |
| One criterion at a time, test first | [`build-slice`](.github/skills/build-slice/SKILL.md) |
| The four-rung review ladder | [`README.md`](README.md#the-review-ladder-and-the-files-that-implement-it) |
| The end-of-ticket harvest loop | [`harvest`](.github/skills/harvest/SKILL.md) |

## When you want reps: review code you just wrote

The hour above builds recognition. This builds calibration, and it takes an afternoon rather
than an hour. It is the exercise the lecture cannot run — the room's editors are closed —
and it is the one thing that reliably transfers.

Adapted from the review week of **Stanford CS146S** (see `Prior art` in [`README.md`](README.md)),
with the tooling removed so it works with whatever you already use.

**Pick four small tasks in a repository you know.** Real ones, from your backlog. Then, for each:

1. **A branch of its own**, and implement it with a **single** prompt. One shot, no follow-ups.
   The point is to produce genuine agent output, not your best pair-programming result.
2. **Review it line by line yourself, first.** Write your findings down before you see any
   machine's. This is the step people skip, and skipping it destroys the whole exercise — once
   you have read the agent's review you cannot unread it.
3. **Open the pull request**, with a description, what you ran to test it, and the tradeoffs.
   [`pr-brief`](.github/skills/pr-brief/SKILL.md) writes this from the diff.
4. **Then** run [`code-review`](.github/skills/code-review/SKILL.md) **in a fresh session** — one
   that never saw the code being written. That constraint is the whole mechanism.

**The comparison is the exercise. The four pull requests are scaffolding.** Write down:

- What you flagged that it missed. Expect this to be the domain-shaped findings — tenancy,
  authorization, whether the thing should exist. That is tier 3, and it is why tier 3 exists.
- What it flagged that you would not have. Expect untested branches and drift outside the plan.
- Where it was **wrong**, quoted. This is the number that matters, and it is why tier 2 comments
  and tier 3 decides. The measured false-positive rate for this kind of review is high enough
  that finding none means you did not look hard — see [`course/citations.md`](course/citations.md).
- **The heuristic you now hold** for when to trust it. One sentence. That sentence is the
  deliverable; everything above it is how you earned the right to write it.

If you want a calibration check before spending the afternoon, do
[**lab 05**](course/labs/05-review-a-planted-pr/lab.md) first. It is this exercise in forty minutes on
a pull request someone else planted: three real findings, and one thing you will want to flag
that is wrong for the characteristic reason. Marked against a key, so you find out.

[`08-review.md`](course/tickets/PROJ-142/08-review.md) is the same idea to read rather than to do — a
finished review with one finding deliberately wrong.

## Two honest things before you clone

**The application here is deliberately tiny, and it is not a product.** `tooling/myapp/` is about six
hundred lines that exist to fail in five specific ways: no auth, no migrations, no deployment, one
table and a decoy. It was not here for most of this repo's life, and it earned itself in the first
hour — turning the real tier-1 stack on against real code immediately found a semgrep rule that
matched none of the actual call sites while passing its own unit tests, and an architecture
contract that did not forbid what the worked example says it forbids. Both had been green for
weeks. Every `path:line` the worked example cites now resolves against it, and
`tooling/tests/test_example_consistency.py` fails if one stops resolving.

**One thing here is not on the slides.** The lecture promises a guard in passing — *"a
pre-execution hook that blocks illegal writes before the file changes"* — and then draws the
ladder with three rungs, so the mechanism is named and never shown. It exists here:
[`tooling/tools/guard_test_edits.py`](tooling/tools/guard_test_edits.py), tier 0. It does not block editing
tests, it blocks *weakening* them, and finding that distinction is the interesting part — a rule
about intent is not checkable, a rule about assertions is. See the Tier 0 section of the README.

## Where the labs are

[`course/labs/README.md`](course/labs/README.md) — five labs, how they are marked, and the two rules the
checker holds itself to. A lab is an eval case with a human as the engine, which is why the
assertion vocabulary is the same one the skills are tested with.

## Where the demos are

[`course/demos.md`](course/demos.md) — every recording, which segment it belongs to, and the **exact
commands**, so you can run any of them yourself rather than only watch. Five of them run against
this repository with nothing else installed.

# Demos

Every recording, what it is for, and the exact commands. Two audiences: the presenter, who needs
a shot list, and a learner who would rather run a demo than watch one.

**Nothing here lives in a `SKILL.md`.** `tooling/scripts/lint_skills.py` enforces exactly seven sections
and a 200-line paste-first budget, and bans host names in a skill body — a `## Demo` section with
a video link would fail the build on two counts. The mapping lives here instead.

## Status at a glance

The deck specifies seven demos, D1–D7. Five of them need a runnable application to fail against,
and `tooling/myapp/` is now that application — so the blocker moved from *no target* to *no shot list*.
D8–D12 run against **this repository, today**, have their beats written below, and several cover
ground the original seven do not. D13–D17 give the five skills that had no demo one each.

**Nothing here has been filmed.** `ready` below means the commands exist and produce the output
quoted beside them; it does not mean an asset exists.

| | Demo | Chapter | Skill / artifact | Status |
|---|---|---|---|---|
| D1 | Cold open — the confident wrong answer | 0.2 | `tooling/myapp/repo/analytics.py` (the decoy) | **ready** |
| D2 | Skill portability — one file, two tools | 1.1 | all skills | **ready** — see D11, which is the honest version |
| D3 | `AGENTS.md` A/B | 2.1 | `00-agents-draft.md` | **ready** |
| D4 | The architecture contract fails | 2.2 | `gates-draft` | **ready** — beats lifted from lab 02 |
| D5 | Invented API + scope creep | 2.3 | `build-slice` | **ready** |
| D6 | Tier-2 triaged review | 3.2 | `code-review` | **ready** — the branch is lab 05 |
| D7 | The tautological test | 3.3 | — | **ready** — a still, from `09-tests-that-lie.md` |
| **D8** | **The guard blocks a weakened test** | **2.2 / 2.3** | `guard_test_edits` | **ready** |
| **D9** | **A test suite that cannot fail** | **3.3 / 4.1** | evals | **ready** |
| **D10** | **The context file and the gate diverge** | **2.1 / 2.2** | `check_commands_sync` | **ready** |
| **D11** | **One file, every host** | **1.1** | `sync-skills` | **ready** |
| **D12** | **The pruning, as a diff** | **2.1** | `00-agents-draft.md` | **ready** |
| D13 | The question you had not thought of | 1.2 | `spec-interrogate` | **beats written** — dry run pending |
| D14 | The out-of-scope section | 1.3 | `spec-draft` | **beats written** — dry run pending |
| D15 | The reviewer's read order | 3.3 | `pr-brief` | **beats written** — dry run pending |
| D16 | A finding becomes a rule | 4.1 | `harvest` | **ready** — the loop is walked without an agent |
| D17 | Reading a repo it has never seen | 2.2 | `stack-profile` | **beats written** — dry run pending, needs a scratch repo |

**All seventeen have beats.** Nothing is filmed. D13, D14, D15 and D17 drive a live agent and
have not had a dry run, so their quoted output is the skill's output contract and the worked
example, not a captured take. `beats written` becomes `ready` after one dry run matches.

**Film D8–D12 first.** They run against this repository with nothing installed, they need no
model call on camera, and D8 in particular closes a hole in the lecture rather than illustrating
a point it already makes.

**D1, D3 and D5 need a live agent on camera, and that is a different kind of risk.** Their
output is non-deterministic — which is the lecture's own thesis, so a take that goes differently
is not a failure — but a take where the agent gets it *right* leaves the chapter with nothing to
show. Record several, and be ready to narrate the one where it behaves: *"this is the run where
it worked, and you cannot tell in advance which run you are getting. That is the whole
argument."*

---

## D1 · Cold open — the confident wrong answer

**Chapter 0.2. Roughly 70 seconds, and it is the first thing the room sees.**

The decoy is `tooling/myapp/repo/analytics.py`. It is smaller than `export_row`, it is one row per
account per day, and its name sounds more like a report than `exports/queries.py` does. An agent
handed the ticket with no context file and no spec reaches for the table whose name sounds right.

**Setup.** A session with **no** `AGENTS.md` loaded and no spec — `--bare`, or a scratch copy of
`tooling/myapp/` alone. This matters: with the context file present the gotcha section names the decoy
outright, which is D3's point and would spoil this one.

**Beat 1 — the ticket, pasted.** `course/tickets/PROJ-142/01-ticket.md`, verbatim. Say nothing about
the codebase.

**Beat 2 — let it work.** The shot is the moment it opens `analytics.py`. Do not narrate over it.

**Beat 3 — the output.** A CSV. Correct-looking columns, plausible dates, and the wrong number
of rows, because daily totals are one row per account per day and the export is one row per
event.

```
PYTHONPATH=tooling python3 -c "
import sqlite3
from myapp.repo.exports import queries
c = sqlite3.connect(':memory:'); c.executescript(queries.SCHEMA)
queries.seed(c, account_id=1, rows=500)
print('export_row for account 1   :', queries.count_export_rows(c, 1), 'rows - one per event')
print('analytics_daily would give : at most 28 - one per account per DAY')
"
```

> `export_row for account 1   : 500 rows - one per event`
> `analytics_daily would give : at most 28 - one per account per DAY`

Two numbers, side by side. That is the whole demo, and the gap is **structural** — it comes
from the two schemas in `queries.py` and `analytics.py`, not from the data. There is no
`seed()` on the analytics table, deliberately: a demo that depended on generated rows matching
would be a demo about the fixture.

**The line to say:** *it did not fail. It did not error, it did not warn, and it did not ask. It
produced a file that looks exactly like the thing that was asked for, and the number in it is
wrong. Nothing downstream of this catches a wrong number — not a linter, not a type checker, not
a test that nobody wrote.*

**Gotchas.** Non-deterministic: some runs pick the right table. Record five and keep the one that
goes wrong, and if a take goes right, that is worth its own sentence — *you cannot tell in
advance which run you are getting.* Do not stage the wrong answer: a prompt that steers it to
`analytics.py` is a lie, and the room will smell it.

---

## D3 · `AGENTS.md` A/B

**Chapter 2.1. Roughly 60 seconds.** The same ticket, twice, and the only variable is one file.

**Beat 1 — without.** The D1 take, or a fresh one. It reaches for `analytics.py`.

**Beat 2 — with.** Same prompt, same model, and the pruned context file for `tooling/myapp/` copied to
the repo root:

```
cp course/labs/01-prune-the-context-file/pruned.md AGENTS.md    # your answer from lab 01
grep -A4 'is a decoy' AGENTS.md
```

**Not `course/templates/python/AGENTS.md`** — that is a fill for the *fictional* service and names no
decoy, so beat 2 would change nothing and the A/B would show a difference that was not there.
```
lint-imports --config yours.ini     # your answer from lab 02
```

> `The API layer goes through the service layer BROKEN`
> `-   shop.api.bad -> shop.repo.queries (l.7)`

**The line to say:** *a `layers` contract forbids a lower layer importing a higher one. It does
not forbid a higher layer skipping a layer to reach a lower one, and nothing tells you — a
contract that is KEPT looks exactly like a contract that is working. This sat on a slide and in
a spec in this repository for weeks, and only running it against real code found it.*

**Beat 4, optional and worth the ten seconds.** Delete `allow_indirect_imports = true` and rerun:
it now also flags `shop.api.good`, which is the *correct* path through the layers. *A gate that
fails on healthy code gets deleted by the first person in a hurry.*

**Restore.** Nothing to restore — `yours.ini` is a learner file and gitignored.

---

## D5 · Invented API + scope creep

**Chapter 2.3. Roughly 60 seconds.** The chapter that had no artifact until `build-slice`, so
this demo shows the artifact rather than the absence.

**Beat 1 — the spec, and one criterion.** `course/labs/06-implement-one-criterion/spec.md`. One
acceptance criterion, a three-line touchpoints file.

**Beat 2 — run it.** `/build-slice` with `specs/LAB-106.md`. The shot is the loop: failing test,
confirm red, implement, run the checks, commit named by the criterion.

**Beat 3 — the drift file, which is the point.**

```
cat specs/LAB-106.drift.md
```

> `## Outside the touchpoints`
> `tooling/myapp/api/exports/views.py:30      ExportResponse gained retry_after_seconds…`
> `tooling/myapp/service/exports/service.py:88   ROWS_PER_SECOND is new…`

**The line to say:** *the touchpoints named three files and it touched five. Neither extra is a
mistake — grounding happened before anyone had implemented anything. The failure mode is not
touching them, it is touching them silently. `git diff --stat` finds a file appearing where the
spec did not expect one. It does not find the file the spec **did** expect, changed in a way
nothing predicted, and in the worked ticket that second kind is exactly what broke.*

**The invented API is a catch, not a beat.** The deck's Demo 5 promises a call to a method that
does not exist, failing the moment it runs. It is not scripted here because it cannot be staged
honestly — a prompt that asks for a fake method is a lie. `build-slice` runs the tests after every
criterion, so if a take invents one it fails on screen in the red/green loop: keep that take and
cut to it. If no take produces one after the six-re-roll budget, say so on camera and narrate the
mechanism over the loop instead: *it runs early and often, so an invented call cannot survive to
the pull request.*

**Gotchas.** Non-deterministic. If it strikes out on the criterion, **keep the take** — the
`## Struck out` section and the two-strike rule are a better demo than the happy path, and
nothing else in the deck shows an agent stopping because it could not do something.

---

## D6 · Tier-2 triaged review

**Chapter 3.2. Roughly 80 seconds.** The branch already exists: `course/labs/05-review-a-planted-pr/`,
three real findings and one decoy that is wrong for the characteristic reason.

**Beat 1 — the inputs.** `spec.md`, `touchpoints.md`, `pr.diff`. Seventy-six lines, three files.
*This is the size of pull request the whole pipeline exists to produce.*

**Beat 2 — the suite is green.**

```
cd course/labs/05-review-a-planted-pr && python3 -m pytest -q tests/test_limits.py
```

*Green is not the same as correct.*

**Beat 3 — run `code-review` in a session that never saw the diff.** The constraint is the
mechanism, and say so while it runs.

**Beat 4 — the output, and the poll.** Three findings, one blocking. The blocking one is the
counter key built from the route alone, so every tenant shares one bucket — which is the sentence
the ticket opens with. **Then ask the room which finding is wrong.**

**Beat 5 — the reveal.** If the take flagged the admin API as a regression:

```
sed -n '13,18p' svc/service/limits.py
```

> `if plan == "internal": return None`

**The line to say:** *every step of that reasoning is right except the conclusion. The helper is
shared, the touchpoints file flags it, and the eight lines that settle it were not read. That is
the failure mode of tier 2, and the measured false-positive rate for this kind of review is 86%.
One wrong in three is better than the average. This is why tier 2 comments and tier 3 decides.*

**Gotchas.** If the take does not produce the decoy, do not fake it — narrate the planted answer
from `course/labs/05-review-a-planted-pr/lab.md` instead and say the run was a good one. And disable the
`mattpocock-skills` plugin: its `code-review` competes for the same trigger.

---

## D8 · The guard blocks a weakened test

**Chapters 2.2 and 2.3. Roughly 60 seconds. Record this one first.**

Why it matters more than its length suggests: slide 22 already promises this — *"Guard
(strongest): a pre-execution hook that blocks illegal writes before the file changes"* — and then
the ladder on slide 29 tables three rungs, not four. So the deck names the mechanism in passing
and never shows it. D8 is the only demo here that covers a tier the lecture asserts but does not
demonstrate.

**Setup.** Clean working tree. `GUARD_MODE` unset for the first beat.

**Beat 1 — the rule as prose, and how many times we say it.**

```
grep -rl "in order to make an implementation pass\|edited into greenness" \
  --include='*.md' . | grep -vE 'README.md|course/demos.md' | sort
```

Ten files. On screen: it is written down everywhere, and nothing checks it. Two of the ten are
new since the count was first taken — the `build-slice` skill and lab 01's answer key. The answer key is not in this copy, so you will count
nine.

The two exclusions are not cosmetic — `README.md` and this file *discuss* the rule rather than
state it, and a grep that counts its own command is the kind of thing that unravels on camera.
Re-run the command if you edit any of those eight; the number in the narration has to be the
number on screen.

**Beat 2 — weaken a real test.** In the editor, in `tooling/tests/test_check_touchpoints.py`, replace

```
    assert declared == set()
    assert extras == set()
```

with `assert True`. Stage it.

**Beat 3 — the commit-time half catches it.**

```
python3 tooling/tools/guard_test_edits.py --staged
```

> `guard_test_edits: ask — this edit removes 1 assertion(s) from tooling/tests/test_check_touchpoints.py`
> `and adds no new test (assertions 12 -> 11, tests 8 -> 8).`

**Beat 4 — the write-time half blocks it.** The stronger beat, because it happens *before* the
file is written:

```
GUARD_MODE=enforce python3 tooling/tools/guard_test_edits.py <<< '{"tool_name":"Write","tool_input":{"file_path":"tooling/tests/test_check_touchpoints.py","content":"def test_x():\n    pass\n"}}'
echo "exit=$?"
```

> `this edit removes every assertion from tooling/tests/test_check_touchpoints.py (assertions 11 -> 0).`
> `A test file that asserts nothing passes unconditionally, including with the code under test deleted.`
> `exit=2`

**Beat 5 — the reframe, narrated over `--explain`.**

```
python3 tooling/tools/guard_test_edits.py --explain tooling/tests/test_check_touchpoints.py
```

The line to say: *every version of that rule says "in order to make it pass" — which is a claim
about intent, and no checker can see intent. Making it checkable forced us to find what the rule
was actually about: the edit weakens an assertion. It does not block editing tests. It blocks
weakening them, which is why test-first still works.*

**Restore before the next take.** `git checkout -- tooling/tests/test_check_touchpoints.py`

**Gotchas.** Beat 4's counts read `11 -> 0` rather than `12 -> 0` because beat 2 already removed
one — do not re-record from a clean file and expect matching numbers. And the default is
`GUARD_MODE=log`, so beat 4 needs the variable set explicitly or nothing blocks.

---

## D9 · A test suite that cannot fail

**Chapters 3.3 and 4.1. Roughly 45 seconds.** The most transferable idea in the set, and it needs
no application.

**Beat 1 — run the suite with an engine that does nothing.**

```
EVAL_ENGINE_CMD=true python3 tooling/tools/run_evals.py --case spec-draft-refuses-unanswered
```

> `✓ did_not_write: specs/EVAL-102.md was correctly not written`
> `✗ output_mentions: output omits 'EVAL-102'`
> `✗ output_mentions: output omits 'answer'`
> `✓ cost_under: no cost reported by the engine`
> `  FAIL`

**Beat 2 — the point, over the frozen output.** *`true` is a program that does nothing and exits
zero. No skill ran. And two assertions passed — because "the skill did not write a spec" and "it
cost almost nothing" are both trivially true when nothing happened at all. That is the shape of a
test that cannot fail: it looks like success.*

*So every negative assertion is paired with a positive one a do-nothing engine cannot produce.
The whole suite scores zero:*

```
EVAL_ENGINE_CMD=true python3 tooling/tools/run_evals.py --all | tail -1
```

> `0/7 passed`

**Ties back to** `09-tests-that-lie.md` — this is the same idea one level up. There it was a test
that passes with the code deleted; here it is a test suite that passes with the subject removed.

---

## D10 · The context file and the gate diverge

**Chapters 2.1 and 2.2. Roughly 40 seconds.** Concrete answer to *"how do you stop the context file
rotting?"*

**Beat 1 — they agree.**

```
python3 tooling/tools/check_commands_sync.py
```

> `python: 5 tools agree — lint-imports, mypy, pytest, ruff, semgrep`
> `typescript: 6 tools agree — depcruise, eslint, prettier, semgrep, tsc, vitest`

**Beat 2 — delete one line from `course/templates/python/AGENTS.md`**, the `semgrep scan` line under
`## Commands`. A plausible tidy-up, not sabotage.

**Beat 3 — the build fails, and says which direction.**

```
python3 tooling/tools/check_commands_sync.py; echo "exit=$?"
```

> `python: DIVERGED`
> `  Enforced by pre-commit-config.yaml but NOT in AGENTS.md Commands: semgrep`
> `  The agent will not run these before showing you code, so they fail in CI`
> `  instead of on the developer's machine.`
> `exit=1`

Note TypeScript stays green — each ecosystem is checked on its own terms.

**The line to say:** *this check found a real divergence the first time it ran. Semgrep was in the
gate and not in the context file, and I had not noticed.*

---

## D11 · One file, every host

**Chapter 1.1. Roughly 50 seconds.** The honest version of D2: the deck's version shows a file
copied into two tools, which asserts portability. This shows it.

```
ls -l .claude/skills/spec-interrogate .cursor/skills/spec-interrogate .agents/skills/spec-interrogate
```

> all three: `-> ../../.github/skills/spec-interrogate`

*Three hosts. One file. Not three copies that will drift — three symlinks, committed, and a
check that fails if any goes stale:*

```
./tooling/scripts/sync-skills.sh --check | tail -1
```

> `8 skills, all destinations in sync.`

*And installing is optional anyway:*

```
./tooling/scripts/sync-skills.sh --print spec-interrogate | pbcopy
```

Paste into a third assistant with nothing installed. **Disable the `mattpocock-skills` plugin
first** — it ships its own `code-review` skill occupying the same trigger space, and it can fire
instead on camera.

---

## D12 · The pruning, as a diff

**Chapter 2.1. Roughly 40 seconds.** The chapter says *the pruning is the teaching*. This makes it
a diff rather than an assertion.

```
wc -l course/tickets/PROJ-142/00-agents-draft.md course/templates/python/AGENTS.md
```

> 166 lines generated, 75 pruned.

```
diff <(grep '^## ' course/tickets/PROJ-142/00-agents-draft.md) <(grep '^## ' course/templates/python/AGENTS.md)
```

> gone: `Project Overview`, `Repository Structure`, `Technology Stack`, `Development Setup`,
> `Coding Standards`, `Testing`, `Python Best Practices`, `Git Workflow`, `Deployment`

**The line to say:** *almost none of those were cut for length. The repository structure is wrong
the first time someone adds a module. The pinned tool versions rot in a month. "We always write
tests" is aspirational against 61% coverage — and an agent believes you.*

**Then the payoff:** scroll to the closing table of `00-agents-draft.md` and the two lines the
generator could not produce — the slow-fixture gotcha and the no-editing-tests rule. *Generation
gets a draft in thirty seconds. The value is entirely in what a human adds afterwards.*

## D13 · The question you had not thought of

**Chapter 1.2. Roughly 60 seconds.** `spec-interrogate` on the real ticket. The shot is that it
stops.

**Setup.** This repository, root `AGENTS.md` present: grounding needs to read the code, and the
decoy is not the point here. No `specs/PROJ-142.*` from an earlier take.

**Beat 1 — the ticket.** `course/tickets/PROJ-142/01-ticket.md`, pasted. Then `/spec-interrogate PROJ-142`.

**Beat 2 — grounding, read-only.** Let it open files without narration. Every claim it makes will
carry a `path:line`.

**Beat 3 — the output, and the stop.** `specs/PROJ-142.answers.md`, in the shape the skill's
output contract fixes:

> at most five questions, each with `blocks`, `assumes`, and an empty `answer:`
> `[ stopped - waiting for a human ]`

Then `specs/PROJ-142.touchpoints.md`. Cover its last entry for the prediction poll, then reveal:

> `(!) tooling/myapp/service/reports/legacy.py:210`
> `    shares the same query - out of scope,`
> `    but will break`

Compare against `course/tickets/PROJ-142/02-interrogation.md` and `04-touchpoints.md`. The wording will
differ; the shape and the `(!)` line must not.

**The line to say:** *every question carries the guess it would otherwise have made silently,
which is why each one takes seconds to answer instead of a meeting. And then it stopped. An
agent that answers its own questions hands you a confident artifact built on guesses you can no
longer see.*

**Restore.** `rm -f specs/PROJ-142.answers.md specs/PROJ-142.touchpoints.md`

**Gotchas.** If a take answers its own questions or skips the stop line, keep it: that is a
finding about the host, and it is the one thing `LEARN.md` tells a learner to watch for. If no
take finds `legacy.py`, narrate the reveal from `04-touchpoints.md` rather than re-prompting
towards it.

---

## D14 · The out-of-scope section

**Chapter 1.3. Roughly 60 seconds.** `spec-draft`, from three inputs and never the ticket alone.
Film straight after D13, because it consumes D13's files.

**Beat 1 — the refusal.** Run `/spec-draft PROJ-142` while every `answer:` is still empty. It
refuses and writes nothing — the behaviour the `spec-draft-refuses-unanswered` eval case holds it
to.

**Beat 2 — a human answers.** Fill the five answers on camera from
`course/tickets/PROJ-142/03-answers.md`. About four minutes in real life; speed-ramp it.

**Beat 3 — the draft.** Run it again. `specs/PROJ-142.md`, a filled copy of `course/templates/spec.md`.
The shot is two sections:

> `## Acceptance criteria` — each with a `measured how:` line and a `from:` answer
> `## Out of scope` — non-empty, and the legacy report is on it

Compare against `course/tickets/PROJ-142/05-spec.md`.

**The line to say:** *if you could not write an assertion for a criterion, rewrite it. And out of
scope is the field that stops the agent cheerfully building the three things nobody asked for.
This file goes into a pull request before a line of code exists — the cheapest place there is to
disagree.*

**Restore.** `rm -f specs/PROJ-142.md specs/PROJ-142.answers.md specs/PROJ-142.touchpoints.md`

**Gotchas.** If beat 1 drafts anyway, that is a real failure of the stop condition: keep it and
say so. Do not paste the answers file from `course/tickets/` wholesale — the human beat is typing them.

---

## D15 · The reviewer's read order

**Chapter 3.3. Roughly 50 seconds.** `pr-brief` describes a pull request and never judges it.

**Setup.** The lab 05 pull request, which has everything a brief needs: `spec.md`,
`touchpoints.md` and `pr.diff` in `course/labs/05-review-a-planted-pr/`. Its ticket is `LAB-105`, so the
output lands in a gitignored `specs/LAB-105.pr.md`.

**Beat 1 — run it.** `/pr-brief` against the lab 05 spec and diff.

**Beat 2 — the four aids.** Scroll the output, in the order the contract fixes:

> `## Description` · `## Acceptance criteria` (unticked) · `## Read order` · `## Candidate untested paths`

Compare against the shape of `course/tickets/PROJ-142/07-pr-body.md`.

**Beat 3 — what is not there.** No verdict, no "looks good", no risk score. *Catching itself
forming a verdict* is this skill's stop condition, because a brief that reviews destroys the
fresh-context property the next stage — D6 — depends on.

**The line to say:** *the read order is the biggest single improvement on a large diff, and
diffs are half again as big as they were. The human starts oriented instead of
reverse-engineering intent from the diff.*

**Restore.** Nothing — `specs/LAB-*` is gitignored.

**Gotchas.** If a take editorialises, keep it only if it then stops; a brief that judges and
carries on is the anti-pattern, not the demo. Film before D6, which reviews the same pull
request in a fresh session.

---

## D16 · A finding becomes a rule

**Chapter 4.1. Roughly 60 seconds.** The harvest loop, walked file to file. It needs no agent: the
loop already ran, and every hop is committed.

**Beat 1 — a human caught it.**

```
sed -n '17,19p' course/tickets/PROJ-142/08-review.md
```

> `### 1 · blocking: the legacy report is now unbounded`

**Beat 2 — the harvest proposed a rule, and stopped.** Scroll `course/tickets/PROJ-142/10-harvest.md` to
`### a custom rule` and the closing `[ stopped - a human commits these ]`.

**Beat 3 — the ledger remembers it, and the rule says where it came from.**

```
grep -n "PROJ-142" harvest/ledger.md | head -1
grep -n "origin" .semgrep/unbounded-export-query.yml
```

> `origin: PROJ-142 review, finding 1`

**Beat 4 — the rule catches it the second time.** In `tooling/myapp/service/reports/legacy.py:210`,
delete the `chunk_size=LEGACY_PAGE_SIZE` keyword — the tidy-up the docstring above it warns
against — then:

```
semgrep scan --config .semgrep/unbounded-export-query.yml myapp --error --metrics=off; echo "exit=$?"
```

> `210┆ query = service.build_export_query(account_id)`
> `exit=1`

**The line to say:** *a human caught this once, in a review. Now a machine catches it every time,
and the rule carries the name of the review that found it. A correction captured once beats a
correction made well every week.*

**Restore.** `git checkout -- tooling/myapp/service/reports/legacy.py`

**Gotchas.** Film last in session C. Optionally run `/harvest` live on D6's review first: the
proposals will differ from `10-harvest.md`, and the stop line must not.

---

## D17 · Reading a repo it has never seen

**Chapter 2.2. Roughly 50 seconds.** `stack-profile`, the step before any gate gets written.

**Setup.** A scratch clone of a small public repository **outside this tree** — one the agent has
not seen and nobody has primed. Install the skill there with
`./tooling/scripts/sync-skills.sh --print stack-profile`, pasted, rather than linking this repository.

**Beat 1 — run it.** `/stack-profile`. It writes `gates/stack-profile.md` in the scratch repo.

**Beat 2 — the evidence.** Scroll `## Stack`, `## Toolchain`, `## Candidate gates`. Every claim
carries `evidence: <path>:<line>`. Open one cited line on camera and show it is real.

**Beat 3 — the mismatches, and the stop.** `## Mismatches` — what the repo's own docs claim against
what its files show — then `[ stopped - waiting for a human ]`.

**The line to say:** *it does not write a single gate yet. It tells you what it thinks your stack
is, with a citation for every claim, and waits for you to correct it, because a generated config
built on a wrong guess about your toolchain is worse than none.*

**Restore.** Delete the scratch clone.

**Gotchas.** If a citation does not resolve when opened, keep the take and say so — that is the
reason the human step exists. If it finds more than two ecosystems it stops early by design;
pick a smaller repository rather than fighting it.


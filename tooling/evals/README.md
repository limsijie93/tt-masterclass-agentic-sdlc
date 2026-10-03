# tooling/evals/

`tooling/scripts/lint_skills.py` proves the skills' **declared** contracts fit together — it reads
`## Output contract` as text. Until this directory existed, nothing ever executed a skill, so
nothing checked that a skill **honours** the contract it declares. A skill whose Procedure was
nonsense passed all ten of the linter's checks.

> The linter proves the contracts fit together. An eval proves a skill keeps its own.

## Read this first: the sabotage the suite must fail

```
EVAL_ENGINE_CMD=true python3 tooling/tools/run_evals.py --all      →  0/7 passed
```

A no-op engine must fail **every** case. That is not a formality, because the most valuable
cases here assert a **refusal** — "given an unanswered question, the skill did not write a
spec" — and a harness that never invoked the engine passes that trivially.

This is the `semgrep --test --config` false green from [`.semgrep/README.md`](../../.semgrep/README.md)
reincarnated in a new place, and it looks like success. Run it and read the output:

```
✓ did_not_write: specs/EVAL-102.md was correctly not written     ← passes on a no-op engine
✗ output_mentions: output omits 'EVAL-102'                       ← catches it
✗ output_mentions: output omits 'answer'                         ← catches it
  FAIL
```

So **every negative assertion is paired with a positive companion** a no-op engine cannot
produce, and `tooling/tests/test_evals_are_wired.py` fails the build if a negative control lacks one.

## What may be asserted, and why the line is there

Model output is non-deterministic, and this repo says three separate times that a flaky gate
destroys trust in about a week. Every assertion in
[`tooling/tools/eval_assertions.py`](../tools/eval_assertions.py) is therefore a property of the
output's **shape** or of the skill's **stopping behaviour** — never of its prose.

| Class | Example |
|---|---|
| Existence and arity | exactly `{answers.md, touchpoints.md}` were written |
| Cardinality bounds | at most five questions; nought to three findings |
| Structural invariants | every question carries both `blocks` and `assumes` |
| **Refusal behaviour** | given an unanswered question, no spec exists |
| Citation resolvability | every `path:line` names a real file with that many lines |
| Verbatim inclusion | criteria "quoted verbatim" — so verbatim is checkable |
| Banned tokens | no `LGTM`, no `%`, no "performant" in a criterion |
| Cost | under the case's declared ceiling |

**Refusal behaviour is the highest-value class**, because a stop condition is this repo's actual
product and refusing is where models actually fail.

What may **not** be asserted: exact question text; *which* five questions were chosen; the
ranking order of findings; whether a finding is correct; word counts.

**And no LLM-as-judge grader.** Stated explicitly so nobody adds one in month two thinking it
was an oversight: a non-deterministic grader over a non-deterministic output is two coin flips,
and when it fails you cannot tell whether the skill regressed or the judge did.

## The fixture problem

The tempting design is to feed the worked ticket in and compare the output to
`course/tickets/PROJ-142/02-interrogation.md`. That is non-deterministic **and** tautological — it
asserts the model reproduces one hand-polished past output. Apply this repo's own test from
[`09-tests-that-lie.md`](../../course/tickets/PROJ-142/09-tests-that-lie.md): *delete the thing under
test, does the check still pass?*

Three rules follow:

1. **A case's expected outcome is a list of properties, never a file.** Mechanised — a case
   mentioning `course/tickets/PROJ-142` fails `tooling/tests/test_evals_are_wired.py`.
2. **The codebase under test is this repository, and each ticket is a real gap in it.** The
   README names the absence of application code, but these skills need *code*, not
   *application* code — and `tooling/scripts/`, `tooling/tools/` and `tooling/tests/` are real and citable by line. Each
   ticket is written for the eval, by no skill, so there is nothing to reproduce, and
   `citations_resolve` becomes a genuine hallucination check rather than a formality.
3. **The worktree is sanitised.** `sanitise_worktree()` deletes `course/tickets/PROJ-142/` and `tooling/evals/`
   before the engine sees anything, so the answer key is physically absent. Unit-tested, so
   removing it is a pytest failure rather than a review miss.

## The invocation

No default is baked into the harness. `EVAL_ENGINE_CMD` is required, and an unset value exits 1
with a pointer here — a wrong default would silently run the wrong thing, and this repo does not
ship unverified commands.

```bash
export ANTHROPIC_API_KEY=...
export EVAL_ENGINE_CMD='claude --bare -p --add-dir . \
  --allowedTools "Read,Grep,Glob,Write,Edit" \
  --permission-mode acceptEdits \
  --output-format json'

python3 tooling/tools/run_evals.py --all
```

Every flag is there for a reason, and one of them is a trap:

- **`--bare`** skips auto-discovery of hooks, plugins, MCP servers, auto memory and `CLAUDE.md`,
  so the run does not depend on what is in the operator's `~/.claude`. That is what makes a CI
  result mean the same thing on two machines. It also means the run does not fire this repo's own
  guards, which is correct — the guards are not under test here.
- **`--add-dir .`** is the part you cannot drop. **`--bare` also skips skill discovery**, which
  would leave the eval running with none of the skills it is supposed to be testing and quietly
  measuring nothing. `--add-dir` is the documented exception: bare mode loads skills from a named
  directory's `.claude/skills/`. Ours are there, symlinked to `.github/skills/`.
- **`--allowedTools` with no `Bash`.** The eval agent must write files, so it cannot be
  read-only — but it does not need a shell, and
  [`read-only-explorer.md`](../../.claude/agents/read-only-explorer.md) already wrote the argument:
  `>` writes, and so do `tee`, `sed -i`, `python -c` and `git checkout`.
- **`--bare` does not use subscription login**, so `ANTHROPIC_API_KEY` must be set.
- **`--output-format json`** carries `total_cost_usd`, which the harness records per case.

A case's prompt names its skill explicitly (`/spec-draft`), which is available in `-p` mode.
These cases test whether a skill **honours its contract**, not whether its description wins the
trigger — that second thing is real and is not deterministically testable, so it is not claimed
here.

**Verified against the published CLI documentation, not by running it.** One real run will
confirm the flags and replace the cost estimate below; until then treat both as provisional.

## Cost

Order of magnitude, Sonnet-class, stated so it can be corrected rather than left as a guess:

| | per case | 6-case suite | authoring (6 × 5 reps) | weekly + ~2 on-change |
|---|---|---|---|---|
| Sonnet-class | ~$0.20–0.50 | ~$1.50–3 | ~$10–15 one-off | ~$10–20/month |

The harness records the engine's reported `total_cost_usd` per case, so the first real run
replaces this table.

**We do not pin a model, and that is a decision rather than an omission.** The obvious advice is
to pin one, and the reason behind it is sound: changing the model changes the thing under test.
But this material is taught to people running whatever their employer bought, and a suite that
only means something on one model measures a configuration nobody in the room has.

So the pin is replaced by a **record**. A case claiming `5/5` carries both a `measured:` date
and a `model:`, and `tooling/tests/test_evals_are_wired.py` fails the build without both. An
unattributed `5/5` is worse than `unmeasured` — `unmeasured` tells you what you do not know, and
a bare number does not.

```
stability: 5/5
measured: 2026-10-01
model: <the exact identifier the run used>
```

**Opus 5.5 is the teaching default** — what the lecture demonstrates on and what the numbers in
this directory should be read against unless a case says otherwise. It is a default, not a
requirement: run the suite on yours, record which, and the result is comparable because the
provenance travels with it.

The cost table above is Sonnet-class, which is the floor rather than the default. A
frontier-model run costs several times it.

## When it runs, and one honest gap

`.github/workflows/evals.yml`: weekly, `workflow_dispatch`, and on pull requests that touch
`.github/skills/**`, `.claude/settings.json`, `tooling/tools/guard_*.py`, `AGENTS.md` or `tooling/evals/**`.

Not every PR — too expensive, and a non-deterministic suite running constantly trains people to
ignore red, which is the same failure as forty review comments. Weekly rather than nightly
because the thing under regression test is prose that changes weekly at most.

**The gap:** `schedule:` only fires on the default branch, and none of this stack is merged yet.
The weekly run will not fire until it lands.

## It reports; it does not gate

The suite's **structure** blocks, via `tooling/tests/test_evals_are_wired.py` in tier 1: every case names
a real skill, every assertion exists, no case expects a worked-example artifact, every case
records `stability: 5/5`, at least one is a negative control and each has a positive companion.
That costs nothing and never flakes.

The **results** report. Three reasons they must not gate:

1. An eval *is* an agent run, and `code-review/SKILL.md` establishes that the same pull request
   reviewed twice can produce different verdicts. Gating on it inverts the ladder Part 3 spends
   a segment building.
2. It needs a secret, so it can never pass on a fork. A required check that cannot pass on a
   fork is a broken gate.
3. It costs money, so re-run-until-green has a bill attached.

The playbook's "gate configuration changes on eval results" is honoured with a **human** as the
gate: the job writes a pass-rate table to the step summary, and the pull request template asks
for the before-and-after rate when a skill body changes. Tier 3, where non-deterministic
evidence belongs.

## Seven cases, and the two rules that keep it small

Twenty to fifty cases on day one would ship half-authored. The starting set is chosen for
load-bearingness rather than coverage:

| Case | What it pins |
|---|---|
| `spec-draft-refuses-unanswered` | **the negative control** |
| `spec-interrogate-grounded` | the full output contract, and citation resolvability |
| `spec-interrogate-ungroundable` | a degenerate stop condition |
| `spec-draft-happy` | section order, out-of-scope minimum, hazard carry-forward |
| `pr-brief-verbatim` | verbatim quoting, and banned verdict language |
| `code-review-clean` | cardinality, at most one blocking, verbatim footer |
| `build-slice-refuses-unassertable` | **the second negative control** — a criterion with no assertion stops the work |

**Stability.** Every case must be run **5× unchanged** and pass 5/5 before its result is
trusted. A case that passes 4 times in 5 is a lottery, not an eval. Five runs **on one model** —
mixing models inside a stability run measures neither.

**No case has been run yet.** Every case reads `stability: unmeasured`, because no key is
configured in this repository and asserting a measurement nobody took would be exactly the
aspirational content this repo warns about — in a directory about verification, which would be
worse. `unmeasured` is not a loophole: a test permits only `5/5` or `unmeasured`, and claiming
`5/5` requires a `measured:` date in the same file. So the claim cannot be made without saying
when it was made.

**Authoring runs are therefore a prerequisite, not a formality.** Until they happen, this suite
is a harness and a set of hypotheses about what these skills do. The harness is verified — a
no-op engine scores zero, and every structural rule is sabotage-tested. The *cases* are not.

**Growth rule.** Every tier-2 finding that a skill's contract should have prevented becomes a
case — the local form of "every incident becomes a permanent eval", tied to an artifact this repo
already produces. `harvest/ledger.md` is where the second sighting gets counted.

**Retirement rule**, which nobody writes and which is the only thing that caps the bill: a case
whose property becomes deterministically checkable by `lint_skills.py` is **deleted**, because
the cheaper check subsumes it. That is *never spend a tier's attention on something the tier
below could have caught*, applied to evals.

## Not covered yet

`stack-profile` and `gates-draft`. Their output is a generated config — the least assertable and
most expensive thing in the set — and `gates-draft` needs a human-corrected profile as input.
Named here so the absence reads as a decision.

**And `build-slice`'s happy path, which this harness cannot run at all.** The invocation above
allowlists `Read,Grep,Glob,Write,Edit` and deliberately no `Bash`, on the argument that the eval
agent must write files but does not need a shell. `build-slice` runs the tests and commits — its
procedure is *confirm the test fails*, then *run the deterministic checks*, then *commit named by
the criterion* — so under this invocation it cannot reach step 3, let alone step 6.

That is a real limit and not a gap to paper over. Two ways out, neither free:

1. **A second invocation for this one skill**, with `Bash` allowlisted and the case run in the
   sanitised worktree it already gets. The worktree is disposable, so the blast radius is
   bounded — but the suite would then have two engine commands, and "what does a green run
   mean" stops having one answer.
2. **Assert the artifact and not the act.** Give the case a repository where the tests already
   pass, and check the shape of `specs/<T>.drift.md` rather than whether a commit exists. Cheap,
   and it tests the reporting half while leaving the half that matters unmeasured.

`build-slice-refuses-unassertable` sidesteps both, which is why it is the case that exists: an
unassertable criterion is caught at step 1, before any shell is needed. The stop condition is
reachable read-only, and the stop condition is the product.

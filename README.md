# Agentic SDLC — companion repo

Files from the lecture **Agentic SDLC: Specs → Quality → Review**, by Si Jie Lim.

### → Just watched the lecture? Read [**LEARN.md**](LEARN.md) instead.
### → Want one page to pin up? [**docs/reference-card.md**](docs/reference-card.md).

It is the hour after: one ticket end to end, one skill you can try without installing anything,
a lab with your hands on the keyboard, and two deliberately-wrong files to check yourself
against. **This** document is the reference — what each file is, why it is shaped that way, and how to adopt it. Come back to it
when you want it in your own repository.

> **Everything produced in the lecture is a file in this repo, reviewed like code.** That is
> what makes it a team practice instead of a personal habit.

## What's yours

| | Folder | What you do with it |
|---|---|---|
| **Start** | [`LEARN.md`](LEARN.md), [`docs/reference-card.md`](docs/reference-card.md) | Read first: which path to take, and the one-page summary |
| **Do** | [`labs/`](labs/) | The hands-on labs. `python3 tools/lab.py` lists them, then `start`, `check`, `solution` |
| **Read** | [`example/`](example/) | Two worked tickets, every step as a file, numbered in reading order |
| **Run** | [`docs/demos.md`](docs/demos.md) | Every lecture demo, with the exact commands, so you can reproduce it |
| **Copy into your repo** | [`.github/skills/`](.github/skills/), [`templates/`](templates/), [`examples/`](examples/) | The skills, the stack-neutral file shapes, and those shapes filled in for Python and TypeScript |
| **Leave alone** | `myapp/`, `tools/`, `tests/`, `scripts/`, `evals/`, `.semgrep/`, `harvest/`, config files | The practice app the labs break, and the machinery that checks this repo. Read it freely; you don't edit it for a lab |

Your own work (`pruned.md`, `yours.ini`, `test_yours.py`, `specs/LAB-*`, `reviews/LAB-*`, each
`report.md`) is gitignored, so it never collides with an update.


## The 90-minute path, if you only do one thing

Three pull requests, each under an hour:

1. Run [`stack-profile`](.github/skills/stack-profile/SKILL.md) on your repo, correct what it
   got wrong, then [`gates-draft`](.github/skills/gates-draft/SKILL.md). You get a baselined
   contract, hook config and `AGENTS.md` Commands block for **your** stack, in `gates/draft/`.
2. Prune the generated `AGENTS.md` below 60 lines by hand — the pruning is the part that
   matters. Put a name in the H1 and the path in `CODEOWNERS`.
3. Add `tier1` to your branch's required status checks. Only `tier1`.

Prefer to copy rather than generate? [`templates/`](templates/) has the stack-neutral shapes and
[`examples/`](examples/) has them filled in for Python and TypeScript. Read
[`templates/README.md`](templates/README.md) first — turning these on repo-wide on day one is how
the initiative dies in week two.

## Honestly: what runs, and what is a template

There **is** an application here now, and it is deliberately small. `myapp/` exists to be
broken in five specific ways, and for nothing else: no auth, no migrations, no deployment, no
front end, one SQLite table and a decoy. Read this before cloning, so nothing below is a
surprise.

It was not here for most of this repo's life, and the change earned itself in the first hour.
Turning the real tier-1 stack on against real code immediately found that
`.semgrep/unbounded-export-query.yml` matched **none** of the actual call sites while passing
its own unit tests, and that a `layers` contract does not forbid a higher layer skipping a
lower one — so the architecture rule the worked example is built on was not being enforced.
Both had been green for weeks. Neither is findable without code to run against.

| Runs green in this repo | Illustrative template |
|---|---|
| `myapp/` — the app, with the full tier-1 stack: ruff, mypy strict, `lint-imports`, semgrep, tests | `templates/*` — written for the same fictional service, stack-neutral |
| `scripts/` and `tools/` — with tests, ruff-clean, mypy-strict-clean | `examples/python/*`, `examples/typescript/*` — two fills of those shapes |
| `.semgrep/` — the rules have their own unit tests, and now real code to fire on | |
| `.importlinter` — three contracts, and a test proves the third one bites | |
| `.pre-commit-config.yaml` — this repo's own gates | |
| `.github/workflows/review.yml` — language-agnostic; it runs whatever your pre-commit config declares | |

`example/PROJ-142/*` are still artifacts rather than code — but every `path:line` they cite now
resolves, and `tests/test_example_consistency.py` fails if one stops resolving. They were
consistent with each other before; they are correct now.

One file is named to *avoid* being picked up automatically: the skill template is
`SKILL.template.md`, not `SKILL.md`, because anything named `SKILL.md` under a skills directory
registers as a live skill.

`templates/importlinter.example.ini` used to be the second such file — it would have failed on
every commit as a root `.importlinter`, because there was no `myapp` for `lint-imports` to
import. That is no longer true, and the root [`.importlinter`](.importlinter) is now real and
enforced. The template stays, because it carries the baseline-and-ratchet commentary an
established repo needs and the live file has no violations to baseline.

## The review ladder, and the files that implement it

| Tier | What | Verdict | Where it lives |
|---|---|---|---|
| 0 · Pre-action | guards that see an edit before it is written | **asks**, or blocks | [`tools/guard_test_edits.py`](tools/guard_test_edits.py), [`tools/guard_protected_paths.py`](tools/guard_protected_paths.py), via [`.claude/settings.json`](.claude/settings.json) |
| 1 · Deterministic | format, lint, types, architecture contract, custom rules, tests | **blocks** | [`.pre-commit-config.yaml`](.pre-commit-config.yaml), [`review.yml`](.github/workflows/review.yml) job `tier1` |
| 2 · Agent judgment | a fresh-context pass against the spec | **comments** | [`code-review`](.github/skills/code-review/SKILL.md), `review.yml` job `tier2` (engine not wired — see below) |
| 3 · Human judgment | domain rules, authorization, whether it should exist | **decides** | [`pull_request_template.md`](.github/pull_request_template.md), [`CODEOWNERS`](.github/CODEOWNERS) |

**Tier 2 is the one rung that does not run here, and saying so is the point.** The `tier2` job in
`review.yml` is real — least privilege, `continue-on-error`, no `pull_request_target`, and a clean
skip when no key is configured — but the line that would invoke an engine is commented out, because
this repo ships no key and a command nobody ran is exactly the aspirational content it warns
against. What is committed is the *contract* (`code-review/SKILL.md`) and the *wiring*; swapping in
your engine is one uncommented line. Until you do, the ladder degrades the way it is supposed to:
tier 1 still blocks, tier 3 still decides.

Never spend a tier's attention on something the tier below could have caught — and that now
extends downward: a guard is cheaper than a commit hook is cheaper than CI. Never invert the
verdicts either: an agent as a merge gate is non-deterministic, and a gate that flakes destroys
trust in about a week.

That is the argument for the *ordering*. The argument for there being four layers rather than one
good one is the **Swiss Cheese Model**: capability gaps are unpredictable and are not correlated
between layers, so a hole in any single one is expected and only the stack is reliable. It is
also why no tier is allowed to be excused as redundant. Sources for both claims, including the
measured non-determinism, are in [`docs/citations.md`](docs/citations.md).

### Tier 0 exists because of a rule we were not keeping

"Do not modify a test in order to make an implementation pass" appeared in eight places in this
repo and was enforced in none of them — in a repo arguing that a standard a machine cannot check
is a preference. So it was a preference.

Making it executable required finding the observable it was actually about. All eight statements
hinge on *"in order to"*, which is a claim about **intent**, and no guard observes intent. The
checkable version is: **the edit weakens an assertion.** That reframe is the interesting part —
making a rule checkable tells you what the rule actually was.

It does not block editing tests, it blocks *weakening* them, so test-first still works: create a
file, add a failing test, edit production code. None of that weakens an assertion. The only thing
you cannot do silently is turn a red test green by editing the test.

**It ships in log mode.** `GUARD_MODE=log` is the default: it reports and blocks nothing, because
[`templates/README.md`](templates/README.md) tells adopters to measure for a week before
enforcing and this is our own gate. Flip to `enforce` in a PR carrying the observed counts.

**The second guard protects the first.** `guard_protected_paths.py` refuses agent edits to
`.claude/settings.json` and `tools/guard_*.py`, because a guard the agent can disable is not a
guard — the same argument the read-only agent makes about its own allowlist, one level up.

It blocks outright rather than asking, and it does *not* ship in log mode. Both look
inconsistent with the guard above and aren't: a pre-action guard never sees a human's editor, so
a false positive here costs a person nothing, and there is no existing backlog to measure
because it is a three-entry deny list on files with no violations. "Measure before enforcing" is
advice about baselines, not a ritual.

The list is three entries and stays that way. **Not** `.github/workflows/` and **not**
`.pre-commit-config.yaml` — this repo's own layers edit both constantly, and a protected list
covering files the team edits daily is the mypy trap: the first legitimate change gets the guard
deleted by someone in a hurry. A test asserts the list has not grown.

**The honest limit, and it is large.** These see the edit tools. They do not see a shell. `cat >`,
`sed -i`, `python -c`, `git checkout` are all invisible to them and all visible in the diff. That
is the same hole the read-only agent names when it refuses to allowlist a shell — and it is why
these are *guards* and not *controls*. The control is admin-set settings a developer cannot
override — `templates/managed-settings.example.json`, with the paths, the three locks, and the
tension it creates, in [`templates/README.md`](templates/README.md).

That tension is worth naming here too: **`allowManagedHooksOnly: true` stops this repo's own
committed guards from running**, because they live in a project source and that is precisely what
the lock excludes. The control that makes a guard trustworthy is the control that switches off a
guard a team committed to its own repo. Resolve it deliberately; the template says how.

**Portability, one level down from the agent files.** The decision is a stdlib script that names
no host. The trigger — `PreToolUse`, `permissionDecision`, exit 2, `$CLAUDE_PROJECT_DIR` — is one
host's vocabulary and lives only in `.claude/settings.json`. There is no Copilot or Cursor
equivalent to ship, and shipping a fake one would be the worst possible bug here. But the same
script is also a `pre-commit` hook, which is host-agnostic — so the rule lands on **every** host
and only the timing differs. Write time on one, commit time on the rest.

## The skills

Chained, and the contract between them is a **file path**, not a conversation — every skill
declares its upstream artifact as a required input and stops if it is missing.

`build-slice` is the newest and closes the one gap the chain had: every other step produced a
file, and the step where code actually gets written produced commits. Which mattered for a
reason narrower than tidiness — `code-review` has to answer *what did this touch that the plan
never mentioned?*, and with no record it infers drift from the diff. That finds a file appearing
where the spec did not expect one. It does not find the file the spec **did** expect, changed in
a way nothing predicted, which in the worked ticket is exactly what broke.

```
ticket → spec-interrogate → answers + touchpoints → [STOPS for a human]
                          → spec-draft            → the spec
                          → build-slice           → the code, and the drift it caused
                          → pr-brief              → the reviewer's aids
       [FRESH SESSION]    → code-review           → at most 3 findings
                          → harvest               → proposals + a ledger entry
```

Until `harvest` existed the chain ended there: `reviews/<T>.review.md` was consumed by nothing,
so every ticket was individually faster and nothing accumulated. `harvest` reads the review and
routes each finding to a permanent home — or logs it, because its rules are all about repetition
and a first sighting is logged rather than proposed. `harvest/ledger.md` is the memory that makes
a second sighting countable, and it is the one skill whose input is its own prior output.

It proposes; a human commits. It has no write path into `AGENTS.md`, the spec template, a config
file, or a skill, and its stop conditions say to halt if it finds itself editing one — an agent
that edits the rules it runs under has removed the reason those rules are trustworthy.

| Skill | Segment | Run it |
|---|---|---|
| [`stack-profile`](.github/skills/stack-profile/SKILL.md) | 06 | Once per repo, before writing gates |
| [`gates-draft`](.github/skills/gates-draft/SKILL.md) | 06 | After the profile is corrected |
| [`spec-interrogate`](.github/skills/spec-interrogate/SKILL.md) | 03 | Before drafting anything |
| [`spec-draft`](.github/skills/spec-draft/SKILL.md) | 04 | Once the questions are answered |
| [`build-slice`](.github/skills/build-slice/SKILL.md) | 07 | After the spec, one acceptance criterion at a time |
| [`pr-brief`](.github/skills/pr-brief/SKILL.md) | 10 | Opening a PR, in the session that wrote the code |
| [`code-review`](.github/skills/code-review/SKILL.md) | 09 | **In a fresh session.** Never the one that wrote it |
| [`harvest`](.github/skills/harvest/SKILL.md) | 12 | After the review, before the branch is deleted |

### Installing them, or not

**Paste-first.** Every skill body works pasted into any assistant, with nothing installed.
Installing is an optimisation:

```bash
./scripts/sync-skills.sh --print spec-interrogate | pbcopy
```

To install, one canonical copy under `.github/skills/` is linked into every other host's path:

```bash
./scripts/sync-skills.sh            # this project: .claude/, .cursor/, .agents/
./scripts/sync-skills.sh --user     # also ~/.claude/ and ~/.agents/, for any repo
./scripts/sync-skills.sh --check    # drift detection, for CI
./scripts/sync-skills.sh --copy     # real copies, for Windows without Developer Mode
```

Six skills cost roughly 240 tokens of always-loaded context — the name and description only.
Bodies load when triggered; `references/` files load when read.

**Language lock, and where it is unavoidable.** An executable check cannot be
language-agnostic — parsing the language is what makes it checkable. So the split is: the
*decision* about what to enforce is a skill (`gates-draft`), and the *executable* is its
generated output. `templates/` names no language; `examples/` holds one fill per ecosystem;
[`gates-by-stack.md`](.github/skills/gates-draft/references/gates-by-stack.md) maps between
them.

Two things turn out to be more portable than they look, and one less. `pre-commit` is not a
Python tool — it manages Node, Go, Rust and Ruby hooks, and it is why tier 1 ports at all. And
`semgrep` spans 30+ languages. But **one semgrep rule cannot span two of them** when its
patterns rely on language-specific syntax: declaring `languages: [python, typescript]` silently
breaks the Python negation and starts flagging correct code. Measured, not assumed — the numbers
are in [`.semgrep/README.md`](.semgrep/README.md).

**One limit, stated rather than hidden.** Skill bodies are portable and
`scripts/lint_skills.py` enforces it (no host names, no absolute paths, declared inputs, fixed
output shape). Agent *definitions* are not portable, because a permission boundary is made of
one host's tool names — hence two `read-only-explorer` files. Cursor's restricted mode is
configured in its UI with no committed equivalent, so there is deliberately no
`.cursor/agents/` file here.

**Which is why a skill's permissions arrive in two halves.** The same tension applies to the
skills themselves: the repository argues for permission boundaries and for portable bodies, and
a permission boundary is spelled in host vocabulary the body is not allowed to use. So the
capability claim is prose in `## Inputs required` — *reads files; writes one file; runs no
commands* — and the enforceable allowlist is `allowed-tools` in the frontmatter, where the ban
does not reach. Prose is the contract and travels; frontmatter is one host's fill and is
expected to be rewritten per host, exactly like the `templates/` and `examples/` split used
everywhere else here. `lint_skills.py` check 11 compares them, so the two halves cannot drift:
a body claiming it runs no commands beside an allowlist granting a shell fails the build.

Seven of the eight skills declare no shell. `build-slice` is the exception and the reason is its
procedure — it has to confirm a test is red before implementing, and that is not something a
skill can do by reading.

## The labs

[`labs/`](labs/) is the keyboard time. Six, about two and a half hours, and **the first three need no
agent, no API key and no account** — which is the ordering decision that matters, because a
learner who meets "you will need a key" at lab 01 stops at lab 01.

```
make setup && source .venv/bin/activate
python3 tools/lab.py
```

| # | Lab | Segment | Needs |
|---|---|---|---|
| 01 | Prune the context file | 05 | nothing |
| 02 | Make the gate actually bite | 06 | nothing |
| 03 | The test that lies | 10 | nothing |
| 04 | Interrogate a real ticket | 03 | an agent |
| 05 | Review a planted pull request | 09 | an agent |
| 06 | Implement one criterion | 07 | an agent |

**A lab is an eval case with a human as the engine.** `tools/lab.py` is `tools/run_evals.py`
with the one call to `$EVAL_ENGINE_CMD` replaced by printing the brief and waiting — same file
format, same frontmatter parser, same assertions. What may be asserted about a skill's output
turns out to be exactly what may be asserted about a learner's, for the same reason: shape and
stopping behaviour are checkable and prose is not.

Marking is the ladder again — machine blocks, a key comments, you decide — and the checker
holds itself to the two rules in [`labs/README.md`](labs/README.md). The first one cost
something: an untouched checkout scored **3/7** on lab 01 the first time, because `max_lines`
and `banned_tokens` are both vacuously true of a file nobody wrote. Eight assertions carry an
existence guard now.

## The worked ticket

**If you are here to learn rather than to adopt, [`LEARN.md`](LEARN.md) walks this in order with
what to notice in each file.**

[`example/PROJ-142/`](example/PROJ-142/) is one ticket from vague report to reviewed pull
request, in reading order — including the bloated `AGENTS.md` draft that
`templates/AGENTS.md` was pruned *from*, so the pruning is a diff rather than a claim.

**Two files there are deliberately wrong.** One review finding is a false positive and one test
verifies nothing; the lecture polls the room on both. `example/PROJ-142/AGENTS.md` tells an
agent not to correct them, which matters because the first thing most people do with this repo
is point an agent at it.

## Do the skills still do what they say?

`scripts/lint_skills.py` proves the skills' **declared** contracts fit together. Nothing
executed a skill until [`evals/`](evals/) existed, so nothing checked that a skill **honours**
the contract it declares — a skill whose Procedure was nonsense passed all ten checks.

> The linter proves the contracts fit together. An eval proves a skill keeps its own.

Assertions are properties of the output's shape or the skill's stopping behaviour, never of its
prose, because a flaky gate destroys trust in about a week. The highest-value ones assert a
**refusal**: given an unanswered question, no spec exists.

Which creates the trap the suite is built around, and it is worth running yourself:

```
EVAL_ENGINE_CMD=true python3 tools/run_evals.py --all      →  0/7 passed
```

A no-op engine passes `did_not_write` trivially. So every negative assertion is paired with a
positive companion a no-op engine cannot produce, and a test fails the build if one is missing.
That is the `semgrep --test` false green from [`.semgrep/README.md`](.semgrep/README.md) in a new
place, and it looks like success.

**No model is pinned, deliberately.** The obvious advice is to pin one — changing the model
changes the thing under test — but this material is taught to people running whatever their
employer bought, and a suite that only means something on one model measures a configuration
nobody in the room has. The pin is replaced by a record: a case claiming `5/5` carries both a
`measured:` date and a `model:`, and a test fails the build without both. **Opus 5.5 is the
teaching default**, not a requirement.

Seven cases, and **none of them has been run yet** — every one reads `stability: unmeasured`,
because no key is configured here and claiming a measurement nobody took would be the
aspirational content this repo warns about, in a directory about verification. A test permits
only `5/5` or `unmeasured`, and `5/5` requires a `measured:` date. So the harness is verified and
the cases are hypotheses until someone runs them.

The suite **reports**; it does not gate. Its *structure* blocks, in tier 1, at no cost and with
no flake. Full reasoning, the fixture-tautology problem, the verified invocation and the cost
estimate are in [`evals/README.md`](evals/README.md).

## This repo checks itself

The thesis applied inward. `make tier1`, or:

```bash
python3 scripts/lint_skills.py --check-agents   # portability rules + the skill chain
./scripts/sync-skills.sh --check                # host symlinks match canonical
semgrep test .semgrep/                          # the rules' own unit tests
python3 tools/check_commands_sync.py            # AGENTS.md Commands == the gate
pytest -q                                       # incl. the example's cross-file consistency
```

Two of those earned their place by failing on their first run. `check_commands_sync.py` found
`semgrep` enforced by the pre-commit template but missing from `AGENTS.md`. `lint_skills.py`
caught `code-review/SKILL.md` reaching a `references/` file from its procedure, which breaks
paste-first.

And `semgrep test .semgrep/` is written that way on purpose: the more obvious
`semgrep --test --config .semgrep/ .semgrep/` reports success even with a deliberately
sabotaged fixture. See [`.semgrep/README.md`](.semgrep/README.md).

## Demos

[`docs/demos.md`](docs/demos.md) maps every recording to its lecture segment and the exact
commands that produce it. All twelve have written, verified beats; none of them is filmed.


## Not here yet

Named so the gaps read as decisions:

- **Governance** (segment 11) — the shape is now `templates/governance.example.md`: visibility
  before limits, four adoption metrics chosen so that gaming one moves another the wrong way, and
  the trust boundary. What is still absent is a **filled** one, and deliberately: the vendor rows
  are a purchasing decision and the thresholds need a month of measurement, so a default here would
  be the aspirational content this repo warns about, in the file a manager is most likely to copy.
- **Per-host install guides** — largely obviated by `sync-skills.sh` and `--print`.
- **More practice PRs with planted problems.** One exists —
  [lab 05](labs/05-review-a-planted-pr/lab.md), three real findings and a decoy — and one is
  not a set.
- **Ticket ingestion via a read-only Jira MCP.** Copy-paste is the committed path; a pasted
  description does miss the criteria filed as a subtask, the decision in a comment, and the
  linked design page, so it is worth doing eventually.

## Prior art

- [`mattpocock/skills`](https://github.com/mattpocock/skills) — MIT. Its `writing-great-skills`
  shaped the authoring rules here. Its own `code-review` is deliberately different: uncapped,
  dual-axis, built on parallel sub-agents. That last part is the interesting bit — parallel
  sub-agents are the thing you *cannot* do portably, so a procedure built on them stops being a
  paste-into-any-chat file.
- [`limsijie93/ai-agent-skills`](https://github.com/limsijie93/ai-agent-skills) — origin of the
  one-canonical-copy-plus-symlinks layout, inverted here so the canonical files sit at the path
  the slides show.
- [**Stanford CS146S · The Modern Software Developer**](https://themodernsoftware.dev/) (Mihail
  Eric) — ten weeks on the same thesis, reached independently: specification and verification,
  not syntax. Three claims this repo was asserting on its own authority now have citations from
  its reading lists, and the review exercise in `LEARN.md` is adapted from its review week. Its
  [assignments](https://github.com/mihail911/modern-software-dev-assignments) ship a real
  application to break, which is the thing this repo deliberately does not — read them if you
  want the hands-on half. Where it goes deep on one vendor per week, we go portable; that is the
  only real disagreement.

## Licence

MIT. See [LICENSE](LICENSE) — this repo exists to be copied.

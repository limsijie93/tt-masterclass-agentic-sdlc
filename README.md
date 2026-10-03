# Agentic SDLC — companion repo

Files from the lecture **Agentic SDLC: Specs → Quality → Review**, by Si Jie Lim.

### → Just watched the lecture? Read [**LEARN.md**](LEARN.md) instead.
### → Want one page to pin up? [**course/reference-card.md**](course/reference-card.md).
### → Following the masterclass? [**course/guide.md**](course/guide.md) maps each chapter to its files.

It is the hour after: one ticket end to end, one skill you can try without installing anything,
a lab with your hands on the keyboard, and two deliberately-wrong files to check yourself
against. **This** document is the reference — what each file is, why it is shaped that way, and how to adopt it. Come back to it
when you want it in your own repository.

> **Everything produced in the lecture is a file in this repo, reviewed like code.** That is
> what makes it a team practice instead of a personal habit.

## What's yours

**Two folders, two jobs.** Everything for the masterclass is in [`course/`](course/).
Everything that already existed to run it, the practice app and the checks, is in
[`tooling/`](tooling/): you use it through commands, and never need to edit it.

```
course/            ← the masterclass
  guide.md           which file goes with which chapter
  reference-card.md  the one-page summary
  demos.md           every lecture demo, with the commands to replay it
  tickets/           two worked tickets, every step as a file     (read)
  labs/              six hands-on labs: ./lab start 01             (do)
  templates/         blank shapes, plus python/ and typescript/ fills  (copy)
tooling/           ← existing assets: read freely, don't edit
  myapp/             the practice app the labs and demos break
  tools/ scripts/    the lab runner, the guards, the checks
  tests/ evals/      the repo's own tests
.github/skills/    the eight skills, where every assistant looks for them
harvest/           the harvest ledger, which the skill expects at this path
lab                the lab runner: ./lab, ./lab start 01, ./lab check 01
```

The root also holds the config files the tools look for there (`AGENTS.md`, `Makefile`,
`pyproject.toml`, the dotfiles).

| To | Open |
|---|---|
| Follow a chapter | [`course/guide.md`](course/guide.md) |
| Read a worked ticket | [`course/tickets/PROJ-142/`](course/tickets/PROJ-142/) |
| Do a lab | `./lab`, then `start 01`, `check 01`, `solution 01` |
| Replay a demo | [`course/demos.md`](course/demos.md) |
| Copy something into your repo | [`course/templates/`](course/templates/), and the skills: [Install the skills](#install-the-skills) |

Your own work (`pruned.md`, `yours.ini`, `test_yours.py`, `specs/LAB-*`, `reviews/LAB-*`, each
`report.md`) is gitignored, so it never collides with an update.

## Install the skills

All eight skills, in one step, from wherever you use Claude:

| You use | Do this |
|---|---|
| **Claude Code**: the terminal, or the **Code** tab in Claude Desktop | Run the two commands below. In the Desktop app, after the first one you can also pick it from **+ → Plugins → Add plugin** |
| **Claude Desktop chat or claude.ai**: Pro, Max, Team or Enterprise | Download the ZIPs from the [latest release](https://github.com/limsijie93/tt-masterclass-agentic-sdlc/releases/latest), one per skill, and upload each under **Customize → Skills**. **Code execution** must be on (**Settings → Capabilities**) |
| **A Team or Enterprise org** | One admin uploads the ZIPs and uses **Publish to org** on each. Everyone else installs nothing |
| **Any other assistant** (Cursor, Copilot, Codex, …) | `npx skills add limsijie93/tt-masterclass-agentic-sdlc`, which needs Node |
| **This repository, opened in Claude Code** | Nothing. `.claude/skills/` already links to every skill |

```
/plugin marketplace add limsijie93/tt-masterclass-agentic-sdlc
/plugin install agentic-sdlc@tt-masterclass-agentic-sdlc
```

Check it worked from a terminal with `claude plugin list`: `agentic-sdlc` is listed. Pull a newer
version later with `claude plugin update agentic-sdlc@tt-masterclass-agentic-sdlc`, then restart
Claude Code.

The plugin namespaces its skills: `/spec-interrogate` becomes `/agentic-sdlc:spec-interrogate`.
They still load on their own when a request matches their description. The plugin ships skills
only, with no hooks: the edit guards in `.claude/settings.json` belong to this repository, and a
plugin would switch them on in every project you open.

These skills read and write files in a repository, so they do the most in Claude Code. In
Desktop chat, upload the files you want them to work on.


## The 90-minute path, if you only do one thing

Three pull requests, each under an hour:

1. Run [`stack-profile`](.github/skills/stack-profile/SKILL.md) on your repo, correct what it
   got wrong, then [`gates-draft`](.github/skills/gates-draft/SKILL.md). You get a baselined
   contract, hook config and `AGENTS.md` Commands block for **your** stack, in `gates/draft/`.
2. Prune the generated `AGENTS.md` below 60 lines by hand — the pruning is the part that
   matters. Put a name in the H1 and the path in `CODEOWNERS`.
3. Add `tier1` to your branch's required status checks. Only `tier1`.

Prefer to copy rather than generate? [`course/templates/`](course/templates/) has the stack-neutral shapes, and
its [`python/`](course/templates/python/) and [`typescript/`](course/templates/typescript/) folders have them filled in. Read
[`course/templates/README.md`](course/templates/README.md) first — turning these on repo-wide on day one is how
the initiative dies in week two.

## Honestly: what runs, and what is a template

There **is** an application here now, and it is deliberately small. `tooling/myapp/` exists to be
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
| `tooling/myapp/` — the app, with the full tier-1 stack: ruff, mypy strict, `lint-imports`, semgrep, tests | `course/templates/*` — written for the same fictional service, stack-neutral |
| `tooling/scripts/` and `tooling/tools/` — with tests, ruff-clean, mypy-strict-clean | `course/templates/python/*`, `course/templates/typescript/*` — two fills of those shapes |
| `.semgrep/` — the rules have their own unit tests, and now real code to fire on | |
| `.importlinter` — three contracts, and a test proves the third one bites | |
| `.pre-commit-config.yaml` — this repo's own gates | |
| `.github/workflows/review.yml` — language-agnostic; it runs whatever your pre-commit config declares | |

`course/tickets/PROJ-142/*` are still artifacts rather than code — but every `path:line` they cite now
resolves, and `tooling/tests/test_example_consistency.py` fails if one stops resolving. They were
consistent with each other before; they are correct now.

One file is named to *avoid* being picked up automatically: the skill template is
`SKILL.template.md`, not `SKILL.md`, because anything named `SKILL.md` under a skills directory
registers as a live skill.

`course/templates/python/importlinter.example.ini` used to be the second such file — it would have failed on
every commit as a root `.importlinter`, because there was no `myapp` for `lint-imports` to
import. That is no longer true, and the root [`.importlinter`](.importlinter) is now real and
enforced. The template stays, because it carries the baseline-and-ratchet commentary an
established repo needs and the live file has no violations to baseline.

## The review ladder, and the files that implement it

| Tier | What | Verdict | Where it lives |
|---|---|---|---|
| 0 · Pre-action | guards that see an edit before it is written | **asks**, or blocks | [`tooling/tools/guard_test_edits.py`](tooling/tools/guard_test_edits.py), [`tooling/tools/guard_protected_paths.py`](tooling/tools/guard_protected_paths.py), via [`.claude/settings.json`](.claude/settings.json) |
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
measured non-determinism, are in [`course/citations.md`](course/citations.md).

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
[`course/templates/README.md`](course/templates/README.md) tells adopters to measure for a week before
enforcing and this is our own gate. Flip to `enforce` in a PR carrying the observed counts.

**The second guard protects the first.** `guard_protected_paths.py` refuses agent edits to
`.claude/settings.json` and `tooling/tools/guard_*.py`, because a guard the agent can disable is not a
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
override — `course/templates/managed-settings.example.json`, with the paths, the three locks, and the
tension it creates, in [`course/templates/README.md`](course/templates/README.md).

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

| Skill | Chapter | Run it |
|---|---|---|
| [`stack-profile`](.github/skills/stack-profile/SKILL.md) | 2.2 | Once per repo, before writing gates |
| [`gates-draft`](.github/skills/gates-draft/SKILL.md) | 2.2 | After the profile is corrected |
| [`spec-interrogate`](.github/skills/spec-interrogate/SKILL.md) | 1.2 | Before drafting anything |
| [`spec-draft`](.github/skills/spec-draft/SKILL.md) | 1.3 | Once the questions are answered |
| [`build-slice`](.github/skills/build-slice/SKILL.md) | 2.3 | After the spec, one acceptance criterion at a time |
| [`pr-brief`](.github/skills/pr-brief/SKILL.md) | 3.3 | Opening a PR, in the session that wrote the code |
| [`code-review`](.github/skills/code-review/SKILL.md) | 3.2 | **In a fresh session.** Never the one that wrote it |
| [`harvest`](.github/skills/harvest/SKILL.md) | 4.1 | After the review, before the branch is deleted |

### Installing them, or not

The one-step install for every Claude surface is in
[Install the skills](#install-the-skills) at the top of this file. The rest of this section is
the manual route, and how it works.

**Paste-first.** Every skill body works pasted into any assistant, with nothing installed.
Installing is an optimisation:

```bash
./tooling/scripts/sync-skills.sh --print spec-interrogate | pbcopy
```

To install, one canonical copy under `.github/skills/` is linked into every other host's path:

```bash
./tooling/scripts/sync-skills.sh            # this project: .claude/, .cursor/, .agents/
./tooling/scripts/sync-skills.sh --user     # also ~/.claude/ and ~/.agents/, for any repo
./tooling/scripts/sync-skills.sh --check    # drift detection, for CI
./tooling/scripts/sync-skills.sh --copy     # real copies, for Windows without Developer Mode
```

The eight skills cost roughly 470 tokens of always-loaded context, the name and description
only (`claude plugin details agentic-sdlc` measures it).
Bodies load when triggered; `references/` files load when read.

**Language lock, and where it is unavoidable.** An executable check cannot be
language-agnostic — parsing the language is what makes it checkable. So the split is: the
*decision* about what to enforce is a skill (`gates-draft`), and the *executable* is its
generated output. `course/templates/` names no language; `course/templates/` holds one fill per ecosystem;
[`gates-by-stack.md`](.github/skills/gates-draft/references/gates-by-stack.md) maps between
them.

Two things turn out to be more portable than they look, and one less. `pre-commit` is not a
Python tool — it manages Node, Go, Rust and Ruby hooks, and it is why tier 1 ports at all. And
`semgrep` spans 30+ languages. But **one semgrep rule cannot span two of them** when its
patterns rely on language-specific syntax: declaring `languages: [python, typescript]` silently
breaks the Python negation and starts flagging correct code. Measured, not assumed — the numbers
are in [`.semgrep/README.md`](.semgrep/README.md).

**One limit, stated rather than hidden.** Skill bodies are portable and
`tooling/scripts/lint_skills.py` enforces it (no host names, no absolute paths, declared inputs, fixed
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
expected to be rewritten per host, exactly like the blank-versus-filled split in `course/templates/` used
everywhere else here. `lint_skills.py` check 11 compares them, so the two halves cannot drift:
a body claiming it runs no commands beside an allowlist granting a shell fails the build.

Seven of the eight skills declare no shell. `build-slice` is the exception and the reason is its
procedure — it has to confirm a test is red before implementing, and that is not something a
skill can do by reading.

## The labs

[`course/labs/`](course/labs/) is the keyboard time. Six, about two and a half hours, and **the first three need no
agent, no API key and no account** — which is the ordering decision that matters, because a
learner who meets "you will need a key" at lab 01 stops at lab 01.

```
make setup && source .venv/bin/activate
./lab
```

| # | Lab | Chapter | Needs |
|---|---|---|---|
| 01 | Prune the context file | 2.1 | nothing |
| 02 | Make the gate actually bite | 2.2 | nothing |
| 03 | The test that lies | 3.3 | nothing |
| 04 | Interrogate a real ticket | 1.2 | an agent |
| 05 | Review a planted pull request | 3.2 | an agent |
| 06 | Implement one criterion | 2.3 | an agent |

**A lab is an eval case with a human as the engine.** `tooling/tools/lab.py` is `tooling/tools/run_evals.py`
with the one call to `$EVAL_ENGINE_CMD` replaced by printing the brief and waiting — same file
format, same frontmatter parser, same assertions. What may be asserted about a skill's output
turns out to be exactly what may be asserted about a learner's, for the same reason: shape and
stopping behaviour are checkable and prose is not.

Marking is the ladder again — machine blocks, a key comments, you decide — and the checker
holds itself to the two rules in [`course/labs/README.md`](course/labs/README.md). The first one cost
something: an untouched checkout scored **3/7** on lab 01 the first time, because `max_lines`
and `banned_tokens` are both vacuously true of a file nobody wrote. Eight assertions carry an
existence guard now.

## The worked ticket

**If you are here to learn rather than to adopt, [`LEARN.md`](LEARN.md) walks this in order with
what to notice in each file.**

[`course/tickets/PROJ-142/`](course/tickets/PROJ-142/) is one ticket from vague report to reviewed pull
request, in reading order — including the bloated `AGENTS.md` draft that
`course/templates/AGENTS.md` was pruned *from*, so the pruning is a diff rather than a claim.

**Two files there are deliberately wrong.** One review finding is a false positive and one test
verifies nothing; the lecture polls the room on both. `course/tickets/PROJ-142/AGENTS.md` tells an
agent not to correct them, which matters because the first thing most people do with this repo
is point an agent at it.

## Do the skills still do what they say?

`tooling/scripts/lint_skills.py` proves the skills' **declared** contracts fit together. Nothing
executed a skill until [`tooling/evals/`](tooling/evals/) existed, so nothing checked that a skill **honours**
the contract it declares — a skill whose Procedure was nonsense passed all ten checks.

> The linter proves the contracts fit together. An eval proves a skill keeps its own.

Assertions are properties of the output's shape or the skill's stopping behaviour, never of its
prose, because a flaky gate destroys trust in about a week. The highest-value ones assert a
**refusal**: given an unanswered question, no spec exists.

Which creates the trap the suite is built around, and it is worth running yourself:

```
EVAL_ENGINE_CMD=true python3 tooling/tools/run_evals.py --all      →  0/7 passed
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
estimate are in [`tooling/evals/README.md`](tooling/evals/README.md).

## This repo checks itself

The thesis applied inward. `make tier1`, or:

```bash
python3 tooling/scripts/lint_skills.py --check-agents   # portability rules + the skill chain
./tooling/scripts/sync-skills.sh --check                # host symlinks match canonical
semgrep test .semgrep/                          # the rules' own unit tests
python3 tooling/tools/check_commands_sync.py            # AGENTS.md Commands == the gate
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

[`course/demos.md`](course/demos.md) maps every recording to its chapter and the exact
commands that produce it. All twelve have written, verified beats; none of them is filmed.


## Not here yet

Named so the gaps read as decisions:

- **Governance** (chapter 4.1) — the shape is now `course/templates/governance.example.md`: visibility
  before limits, four adoption metrics chosen so that gaming one moves another the wrong way, and
  the trust boundary. What is still absent is a **filled** one, and deliberately: the vendor rows
  are a purchasing decision and the thresholds need a month of measurement, so a default here would
  be the aspirational content this repo warns about, in the file a manager is most likely to copy.
- **Per-host install guides** — largely obviated by `sync-skills.sh` and `--print`.
- **More practice PRs with planted problems.** One exists —
  [lab 05](course/labs/05-review-a-planted-pr/lab.md), three real findings and a decoy — and one is
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

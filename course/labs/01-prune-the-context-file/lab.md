---
lab: "01"
title: Prune the context file
segment: "05"
needs: no-agent
minutes: "20"
solution_into: course/labs/01-prune-the-context-file
assertions:
  - name: max_lines
    path: "course/labs/01-prune-the-context-file/pruned.md"
    limit: 60
  - name: file_mentions
    path: "course/labs/01-prune-the-context-file/pruned.md"
    needles: ["## Commands", "## Architecture", "## Gotchas"]
    hint: "Three sections change what an agent does. Those three survive."
  - name: banned_tokens
    path: "course/labs/01-prune-the-context-file/pruned.md"
    tokens: ["Repository Structure", "Deployment", "Python Best Practices", "Development Setup"]
    hint: "A whole section survived that should not have. Which one changes what the agent does?"
  - name: banned_tokens
    path: "course/labs/01-prune-the-context-file/pruned.md"
    tokens: ["3.12.4", "always write tests", "90%"]
    hint: "Something here is true today and false in a month, or was never true at all."
  - name: banned_tokens
    tier: 2
    path: "course/labs/01-prune-the-context-file/pruned.md"
    tokens: ["code review convention"]
    hint: "One line in the draft is not a rot risk. It is wrong NOW. Find it."
  - name: file_mentions
    tier: 2
    path: "course/labs/01-prune-the-context-file/pruned.md"
    needles: [".importlinter"]
    hint: "You deleted a false claim. What is actually true, and where does a machine check it?"
  - name: file_mentions
    tier: 2
    path: "course/labs/01-prune-the-context-file/pruned.md"
    needles: ["analytics"]
    hint: "You cut something that looked like trivia and was the most expensive line in the file."
---

## Brief

A generator pointed at `myapp/` produced `draft.md`. It reads well. It is also the shape of
context file the lecture spends a segment arguing against: long enough that the instruction
that matters is crowded out, and confident about things that are not true.

Your job is the part a generator cannot do. **Cut it under sixty lines, and keep only what
changes what an agent does.**

The test for every line: *if I delete this, does the agent behave differently?* "Prefer
`pathlib` to `os.path`" does not survive that test — ruff already enforces it, and a rule two
tools enforce is a rule you will eventually change in one place. "The export fixtures are slow"
does survive it: nothing else in the repository says so, and an agent that does not know it
will spend twenty minutes debugging a timing problem that is not there.

There is a second thing in the draft, and it is not a length problem. One statement is simply
false. The lecture calls this **context poisoning**: a wrong fact enters the context, is
treated as true, and is reused. It is why a rotted context file is worse than no context file —
the failure is active rather than passive. Find it, cut it, and replace it with the true
version.

## Start

```
cp course/labs/01-prune-the-context-file/draft.md course/labs/01-prune-the-context-file/pruned.md
wc -l course/labs/01-prune-the-context-file/pruned.md
```

Then cut `pruned.md` by hand. By hand is the exercise — this is the one step in the whole
pipeline that does not delegate, and the reason is in `python3 tools/lab.py solution 01`.

You may read `myapp/` and anything in this repository while you do it. You will need to: one
of the checks below cannot be satisfied without looking at what actually enforces the layering.

It is called `pruned.md` and not `AGENTS.md` for a boring reason worth knowing: a file named
`AGENTS.md` in a subdirectory is loaded as context by agents working in that subdirectory. A
lab fixture that quietly becomes a real instruction file is a bad joke to play on yourself.

```
python3 tools/lab.py check 01
```

## What good looks like

Fifty-something lines: an H1 with an owner, `## Commands`, `## Architecture`, `## Gotchas`, and
almost nothing else.

**The cuts, and why each one — this is the part worth arguing with.**

| Cut | Why |
|---|---|
| `Repository Structure` | Wrong the first time someone adds a module, and nothing tells you it went stale. The agent can list the directory; it cannot know the tree in your file is six weeks old. |
| `Technology Stack` versions | `Python 3.12.4` rots in a month. Worse, it is *already* a second place the versions live — `requirements-dev.txt` and `.pre-commit-config.yaml` pin them, and three sources of truth means two of them are wrong. |
| `Development Setup` | It is a README section. An agent does not create your virtualenv. |
| `Coding Standards` | Nine bullets, eight of which ruff enforces. A standard a machine already checks does not need restating; restating it means the day you change the ruff config you have two rules. |
| `Python Best Practices` | Same, and worse: it is generic Python advice that has nothing to do with this repository. It is the clearest example of volume crowding out the instruction that matters. |
| `Testing` | `We always write tests` is aspirational, and **an agent believes you**. Stating a coverage target the repo does not hold teaches the agent that this file describes wishes. Once it learns that, it discounts the lines that were true. |
| `Git Workflow` | Real, and it belongs in `CONTRIBUTING.md`. It does not change what the agent writes. |
| `Deployment` | "There is nothing to run locally" — so there is nothing for the agent to do. |

**What survives, and why it is short.** `## Commands` — because an agent that does not know the
gate ships code that fails CI instead of failing on the developer's machine. `## Architecture` —
four lines, not forty, naming the layer order and *what enforces it*. `## Gotchas` — the two
lines nothing else in the repository knows.

**The false statement.** The draft says the API-never-reaches-the-repository rule is

> a **code review convention** and reviewers are asked to watch for violations.

It is not. It is `.importlinter`, it blocks in tier 1, and the contract that does the work is
`api-never-calls-repo` — a `forbidden` contract, not the `layers` one, because a `layers`
contract does *not* forbid a higher layer skipping a lower one. That distinction was found by
running the tool and watching a violation pass, which is the only way it could have been found.

Getting this wrong in a context file costs twice. The agent is told a machine will not catch
the violation, so it weighs the rule as advice — and a reviewer reading the same file is told
to watch for something a machine is already watching for, which is tier-3 attention spent on
tier-1 work.

**The decoy.** The `analytics.py` gotcha looks like trivia and is the most expensive line in
the file. `myapp/repo/analytics.py` and `myapp/repo/exports/queries.py` both select on the
account column and the analytics table is smaller, so an agent asked to export an account's
rows reaches for the wrong one and produces a confident CSV with the wrong number of rows in
it. Nothing else in the repository says so. That is the definition of a line that earns its
place — and it is exactly the shape of line that gets cut when you are pruning for length
rather than for effect.

**Why you did this by hand.** Compare `course/tickets/PROJ-142/00-agents-draft.md` against
`course/templates/python/AGENTS.md`: 166 lines to 75, and the closing table names the two lines the
generator could not produce — a slow-fixture gotcha and a rule about not editing tests. Neither
is derivable from the source tree. Generation gets you a draft in thirty seconds; every bit of
the value is in what a human removes and the two things a human adds.

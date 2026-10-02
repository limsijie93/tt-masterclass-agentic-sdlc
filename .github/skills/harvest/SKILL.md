---
name: harvest
allowed-tools: Read, Grep, Glob, Write, Edit
description: >
  Run at the end of a ticket, after the review. Turns each finding into a proposal for a
  permanent place — the context file, the spec template, an executable rule, a new skill, or an
  eval case — and stops for a human to commit.
---

## Purpose

The first three blocks of this practice make a team faster at producing code. On their own that
is all they do: each ticket is individually quicker and nothing accumulates. A correction made
well every week is worse than a correction captured once, and the difference between the two is
whether anything outgrows the ticket it was found on.

This is the step that makes the loop a loop. Every other artifact here ends at "merged". This one
reads what the review found and asks, of each finding, the only question that compounds: **does
this belong somewhere permanent, and where?**

It costs about thirty seconds a ticket, and it is the first thing dropped when a sprint is tight —
which is why it is a file with a procedure rather than a good intention.

## When to use / when not to

Use once per ticket, after review, before the branch is deleted. The review is still readable and
the reasons are still fresh; a week later the finding is a line in a closed pull request nobody
will reopen.

Do not use:

- Mid-implementation. A finding is not a lesson until someone decided what to do about it.
- To make the change. This proposes; a human commits. See the stop conditions.
- On a ticket with no review. There is nothing to read.

## Inputs required

1. `reviews/<TICKET>.review.md` — the findings.
2. `specs/<TICKET>.md` — what was asked for, so a finding can be told from a missing requirement.
3. `harvest/ledger.md` — every previous observation. **This is the input that makes the rules
   work**: they are all about repetition, and one ticket cannot see repetition.

**Capabilities.** Reads the review, the spec and the ledger; writes `harvest/<TICKET>.md`, and **appends to** `harvest/ledger.md`; **runs no commands**. The append is why this skill's allowlist is one entry wider than every other shell-free skill in the chain: a host that distinguishes creating a file from modifying one has to be handed both. The ledger is added to across tickets rather than replaced, because a memory you rewrite each ticket is not a memory.

## Procedure

1. **Read the ledger first.** Load every previous observation before looking at this ticket's
   findings, so a repeat is recognisable as a repeat rather than logged as new.
   *Done when:* you can say, for each finding, whether the ledger already contains something of
   the same shape.

2. **Take each finding and route it.** One destination each, from the table below. A finding that
   fits nowhere is not a failure — say so and move on; some findings are about one ticket and
   nothing else, and inventing a permanent home for them is how a context file reaches four
   hundred lines.

   | What you noticed | Where it goes |
   |---|---|
   | A mistake the agent repeats | the repository's context file |
   | A field the spec kept missing | the spec template |
   | Something a human caught that a machine could have | a lint rule, an architecture contract, a custom rule, or a test |
   | A procedure used more than twice | a new skill |
   | A way an agent broke a skill's own contract, seen twice | an eval case |

3. **Apply the twice rule, and cite the ledger.** Rows one, four and five say *repeats*, *more
   than twice*, and *seen twice*. A first sighting is logged and **not** proposed. Every proposal
   names the previous ledger entries it is counting.
   *Done when:* every proposal cites at least one prior entry, or is a row where once is enough.

4. **Write the change, do not describe it.** A proposal is the actual line, rule, or field —
   quoted, ready to paste. "Consider adding a note about chunk sizes" is not a proposal; it is
   a reminder to do this work again later.
   *Done when:* every proposal contains text a human could commit without rewriting it.

5. **Prefer the cheapest destination that can hold it.** If a machine can check it, it goes to
   the machine, not to prose. A rule in the context file is a suggestion; the same rule in a
   config file blocks the pull request. Never propose prose for something checkable.
   *Done when:* no proposal routes to the context file when an executable destination exists.

6. **Append to the ledger** — one line per observation, including the ones you did not propose.
   The unproposed ones are the whole point: they are what makes the second sighting countable.

7. **Emit and stop.**

## Output contract

Two files.

`harvest/<TICKET>.md`:

```
harvest - <TICKET>

<n> findings read · <n> proposals · <n> logged, not yet proposed

## Proposals

### <destination>
from     <finding reference>
seen     <this ticket>, and <prior ledger dates>
change   <the exact text, rule, or field to add>
why      <one line>

## Logged, not proposed

<observation>  first sighting - proposed on the second

[ stopped - a human commits these ]
```

`harvest/ledger.md`, appended, one line per observation:

```
<date>  <TICKET>  <destination-or-none>  <one-line observation>
```

## Stop conditions

- **Always**, after emitting. This skill has no write path into any of the destinations.
- No review for this ticket. Stop, and say the review is the prerequisite.
- No ledger. Create it empty, log this ticket's observations, propose nothing that needs a second
  sighting, and say so.
- A proposal you cannot write concretely. Log it instead, and say which one.
- You find yourself editing the context file, the spec template, a config file, or a skill.
  Stop immediately. **An agent that edits the rules it runs under has removed the reason those
  rules are trustworthy** — the same objection that makes the guard machinery non-editable.

## Anti-patterns

- **Proposing on a first sighting.** Every rule here is about repetition. One occurrence is a
  fact about one ticket; the second is a fact about the team.
- Routing to prose what a machine could check. That converts a finding into a preference.
- Proposing a description instead of a change. It defers the work and looks like progress.
- Committing anything.
- Harvesting only the blocking finding. The non-blocking ones are cheaper to fix and more likely
  to recur, which is exactly the profile of something worth making permanent.
- Skipping the ledger append because nothing was proposed. Then the second sighting is a first
  sighting again, permanently, and nothing ever crosses the threshold.
- A proposal that adds a line to the context file without saying which line it replaces. That
  file has a length budget; growth without deletion is how it stops being read.

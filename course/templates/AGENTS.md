<!-- Copy to AGENTS.md at your repository root.

     STACK-NEUTRAL SKELETON. Nothing here names a language, because the SHAPE of a repo
     contract is the portable part and the CONTENT never is. Two filled versions:

       course/templates/python/AGENTS.md
       course/templates/typescript/AGENTS.md

     You should not fill this in by hand. Run `.github/skills/stack-profile` to detect what
     the repo actually is, then `.github/skills/gates-draft` to generate the Commands and
     Architecture sections for that stack. Then PRUNE — the pruning is the part that
     matters, and see course/tickets/PROJ-142/00-agents-draft.md for what unpruned looks like.

     AGENTS.md is an open standard under the Linux Foundation's Agentic AI Foundation, read
     natively by 20+ agents and adopted in 60,000+ repositories. It is not a feature of any
     one assistant. Write it once.

     TARGET: under 60 lines for what you copy. If a line does not change what an agent does,
     delete it. The failure mode is the 400-line file nobody reads, and a rotted context
     file is worse than none because it teaches the agent to lie about your codebase.

     NEVER put aspirational rules here. "We always write tests" when you don't describes a
     codebase that does not exist, and the agent will believe you. -->

# AGENTS.md · reviewed in PR, owned by @<name>

## Commands

<!-- The highest-value lines in this file. Every deterministic gate, in the order they
     should run, so the agent arrives at the pull request having already passed them.

     One rule: these must be the SAME TOOLS your pre-commit config enforces. Not the same
     arguments — scope differs by design — the same tools, reading the same config.
     tooling/tools/check_commands_sync.py fails the build when they diverge, so this cannot rot
     quietly. -->

Run these before showing me any code. Fix what they report, then tell me what you changed
and what you could not fix.

```
<formatter>
<linter>
<type checker>
<architecture contract>
<custom rules>
<tests>
```

## Architecture

<!-- The dependency direction you argue about most. State it flatly — "generally" and
     "where possible" turn a standard into a coin flip repeated a hundred times a sprint.

     Then name the file that ENFORCES it. Prose an agent can read but a machine cannot
     check is a preference, not a standard. -->

`<outer>` → `<middle>` → `<inner>`, never the reverse.

This is not advice. It is a contract in `<contract file>`, it fails the build, and it is the
same rule you are reading — one source of truth, two enforcement points.

## Conventions

<!-- Only what is specific to THIS codebase and changes what an agent does. Delete anything
     the model already knows: DRY, SOLID, "meaningful variable names", "keep functions
     small". Generic advice spends your context window telling it something it has. -->

- <a convention a newcomer would get wrong>
- <a convention that is enforced, with the rule that enforces it>

## Gotchas

<!-- The highest-value section, and the one a generator cannot write for you. These are the
     things that surprised someone. If you only add one line to this file by hand, add it
     here. -->

- <the thing that surprised the last person>

## Do not touch

- `<vendored code>`
- `<generated code>`
- Any test, in order to make an implementation pass. If a test is wrong, say so and stop.
  A suite edited into greenness is worse than no suite.

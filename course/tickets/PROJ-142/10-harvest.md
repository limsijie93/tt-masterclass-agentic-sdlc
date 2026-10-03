<!-- Worked example. In a real repo this is harvest/PROJ-142.md, written after the review and
     before the branch is deleted. Cited paths belong to the fictional myapp service.
     See ./README.md for the canon. -->

# harvest/PROJ-142.md

```
harvest - PROJ-142

3 findings read · 1 proposal · 2 logged, not yet proposed

## Proposals

### a custom rule
from     finding 1 (blocking) - legacy report went unbounded
seen     PROJ-142, and 2026-06-11 PROJ-098 (same shape: a default that means "no limit")
change   .semgrep/unbounded-export-query.yml
         pattern:      build_export_query(...)
         pattern-not:  build_export_query(..., chunk_size=$N, ...)
         message:      chunk_size is required; the default is unbounded
why      A human caught this twice now. The second time is the signal: a machine can
         check it, so it should not be a sentence in a context file.

## Logged, not proposed

The async job's execution branch shipped untested   first sighting - the PR flagged it,
                                                    the reviewer agreed, nothing recurred yet

A tier-2 finding reasoned about a streamed response  first sighting - if a review misreads
without reading the test body                       streaming again, this becomes an eval case

[ stopped - a human commits these ]
```

---

## What this artifact is for

**This is the file that turns twelve faster tickets into a team that gets faster.** Every other
artifact in this directory ends at "merged". Without this one, each ticket was individually
quicker and nothing accumulated — which is precisely the problem the client asked us to solve, so
a pipeline that stops at review answers a different question than the one asked.

Three things worth reading closely.

**One proposal from three findings.** Two are logged and not proposed, because the harvest rules
are about repetition and both were first sightings. That restraint is the mechanism, not
timidity: a context file that grows a line for every finding reaches four hundred lines and stops
being read, which is the failure mode segment 05 spends a whole artifact on.

**The proposal is the rule, not a note about the rule.** "Consider requiring a chunk size" is a
reminder to do this work again later. The actual pattern, ready to paste, is work that is done.

**It routes to the cheapest destination that can hold it.** The finding *could* have become a
line in `AGENTS.md`. It became a semgrep rule instead, because a machine can check it — and by
this repo's own argument, a rule in prose is a suggestion while the same rule in a config file
blocks the pull request. Prose is where things go when nothing cheaper will hold them.

Note where that rule actually came from: `.semgrep/unbounded-export-query.yml` carries
`origin: PROJ-142 review, finding 1` in its metadata. This artifact is that provenance, written
down at the moment it was decided rather than reconstructed afterwards.

## What it does not do

It does not commit anything. `harvest` has no write path into `AGENTS.md`, the spec template, a
config file, or a skill — and its stop conditions say to halt if it finds itself editing one.

An agent that edits the rules it runs under has removed the reason those rules are trustworthy.
That is the same objection that makes `tooling/tools/guard_protected_paths.py` refuse agent edits to the
guard machinery, one level up: here the protected thing is not a script but the team's agreement.

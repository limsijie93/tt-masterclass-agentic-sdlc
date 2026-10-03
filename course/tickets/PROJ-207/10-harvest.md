<!-- Worked example. In a real repo this is harvest/PROJ-207.md, written after the review and
     before the branch is deleted. Cited paths belong to the fictional myapp service.
     See ./README.md for the canon. -->

# harvest/PROJ-207.md

```
harvest - PROJ-207

3 findings read · 1 proposal · 2 logged, not yet proposed

## Proposals

### a custom rule
from     finding 1 (blocking) - the gate inherited a fail-open default
seen     PROJ-207, and 2026-08-24 PROJ-142 (same shape: a shared helper whose most
         dangerous argument is optional, and whose default is the unsafe value)
change   .semgrep/fail-open-entitlement.yml
         pattern:      has_feature(...)
         pattern-not:  has_feature(..., default=$D, ...)
         message:      pass default explicitly; the helper fails open
why      Second sighting of the shape, in a different module, with a different
         argument. The first time it was chunk_size meaning unbounded. A machine
         can check "was this argument passed", so it should not be a sentence
         somebody remembers.

## Logged, not proposed

A tier-2 review was refuted by a file the spec       first sighting - if scoping excludes
deliberately excluded from its context               a refutation again, this becomes the
                                                     argument for a tier-3 checklist item

An invalidation hook shipped with no test for        first sighting - correct today; nothing
the empty-cache case                                 recurred yet

[ stopped - a human commits these ]
```

---

## Why one proposal and two logged

The restraint is the mechanism. Every rule this step can propose is about **repetition**, and a
single ticket cannot see repetition — so a first sighting gets written down and nothing else.
A harvest that proposed something for all three findings is how a context file reaches four
hundred lines and stops being read, at which point it enforces nothing and costs tokens on
every request.

The one proposal cleared that bar by arithmetic, not by judgement. The ledger already held the
export ticket's `chunk_size` finding from August. This is the same shape — a shared helper, an
optional argument, a default that is the dangerous value — in a module that has nothing to do
with exports. Two independent sightings of one shape is what makes it a property of how this
team writes code rather than a property of one ticket.

## Why it routes to a rule and not to prose

The cheapest destination that can actually hold it. A sentence in a context file saying "always
pass `default` explicitly" is a preference: it is not checked, so within a quarter it is
followed in some call sites and not others, and nobody can tell you which without reading them
all.

`pattern` plus `pattern-not` is the whole rule, and it is checkable by a machine that does not
get tired. It fails the build on the call site, which is where the decision actually is — the
signature cannot be fixed, because `tooling/myapp/service/billing/upgrade.py` needs the opposite
default and needs it for a good reason.

That is worth stating plainly: **the rule exists because the bug cannot be fixed.** Two callers
want opposite behaviour from one helper, which is a legitimate design, and the residual risk is
that a third caller says nothing and inherits the wrong one. A gate on the call site is the
only thing that addresses the residual rather than the instance.

## What this step does not do

It **does not commit anything**. It writes proposals and stops. A step that edited the rules it
runs under would be able to widen its own remit, which is the same argument tier 0 makes about
a guard the agent can disable — and `harvest` has an explicit stop condition for exactly that
case.

A human reads the three, takes the one, and the ledger row for the other two survives to be
counted against whatever arrives next.

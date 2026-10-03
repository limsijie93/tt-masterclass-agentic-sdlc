<!-- Worked example. In a real repo the block below is written to specs/PROJ-207.answers.md
     with every `answer:` line empty. Cited paths resolve against tooling/myapp/, which is real and
     deliberately minimal. See ./README.md for the canon and path map. -->

# spec-interrogate PROJ-207 — the output

Grounding ran first, read-only. It is what makes question 4 askable at all: nobody on the
ticket mentioned the upgrade page, and the only way to know it shares the helper is to have
read the callers before writing anything.

```
spec-interrogate PROJ-207

1  Is "not entitled" the same state as "we could not determine entitlement"?
   blocks   what the helper returns when there are no rows
   assumes  they are the same, and both refuse
   answer:

2  How stale may an entitlement be, in seconds?
   blocks   whether this is a cache TTL or a cache invalidation problem
   assumes  a minute is acceptable
   answer:

3  What should a blocked request return — a 403, or a 200 with the feature hidden?
   blocks   the response shape, and whether the client needs changing too
   assumes  403 with somewhere to go
   answer:

4  tooling/myapp/service/billing/upgrade.py:44 calls the same entitlement helper.
   Is changing its behaviour in scope for this ticket?
   blocks   the blast radius, and whether the shared default can move at all
   assumes  out of scope
   answer:

5  Does a plan change already notify the application, or only the billing provider?
   blocks   whether invalidation is available or the TTL is the only tool
   assumes  there is a plan-change path we can hook
   answer:

[ stopped - waiting for a human ]
```

## Why question 1 is first

It looks like a definitions question and it is the whole ticket. Both reported symptoms come
out of one conflation: an account with no entitlement rows yet and an account entitled to
nothing return the same empty set, and the code in front of them picks an answer.

The support ticket describes that as two unrelated bugs — someone got too much, someone got too
little. They are one bug seen from both sides, and an interrogation that did not ask this would
have produced a spec for two.

## Why this stops here

The stop is the whole mechanism. An agent that answers its own questions produces a confident
artifact, and the team then anchors on it — the guesses are now invisible, which is strictly
worse than not having asked.

Five is a cap, not a target. Everything below the cap gets assumed and recorded in the spec's
Assumptions section, where it can be corrected in a pull request instead of in a meeting.

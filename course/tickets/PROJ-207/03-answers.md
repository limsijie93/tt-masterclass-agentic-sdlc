<!-- Worked example. This is specs/PROJ-207.answers.md after a human filled it in — the same
     file as 02, with the answers written on the `answer:` lines. spec-draft reads THIS, and
     refuses to run while any answer is blank. -->

# PROJ-207 — answered

Four minutes of a staff engineer's time, in a thread, on a Tuesday. That is the trade the
interrogation step is making: five questions answered in four minutes against a spec written on
five guesses and corrected over two weeks.

```
spec-interrogate PROJ-207

1  Is "not entitled" the same state as "we could not determine entitlement"?
   blocks   what the helper returns when there are no rows
   assumes  they are the same, and both refuse
   answer:  No. No rows means signup has not finished writing them, which is a real state
            for about a minute after self-serve signup. The gate must refuse in both cases,
            but the upgrade page must NOT — it should assume they might have it.

2  How stale may an entitlement be, in seconds?
   blocks   whether this is a cache TTL or a cache invalidation problem
   assumes  a minute is acceptable
   answer:  60 seconds is fine as a ceiling. But a plan change should be visible immediately,
            not in a minute — that is the complaint about upgrades not appearing.

3  What should a blocked request return — a 403, or a 200 with the feature hidden?
   blocks   the response shape, and whether the client needs changing too
   assumes  403 with somewhere to go
   answer:  403, and include the upgrade URL. The client already renders an upsell when it
            gets one; it currently never does, which is its own small waste.

4  tooling/myapp/service/billing/upgrade.py:44 calls the same entitlement helper.
   Is changing its behaviour in scope for this ticket?
   blocks   the blast radius, and whether the shared default can move at all
   assumes  out of scope
   answer:  Out of scope, and do not change its behaviour. That page is allowed to be
            optimistic — nagging someone about a feature they already have is the worse
            error there. Fix the gate at its own call site.

5  Does a plan change already notify the application, or only the billing provider?
   blocks   whether invalidation is available or the TTL is the only tool
   assumes  there is a plan-change path we can hook
   answer:  Yes, change_plan is ours and every upgrade and downgrade goes through it.

[ answered - spec-draft may run ]
```

## What answer 4 bought

It is the only answer that changed the shape of the work rather than a value in it.

The obvious fix for the reported bug is to change the shared helper's default from True to
False. One line, fixes the gate, and quietly changes what the upgrade page shows to every
account mid-signup. Nobody on the ticket would have noticed until a different support
escalation arrived by a different route.

The question was only askable because grounding read the callers before anything was written.
Nothing in the ticket mentions billing.

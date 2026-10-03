<!-- Worked example. In a real repo the block below is written to specs/PROJ-142.answers.md
     with every `answer:` line empty. Cited paths resolve against tooling/myapp/, which is real and
     deliberately minimal. See ./README.md for the canon and path map.

     Slide 13 shows the first two questions and the stop line. This is the full output. -->

# spec-interrogate PROJ-142 — the output

Grounding ran first, read-only. That is what makes questions 3 and 4 askable at all: you cannot
ask whether a limit is hard until you have seen there is a synchronous path and a queue, and you
cannot ask about `legacy.py` until you have found it.

```
spec-interrogate PROJ-142

1  Which export formats are in scope?
   blocks   changes the whole approach
   assumes  CSV only
   answer:

2  Is 30s a hard limit or a target?
   blocks   decides sync vs async
   assumes  soft target
   answer:

3  What row count must this support, and what is the largest account today?
   blocks   streaming is enough, or the work has to move off the request
   assumes  around 100k rows
   answer:

4  tooling/myapp/service/reports/legacy.py:210 calls the same query builder.
   Is changing it in scope for this ticket?
   blocks   the blast radius, and whether this is one PR or two
   assumes  out of scope
   answer:

5  Can the client poll for a result, or must the response stay synchronous?
   blocks   whether an async path is available to us at all
   assumes  polling already exists for bulk import
   answer:

[ stopped - waiting for a human ]
```

## Why this stops here

The stop is the whole mechanism. An agent that answers its own questions produces a confident
artifact, and the team then anchors on it — the guesses are now invisible, which is strictly worse
than not having asked.

Five is a cap, not a target. Everything below the cap gets assumed and recorded in the spec's
Assumptions section, where it can be corrected in a pull request instead of in a meeting.

Note what none of these questions are about: naming, file layout, formatting, or which library to
use. Those are either settled by the repo's context file or genuinely do not block the work. A
question that does not change the implementation is a question that spends a human's attention
for nothing.

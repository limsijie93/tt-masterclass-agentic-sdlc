<!-- Worked example. specs/PROJ-142.answers.md after a human filled it in. This file is the
     input that makes drafting possible, and the reason spec-draft has three inputs rather
     than one. See ./README.md for the canon. -->

# specs/PROJ-142.answers.md — answered

Answered by the product owner and the on-call engineer, in about four minutes. That is the point
of the `assumes` field: each question is answerable in seconds because it already carries the
guess it is correcting.

```
spec-interrogate PROJ-142

1  Which export formats are in scope?
   blocks   changes the whole approach
   assumes  CSV only
   answer:  CSV only. XLSX is a separate request and is not funded.

2  Is 30s a hard limit or a target?
   blocks   decides sync vs async
   assumes  soft target
   answer:  Hard. The gateway terminates the request at 30s, so anything
            slower is an error page no matter what we intend.

3  What row count must this support, and what is the largest account today?
   blocks   streaming is enough, or the work has to move off the request
   assumes  around 100k rows
   answer:  1M rows. Largest account today is 840k and growing ~4%/month,
            so 1M is next quarter, not hypothetical.

4  tooling/myapp/service/reports/legacy.py:210 calls the same query builder.
   Is changing it in scope for this ticket?
   blocks   the blast radius, and whether this is one PR or two
   assumes  out of scope
   answer:  Out of scope. The legacy report page is being retired in Q4 and
            nobody wants to touch it. But it must not get SLOWER or break —
            file a follow-up if this change puts it at risk.

5  Can the client poll for a result, or must the response stay synchronous?
   blocks   whether an async path is available to us at all
   assumes  polling already exists for bulk import
   answer:  Yes. The bulk-import screen already polls a job-status endpoint,
            so the client-side pattern exists and is understood.
```

## What each answer bought

| Answer | What it decided |
|---|---|
| 1 | Scope. XLSX moves to `Out of scope`, which is the field that stops the agent building it anyway. |
| 2 | `30s` becomes a testable threshold rather than an aspiration — acceptance criterion 1. |
| 3 | `1M rows` becomes the load the criterion is measured at. Without it, "under 30s" is untestable. |
| 4 | The `(!)` hazard becomes a decision on the record. This is the answer that the review in `08-review.md` turns out to depend on. |
| 5 | An async path is available, so a `202 + job id` response is legitimate — acceptance criterion 2. |

Answer 4 is the one worth pausing on. The hazard was found by grounding, decided by a human, and
written down — and it *still* caused the blocking finding at review time, because the
implementation touched the shared query builder anyway. The point is not that writing it down
prevents the problem. The point is that it turns a Friday-night incident into a review comment.

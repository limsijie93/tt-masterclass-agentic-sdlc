<!-- Worked example. In a real repo this is specs/PROJ-142.md, opened as PR #318 — before any
     implementation exists. It is a filled copy of course/templates/spec.md. Cited paths resolve against
     myapp/, which is real and deliberately minimal.
     See ./README.md for the canon. -->

# specs/PROJ-142.md · PR #318

| | |
|---|---|
| Ticket | `PROJ-142` |
| Owner | @limsijie93 |
| Drafted | 2026-08-24 |
| Inputs | `specs/PROJ-142.answers.md`, `specs/PROJ-142.touchpoints.md` |

## Goal

A customer on the largest account can export their account report as CSV and get the complete
file, without hitting the gateway timeout.

## Acceptance criteria

1. **CSV completes under 30s at 1M rows**
   - measured how: request the export for a 1M-row fixture account, drain the full response
     body, assert wall-clock under 30s
   - from: answer 2 (30s is a hard gateway limit) and answer 3 (1M rows)

2. **Returns 202 + job id when async**
   - measured how: request an export above the synchronous threshold, assert status 202 and a
     job identifier in the body; poll the status endpoint and assert it reaches a terminal state
   - from: answer 5 (the client already polls a job-status endpoint for bulk import)

## Out of scope

- **XLSX and any other format** — answer 1. CSV only; XLSX is a separate, unfunded request.
- **Scheduled and recurring exports** — nobody asked, and a reader would otherwise assume the
  async job means we now support them.
- **The legacy report page** (`myapp/service/reports/legacy.py:210`) — answer 4. It shares the
  query builder and is being retired in Q4. It must not get slower or break, but it is not being
  changed here.

## Touchpoints

```
myapp/api/exports/views.py:41           entry point
myapp/service/exports/service.py:88     query builder
myapp/tasks/queue.py:12                 async path
tests/test_exports.py                   3 tests exist

(!) myapp/service/reports/legacy.py:210
    shares the same query - out of scope,
    but will break
```

## Open questions

None. Empty before implementation starts, which is the condition for starting.

## Done when

An export for the largest live account returns a complete CSV, and the gateway-timeout errors
stop appearing in the exports endpoint's error rate.

---

## Constraints

- `myapp.api` must not import from `myapp.repo`. The obvious way to make this fast is to stream
  rows straight out of the data layer from the view — that is a layering violation, and
  `lint-imports` blocks it. Go through `myapp.service`.
- No test may be modified to make an implementation pass. A suite edited into greenness is worse
  than no suite.

## Known dependents / blast radius

| Dependent | Decision |
|---|---|
| `myapp/service/reports/legacy.py:210` | Out of scope, must not regress. Calls the same query builder, so any signature change to it has to stay backward compatible. **File a follow-up if this change puts it at risk.** |

## Data and scale assumptions

1M rows, from answer 3. The largest account today is 840k rows growing about 4% a month, so 1M is
next quarter rather than hypothetical. The fixture is generated, not a copy of production data.

## Rollout

Single deploy, no migration. The asynchronous path reuses the existing job queue and the existing
client-side polling from the bulk-import screen, so there is nothing new to enable.

## Observability

The exports endpoint's p99 latency and its 5xx rate, plus job-queue depth for the async path.

## Assumptions

Recorded rather than asked, because they fell below the five-question cap. Correct any of these in
review rather than in an incident:

- The synchronous threshold is a row count, not a byte count.
- The CSV column set is unchanged. This is a performance fix, not a format change.
- The existing three tests in `tests/test_exports.py` are correct and worth keeping.

## Commit slices

One per acceptance criterion, which is what makes the pull request reviewable criterion by
criterion.

- [ ] criterion 1 · stream the CSV response
- [ ] criterion 2 · move oversized exports onto the job queue
- [ ] criterion 2 · add the job-status route

<!-- LAB 06 FIXTURE. In a real repo this is specs/LAB-106.md, written by spec-draft after the
     questions were answered. It is a one-criterion slice on purpose: the smallest thing that
     can be implemented, and therefore the smallest thing that can drift. -->

# specs/LAB-106.md   ·   PR #402

## Goal

An export that is too large to run inside the request tells the caller how long to wait,
instead of returning a bare job id and leaving them to poll blind.

## Acceptance criteria

1. When an export is queued, the response carries `retry_after_seconds`, an integer, computed
   as the row count divided by `ROWS_PER_SECOND` and rounded up, with a floor of 1.

## Out of scope

- The synchronous path. A response that did not queue gains no new field.
- Making the estimate accurate under load. A fixed rate is enough for a first cut, and the
  ticket says so.
- `tooling/myapp/service/reports/legacy.py`, which calls the same builder and must not change.
- Any change to the job id, the status route, or the 202.

## Touchpoints

tooling/myapp/service/exports/service.py:104     should_queue, and the threshold it reads
tooling/myapp/api/exports/views.py:41            where the 202 is built
tooling/tests/test_exports.py:1                  existing coverage

## Open questions

- Whether `ROWS_PER_SECOND` should later be measured rather than fixed. Non-blocking.

## Done when

A queued export's response body contains an integer `retry_after_seconds` of at least 1, and a
test proves it for a row count that is not an exact multiple of the rate.

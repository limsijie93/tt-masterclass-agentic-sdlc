<!-- Worked example. In a real repo this is specs/PROJ-207.md, opened as PR #341 — before any
     implementation exists. The point of a spec PR is that the disagreement happens here,
     where it costs a comment, rather than in review where it costs a rewrite. -->

# specs/PROJ-207.md · PR #341

**Ticket:** PROJ-207 · Customer saw a feature they don't pay for
**Author:** spec-draft, from 01-ticket.md + 03-answers.md + 04-touchpoints.md
**Status:** proposed

## Goal

Entitlements reflect what an account is currently paying for, on every request, without a
logout. Both reported symptoms — a free account keeping a paid feature, an upgraded account not
seeing one — resolve to the same conflation between "entitled to nothing" and "entitlements not
written yet".

## Acceptance criteria

1. **Entitlement change visible within 60s**
   Resolution happens server-side per request behind a cache whose TTL is sixty seconds. A plan
   change invalidates immediately rather than waiting out the window.
   *Verified by* `tooling/tests/test_entitlements.py:48`, at the boundary: TTL-1 still cached, TTL not.

2. **Returns 403 + upgrade_url when not entitled**
   A refused request carries the upgrade URL for the flag it refused, so the client's existing
   upsell path has something to render.
   *Verified by* `tooling/tests/test_entitlements.py:72`.

## Out of scope

- **`tooling/myapp/service/billing/upgrade.py:44`.** It calls the same helper and must keep its current
  behaviour: optimistic when entitlement is unknown. Per answer 4, being wrong in the generous
  direction is the cheaper error on an upgrade page, and this ticket does not change it.
- **The shared default itself.** `has_feature(..., default=True)` stays as it is. The fix goes
  to the gate's call site. Moving the default is a two-caller change and this is a one-caller
  ticket.
- **A shared cache across processes.** The cache here is process-local. Cross-process
  invalidation is a different ticket with a different failure mode.
- **The client's upsell component.** It already renders an upgrade URL when given one.

## Touchpoints

From `04-touchpoints.md`, unchanged:

- `tooling/myapp/api/entitlements/views.py:37` — entry point
- `tooling/myapp/service/entitlements/service.py:89` — the shared helper
- `tooling/myapp/service/entitlements/service.py:70` — cache and TTL
- `tooling/myapp/repo/entitlements/queries.py:43` — the rows
- `tooling/tests/test_entitlements.py`

## Done when

Both criteria are verified by the cited tests, `lint-imports` still passes, and
`tooling/myapp/service/billing/upgrade.py` is unchanged in the diff.

That last clause is an acceptance criterion in everything but name: the out-of-scope file being
absent from the diff is checkable, and a reviewer should not have to notice it.

## Constraints

- The API layer may not read the entitlements table directly. `.importlinter` blocks
  `myapp.api -> myapp.repo`, and the shortcut is tempting here for the same reason it was in
  the export ticket: it is the shortest way to answer the question and it opts the caller out
  of the freshness promise the service owns.
- No sleeping in tests. The TTL is sixty seconds and the clock is injected.

## Assumptions

Recorded because they were below the five-question cap and nobody was asked:

- Sixty seconds is a ceiling rather than a target; a shorter TTL is not a regression.
- Every plan change goes through `change_plan`. If a second write path exists, invalidation
  misses it and criterion 1 holds only to the TTL.
- Flags are small in number and cheap to fetch as a set.

## Commit slices

One per criterion, test first:

1. Cache with TTL and injected clock, plus invalidation on plan change.
2. The gate: 403 and upgrade URL, with `default=False` passed explicitly.

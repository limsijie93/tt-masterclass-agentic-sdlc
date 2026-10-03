<!-- Worked example. Output of `pr-brief`, which describes and never judges. In a real repo
     this is specs/PROJ-207.pr.md, pasted into PR #342. -->

# PROJ-207 · Entitlements resolve per request

**Spec:** PR #341 (merged) · **Implements:** PROJ-207 · **PR #342**

Entitlements were read once at login and held for the session. That is why a downgraded
account kept a paid feature until it logged out, and why an upgraded one could not see the
feature it had just bought. Both are the same conflation, from opposite sides: an account with
no entitlement rows yet and an account entitled to nothing return the same empty set.

Resolution now happens server-side per request behind a sixty-second cache, and a plan change
invalidates rather than waiting out the window.

## Acceptance criteria

- [x] **Entitlement change visible within 60s** — `tests/test_entitlements.py:48`
- [x] **Returns 403 + upgrade_url when not entitled** — `tests/test_entitlements.py:72`

## Suggested read order

1. `myapp/service/entitlements/service.py` — the cache and the TTL. Start at
   `resolve_entitlements`; the injected clock is what makes the boundary testable.
2. `myapp/api/entitlements/views.py` — the gate. The argument that matters is `default=False`,
   and commit b7e4d2 is that one line on its own.
3. `tests/test_entitlements.py:48` — the boundary, at TTL-1 and TTL.
4. `myapp/repo/entitlements/queries.py` — `count_entitlements` exists to tell "no rows yet"
   from "entitled to nothing", which is the distinction the ticket is about.

## Out of scope, unchanged in this diff

`myapp/service/billing/upgrade.py:44` calls the same helper and keeps its current optimistic
behaviour, per answer 4 of the interrogation. It is not in the diff. If it appears in a later
one, that is the change this spec said not to make.

## Candidate untested paths

Offered as candidates, not as defects. A reviewer decides.

- A plan change for an account with nothing cached. `invalidate` is a no-op there and nothing
  asserts that it stays one.
- Two resolutions inside the same TTL window for different accounts. The cache is keyed by
  account and nothing tests that one account's entry cannot answer for another.
- A flag absent from a non-empty entitlement set. Covered incidentally by the 403 test, not
  directly.

## What this description deliberately does not say

Whether the change is good. `pr-brief` runs before review and stops if it catches itself
forming a verdict, because the reviewer three steps downstream needs a fresh context rather
than an inherited conclusion.

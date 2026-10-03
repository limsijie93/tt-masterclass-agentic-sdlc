<!-- LAB 05 FIXTURE. In a real repo this is specs/LAB-105.md. It is the thing the review
     checks against, and a review without one is a style opinion wearing a uniform. -->

# LAB-105 — One tenant's traffic slowed everyone else down

## Problem

A single customer sent a burst of search requests and every other customer's latency went up
with it. There is no request limiting in the public path today.

## Acceptance criteria

1. A request over the limit returns `429` with a `Retry-After` header naming the window.
2. Limits are **per tenant**: one tenant's traffic must not consume another tenant's allowance.

## Out of scope

- **The internal admin API.** It shares `limit_for` and must not start being throttled.
- **Report generation.** Nothing in `svc/service/reports.py` is part of this change.
- Per-route limits. One limit per tenant per window is enough for now.

## Constraints

- `svc.api` goes through `svc.service`. The middleware must not read the counter store directly.

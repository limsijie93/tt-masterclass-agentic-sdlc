<!-- Worked example, second chain. The ticket as filed, unedited — vague but typical, which
     is the only kind worth practising on. See ./README.md for the canon and path map. -->

# PROJ-207 · Customer saw a feature they don't pay for

**Reporter:** Support (escalated from a customer success call)
**Priority:** High
**Component:** Billing / entitlements

## Description

A customer on the free plan reported that Advanced Export was available to them for "a couple
of weeks". They used it. When they mentioned it on a renewal call, we confirmed it should never
have been visible.

Support has found two more accounts in the same state. All three were created through the new
self-serve signup flow.

We also have the opposite complaint from a different account: they upgraded, and the feature
did not appear until they logged out and back in.

Can we make entitlements actually reflect what someone is paying for?

## Notes from the CS call

> "They were quite gracious about it but obviously we can't invoice for it retroactively."

Engineering note added later: entitlements are read once at login and cached for the session.

<!-- Worked example. In a real repo this is specs/PROJ-207.touchpoints.md. Cited paths resolve
     against tooling/myapp/, which is real and deliberately minimal.
     See ./README.md for the canon and the slide-path-to-real-path map. -->

# specs/PROJ-207.touchpoints.md

Output of the grounding pass: read-only exploration, every claim carrying a `path:line`.

```
touchpoints - PROJ-207

tooling/myapp/api/entitlements/views.py:37        entry point
tooling/myapp/service/entitlements/service.py:89  the shared helper
tooling/myapp/service/entitlements/service.py:70  cache and TTL
tooling/myapp/repo/entitlements/queries.py:43     the rows
tooling/tests/test_entitlements.py                6 tests exist

(!) tooling/myapp/service/billing/upgrade.py:44
    calls the same helper and wants the
    opposite default - out of scope,
    but will break
```

## The `(!)` line is the whole reason this file exists

Nothing in the ticket mentions billing. Support escalated a feature-gate bug, and the obvious
implementation reads "change the default so it refuses" — which is one line, passes every test
anybody would think to write for the gate, and changes the upgrade page for every account whose
signup has not finished.

Grounding found it by reading the callers of the helper before anything was written. That is
thirty seconds of a read-only pass, and it converted a one-line fix into a question a human
answered in four minutes, which is answer 4 of `03-answers.md`.

## This file gets read three times

Once by `spec-draft`, to fill the out-of-scope section with something other than a guess. Once
by `build-slice`, which treats everything outside this list as drift and writes it down. Once by
`code-review`, which asks what the change touched that the plan never named.

Three consumers is the argument for grounding being its own step rather than the first paragraph
of the spec. A paragraph gets skimmed; a file gets diffed.

## What is deliberately not here

The client. The upsell component already renders an upgrade URL when it gets one and currently
never does, so criterion 2 makes an existing code path start working rather than adding one.
That is worth knowing and is not a touchpoint, because this ticket does not open that file.

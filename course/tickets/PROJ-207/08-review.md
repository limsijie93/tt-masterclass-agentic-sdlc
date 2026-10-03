<!-- Worked example. Output of `code-review` in a FRESH session on PR #342: it has the spec,
     the touchpoints, the drift file and the diff, and none of the conversation that produced
     them. Finding 3 is deliberately wrong — see ./README.md, behind the spoiler. -->

# code-review PROJ-207 — PR #342

Read: `specs/PROJ-207.md`, `specs/PROJ-207.touchpoints.md`, `specs/PROJ-207.drift.md`, the diff.

Both acceptance criteria have a cited test and both tests assert something the criterion
actually says. Scope is clean: four files, all inside the declared touchpoints, and the
out-of-scope file is absent from the diff.

Three findings.

### 1 · blocking: the gate inherits a fail-open default one commit out of three

`tooling/myapp/api/entitlements/views.py` at commit 91ca80 calls the shared helper without passing
`default`, so it inherits `default=True` and grants the feature to any account whose
entitlement rows have not been written yet — which the spec's own Goal says is a real state
for about a minute after self-serve signup.

Commit b7e4d2 adds `default=False` and fixes it. The reason this is still blocking rather than
resolved is that nothing prevents the next call site from making the same mistake. The helper's
signature is the hazard: it is the only function in this module whose most dangerous argument
is optional, and the safe value is not the default.

`tooling/myapp/service/billing/upgrade.py:44` is the second caller and passes `default=True`
explicitly, correctly, for its own reasons. So the default cannot simply be flipped, and the
fix has to be a rule about call sites rather than a change to the signature.

**Suggested:** a check that fails on any call to `has_feature` without an explicit `default`.

### 2 · the invalidation path has no test for the empty case

`change_plan` calls `invalidate` for every plan change. When the account has nothing cached
that is a no-op, and nothing asserts it stays one. This is listed as a candidate untested path
in the pull request body, and it is the one of the three worth taking: a future `invalidate`
that raises on a missing key would break every first-ever plan change, and no current test
would notice.

Not blocking. The behaviour is correct today.

### 3 · acceptance criterion 1 is not met for revoked entitlements

The criterion says an entitlement change is visible within sixty seconds. The cache returns a
held value for the whole TTL, so an entitlement revoked immediately after a resolution is
served for up to sixty more seconds. For a downgrade — which is the reported bug — that means
the customer keeps a paid feature for a minute after losing it.

Acceptance criterion 2 is met. Criterion 1 is met for grants and not for revocations, and the
test at `tooling/tests/test_entitlements.py:48` only exercises the grant direction.

**Suggested:** invalidate on plan change rather than relying on the TTL.

---

> Advisory — not a merge gate. This review cannot judge domain rules, authorization or tenancy
> scoping, architectural fit, or whether this feature should exist. A human decides.

## Notes on the shape of this output, not its content

Three findings, one blocking. The contract is zero to three and **at most** one blocking, which
is not the same as exactly one: a clean pull request gets zero findings and no blocking verdict,
and a review that manufactures one to look diligent is how a bot gets muted.

Each finding names a file and a reason. None of them says "consider refactoring".

Finding 3 is the one to read twice.

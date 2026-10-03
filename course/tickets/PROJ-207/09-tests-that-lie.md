<!-- Worked example, second chain. The tautological test here is a DIFFERENT shape from the
     export ticket's: that one asserted on a mock's return value; this one asserts on a
     fixture it wrote itself. Both pass. Both cover nothing. -->

# The test that lies · PROJ-207

## The test as first written

```python
def test_has_feature_returns_the_entitlements_we_seeded() -> None:
    connection = _connection()
    queries.seed(connection, ACCOUNT, ("advanced_export",))

    flags = queries.fetch_entitlements(connection, ACCOUNT)

    assert service.has_feature(connection, ACCOUNT, "advanced_export") == (
        "advanced_export" in flags
    )
```

It passes. It is named sensibly. Coverage counts it, and it touches the helper the whole ticket
is about.

## Why it asserts nothing

The right-hand side of the assertion is computed from the same query the left-hand side runs.
Both sides read the database and ask the same question, so they agree no matter what
`has_feature` does with the answer — the argument order, the fail-open default, the cache, the
`count_entitlements` branch. Change any of them and the test still passes.

Apply the check that subsumes all of this: **delete the body of `has_feature` and return
`flag in queries.fetch_entitlements(connection, account_id)`**. The blocking finding of this
entire ticket is now unfixable-by-construction, and this test is green.

It is a different shape from the export ticket's tautology, which asserted on a value a mock had
been told to return. Nothing is mocked here. The fixture is real, the database is real, and the
test is still circular — because the expected value was *derived* rather than *stated*.

## The honest rewrite

```python
def test_an_account_with_no_rows_is_refused_by_the_gate() -> None:
    connection = _connection()

    response = views.feature_view(connection, UNWRITTEN_ACCOUNT, FLAG)

    assert response.status == 403
```

Three differences, and they are the general rule:

1. The expected value is **written down**, not computed. `403` is a literal. Nothing in the
   test can derive it from the code under test.
2. It exercises the path the criterion is about — the gate, with an account in the state the
   ticket exists for — rather than the helper in isolation.
3. The fixture arranges an **input**. The output is discovered, and disagreeing with it is how
   the test fails.

## The one this ticket nearly shipped

Worth showing because it is subtler and it passed review once:

```python
def test_the_cache_is_used() -> None:
    connection = _connection()
    service.resolve_entitlements(connection, ACCOUNT)
    _, cached = service.resolve_entitlements(connection, ACCOUNT)
    assert cached is True
```

This one does assert a literal, and it does exercise the real path. It is still nearly useless,
because it proves a cache exists and says nothing about when it stops. It passes against a TTL
of sixty seconds, of six hours, and of infinity — and "of infinity" is the bug the ticket was
filed for.

`tooling/tests/test_entitlements.py:48` probes TTL-1 and TTL instead. **A test that does not fail
against the bug you are fixing is decoration**, however real its fixtures are.

## Why this is the reviewer's third question

Once tier 1 and tier 2 have run, the human has three questions left:

1. Does it satisfy every acceptance criterion?
2. What did it touch that the spec never mentioned?
3. **Are the tests real, or tautologies?**

`tooling/tools/mutate.py` now answers a large part of the third mechanically: it changes a line of
`tooling/myapp/` and reports what the suite failed to notice. Both circular tests above survive a
mutation of the code they claim to cover, so both would be reported.

What it does not reach is the second example — the cache test survives nothing, because it
genuinely exercises the path; it is simply asking a weaker question than the criterion does. No
mutation operator can tell you that a passing assertion is about the wrong property.

So the machine catches tests that do not depend on the code. A person still has to catch tests
that depend on it and ask it the wrong question.

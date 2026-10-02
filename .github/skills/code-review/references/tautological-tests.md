# Tests that verify nothing

The third disclosure tier: this file is not loaded at startup, and no step of the skill's
procedure depends on it. It loads when someone reads it.

The one check that subsumes everything below: **delete the production code under test. Does
the test still pass?** If yes, it tests nothing. Every shape here is a way of failing that
check while looking like a test.

Worth naming the reason these are so common in generated code. A model asked to "add a test
for this function" is optimising for a test that passes, and the surest way to make a test
pass is to remove its dependence on the thing under test. Nobody writes these dishonestly.
They are what "make the tests green" looks like when taken literally.

---

## 1 · Asserting on your own mock

The canonical one, and vivid in Python.

```python
def test_export_returns_csv():
    service = Mock()
    service.export.return_value = "col1,col2\n1,2"
    result = service.export()          # calling the mock, not the code
    assert result == "col1,col2\n1,2"  # asserts the mock's own return value
```

The mock is configured to return a value, then asked for that value, and the value is
compared to itself. Delete the real `export` and it passes. Delete the entire module and it
passes.

**The honest version** calls the real thing and asserts something the real thing decides:

```python
def test_export_returns_csv(account_with_rows):
    result = export_service.export(account_with_rows, chunk_size=100)
    lines = result.splitlines()
    assert lines[0] == "id,email,created_at"   # the header the code chose
    assert len(lines) == 101                   # 100 rows plus the header
```

## 2 · Asserting that the mock was called

```python
def test_queues_the_job():
    queue = Mock()
    schedule_export(account, queue=queue)
    queue.enqueue.assert_called_once()
```

Better than shape 1 — it does exercise `schedule_export` — but it verifies the *wiring* and
nothing about the outcome. It passes if the job is enqueued with the wrong arguments, the
wrong account, or a payload that will fail on the worker. Assert on the payload, or on the
state after the job runs.

## 3 · The assertion that cannot fail

```python
def test_export_is_valid():
    result = export_service.export(account)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) >= 0          # always true
```

`len(result) >= 0` is a tautology in the literal sense. `is not None` and `isinstance` are
nearly as weak: they pass for `""` and for an error message rendered as a string.

## 4 · Testing the framework

```python
def test_model_saves():
    account = Account(name="test")
    account.save()
    assert Account.objects.get(id=account.id).name == "test"
```

This tests the ORM, which already has its own test suite. It will not fail for any bug you
could introduce, and it will fail loudly on an unrelated framework upgrade — noise in both
directions.

## 5 · Snapshot tests nobody reads

An approved snapshot is only as good as the review of the day it was approved. A snapshot
regenerated with `--update` after a change that broke behaviour is worse than no test: it
records the bug as intended, with a timestamp and an author.

Snapshots are good for output that is genuinely hard to assert piecewise, and only when the
diff is read every time it changes.

## 6 · The test that mirrors the implementation

```python
def test_discount():
    assert calculate_discount(100, 0.1) == 100 - (100 * 0.1)
```

The expected value is the implementation, restated. Any error in the formula is copied
faithfully into the assertion. Write the number: `== 90`.

---

## When reviewing

Three questions, in order of how often they find something:

1. If I deleted the function under test, would this fail?
2. Does the assertion name a value a human decided, or one the test just handed itself?
3. Would this fail for the bug the change was most likely to introduce?

A test suite with no failures and no coverage of the risky path is not evidence of quality.
It is evidence of a test suite. And **a suite edited into greenness is worse than no suite**,
because it converts an unknown into a false assurance — which is why "do not modify a test to
make an implementation pass" belongs in the repository's context file, stated flatly, as a
thing the agent will otherwise try.

---
lab: 03
title: The test that lies
chapter: "3.3"
needs: no-agent
minutes: 25
solution_into: course/labs/03-the-test-that-lies
assertions:
  - name: command_exits
    cmd: "cd course/labs/03-the-test-that-lies && python3 -m pytest -q test_yours.py >/dev/null 2>&1"
    code: 0
    needs: ["pytest"]
    hint: "Write course/labs/03-the-test-that-lies/test_yours.py, and make it pass against the real code first."
  - name: command_exits
    cmd: "cd course/labs/03-the-test-that-lies && ./mutate.sh blunt test_yours.py"
    code: 1
    needs: ["pytest"]
    hint: "Your test still passes with the function gutted. It is testing a mock, not the code."
  - name: command_exits
    tier: 2
    cmd: "cd course/labs/03-the-test-that-lies && ./mutate.sh default test_yours.py"
    code: 1
    needs: ["pytest"]
    hint: "A silent cap on the no-limit default slipped past you. Read the docstring as a contract, not as prose."
---

## Brief

`test_lies.py` passes. Run it.

```
cd course/labs/03-the-test-that-lies
python3 -m pytest -q test_lies.py
```

Now apply the one-step check the lecture gives you — *delete the function under test; does this
still pass?*

```
./mutate.sh blunt test_lies.py ; echo "exit=$?"
```

It exits `0`. The function it claims to test has been gutted and the test does not notice,
because the value it asserts on is the value it configured on the mock four lines earlier. It
has been green since the day it was written and it has never once been able to fail.

**Write a test that can.** Then find out whether it can catch more than the obvious break.

## Start

```
cd course/labs/03-the-test-that-lies
$EDITOR test_yours.py           # a new file; do not repair test_lies.py
```

Read `exporter.py`, including the docstring. Then:

```
python3 -m pytest -q test_yours.py       # passes against the real code
./mutate.sh blunt   test_yours.py        # must FAIL (exit 1)
./mutate.sh default test_yours.py        # must FAIL (exit 1) — this is the interesting one
```

`mutate.sh` is fifteen readable lines. Open it before you trust it.

```
./lab check 03
```

## What good looks like

Three tests. Two of them are the ones anybody writes:

```python
def test_rows_are_chunked_to_the_requested_size() -> None:
    assert chunk(["a", "b", "c"], size=2) == [["a", "b"], ["c"]]

def test_no_rows_is_no_chunks() -> None:
    assert chunk([], size=2) == []
```

Both call the real function, so both fail the moment it is gutted. That is tier 1 of this lab
and it is the easy half.

**The third test is the lab.**

```python
def test_the_default_means_no_limit_not_a_large_limit() -> None:
    rows = [str(n) for n in range(5000)]
    result = chunk(rows)
    assert len(result) == 1, "size=None must mean one chunk, not a big chunk"
```

The `default` mutation replaces the documented "no limit" with a silent limit of 1000. Every
test above that uses three rows and an explicit `size` still passes — the mutation is invisible
to them, because they never exercise the default and never go near the boundary. Only a test
that reads the docstring as a **contract** and pins it above any plausible implicit cap fails.

That is the same bug as the worked ticket. `chunk_size=None` meaning "unbounded" is the footgun
in `course/tickets/PROJ-142/`, it is the finding that `harvest/ledger.md` records twice, and the second
sighting is what turned it into a semgrep rule. Here you meet it from the other side: not as a
bug someone wrote, but as a change your test suite would have waved through.

**Two things worth taking away.**

*What a passing suite tells you.* It tells you the code and the tests agree. It does not tell
you the tests would notice if the code changed. Those are different claims, and only the second
one is what you buy tests for. `mutate.sh` measures the second claim, and measuring it is the
only way to find a test like `test_lies.py`, because from the outside it is indistinguishable
from a good one — green, named sensibly, reviewed and approved.

*Why this matters more with an agent in the loop.* Asked to make a failing test pass, the
cheapest available edit is often to the test. Tier 0 (`tooling/tools/guard_test_edits.py`) catches the
blunt version of that — an edit that removes assertions — and it cannot catch a test that was
born tautological. Nothing can, except running it against broken code.

**The production version.** `mutate.sh` is hand-rolled so you can read it. The real tools are
`mutmut` for Python and `Stryker` for JavaScript and TypeScript, and they generate the
mutations rather than hard-coding two. They are not wired into this repository's tier 1, on
purpose and for the reason `course/templates/README.md` gives about every new checker: turned on
repo-wide on day one, a mutation run produces a wall of surviving mutants nobody triages, and
the tool is discredited permanently. Measure first, baseline, then ratchet.

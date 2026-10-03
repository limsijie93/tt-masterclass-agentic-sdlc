<!-- Worked example, and the SECOND file here that is deliberately wrong.

     The first test below verifies nothing. That is the point — the lecture puts it on screen
     and asks the room whether it tests anything. Do not fix it. See ./README.md.

     Named .md rather than .py so pytest does not collect it. -->

# The test that verifies nothing

Slide 35. This is the most common decorative test a coding agent produces, and it is vivid in
Python.

```python
def test_export_returns_csv():
    service = Mock()
    service.export.return_value = "col1,col2\n1,2"
    result = service.export()          # calling the mock, not the code
    assert result == "col1,col2\n1,2"  # asserts the mock's own return value
```

Read it in the order it executes. A mock is created. The mock is told what to return. The mock
is asked for that value. The value is compared to itself.

**Delete `export` from the production code and this test still passes. Delete the entire
exports module and it still passes.** It is a two-line assertion that a string equals itself,
wearing the name of a test.

## Why an agent writes this

Not dishonestly. Asked to "add a test for the export function", a model is optimising for a
test that passes, and the most reliable way to make a test pass is to remove its dependence on
the thing being tested. Mocking the subject is the shortest path to green.

Which is why "do not modify a test to make an implementation pass" belongs in the repository's
context file as a flat prohibition. The agent will try it, and it will look like diligence.

## The honest version

```python
def test_export_returns_csv(account_with_100_rows):
    result = export_service.export(account_with_100_rows, chunk_size=10)

    lines = result.splitlines()
    assert lines[0] == "id,email,created_at"   # the header the code chose
    assert len(lines) == 101                   # 100 rows plus the header
    assert lines[1].startswith("1,")           # a value the code produced
```

Three differences, and each one matters:

1. It calls the real service, so deleting the real service fails the test.
2. It asserts on values the **code** decided — the column order, the row count, the first
   field — not values the test handed itself.
3. It uses a fixture for the input rather than a mock for the output. The input is arranged;
   the output is discovered.

## The check that subsumes all of this

> Delete the production code under test. Does the test still pass?

That question catches every shape of this problem and needs no taxonomy to apply. More shapes,
with the reasoning for each, are collected in
`.github/skills/code-review/references/tautological-tests.md`.

**And a machine now asks it, on every pull request.** `tooling/tools/mutate.py` is that question
automated: it changes one line of `tooling/myapp/` — a `>` to a `>=`, a `None` to a `0` — runs the
suite, and reports every mutation the suite did not notice. A test that passes against code
that has been altered underneath it is not testing that code. That is the same claim as the
block quote, narrowed to something executable.

It is a weaker instrument than deleting the function, and deliberately: five operators, not
every possible edit. What it buys is that it runs without anyone remembering to.

## Why this is the reviewer's third question

Once tier 1 and tier 2 have run, the human has three questions left:

1. Does it satisfy every acceptance criterion?
2. What did it touch that the spec never mentioned?
3. **Are the tests real, or tautologies?**

The first two can be substantially answered by a machine — a spec, a touchpoints list, and a
diff are all machine-readable. The third was the one that resisted, because a tautological
test is *syntactically* indistinguishable from a good one. It is well-formed, it is named
sensibly, it passes, and coverage counts it.

**That sentence was true when this file was written and it is now half wrong, which is worth
leaving in rather than editing away.** Syntax was never the angle. Behaviour is: mutate the
code the test claims to cover and see whether the test objects. `tooling/tools/mutate.py` does that in
tier 1, and finding 17 of the 20 September review — *test quality lives at tier 2* — is what
made it worth building. The reviewer's third question is no longer purely human.

What stays human is everything the five operators do not reach: a test asserting on its own
mock still passes every mutation of production code it never calls. The machine catches the
tests that do not depend on the code. A person still has to catch the tests that do not
*touch* it.

So the reviewer's job in the AI era is narrower than this file first claimed, and more
durable for it: not reading every line, and not asking all three questions either — asking
the parts of the third that no sensor reaches, and building the sensor for the rest.

**A suite edited into greenness is worse than no suite**, because no suite is a known unknown
and a green suite full of these is a false assurance with a number attached.

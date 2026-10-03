# .semgrep/ — custom rules, with tests

> **Not course material.** It lives at the root rather than in [`tooling/`](../tooling/) because
> the tools that read it expect this path. You don't edit it for a lab.

Two rules. Both are the "executable version" column of chapter 2.2's prose-to-executable
table, and both are unit-tested, which is the part people are surprised by: a lint rule is
code, and it can be wrong.

## Run the tests

```
semgrep test .semgrep/
```

**Use that exact form.** Two nearby commands look equivalent and are not:

| Command | What it actually does |
|---|---|
| `semgrep test .semgrep/` | Finds both rule/fixture pairs. Exits 1 and names the rule and line on failure. **This is the one.** |
| `semgrep --test --config .semgrep/ .semgrep/` | Silently tests only one pair and reports `1/1 ✓ All tests passed`. A sabotaged fixture still passes. |
| `semgrep --test --config .semgrep/<rule>.yml ...` | Crashes with an `IndexError` in semgrep's own test harness. |

The middle row is the dangerous one, because it looks like success. It was verified by
sabotaging a fixture and watching it report green — which is exactly the tautological-test
lesson from chapter 3.3, applied to this repo's own test suite. A test that cannot fail is not
a test.

## Why one rule lives in a subdirectory

`api/no-orm-above-service.yml` has a `paths.include` of `**/api/**`, because a data-layer
call is only a violation *above* the service layer — flagging it in the service layer would
be noise, and noise is how a tool gets muted.

But semgrep pairs a rule with its fixture by basename in the same directory, and a fixture
sitting at `.semgrep/no-orm-above-service.py` does not match `**/api/**`, so the rule would
never fire on it and the test would be vacuous. Putting both files under `.semgrep/api/`
satisfies the pairing and the path filter at once.


`unbounded-export-query.yml` needs no such trick: it is specific by function name, so it sits
flat. Every path filter you can avoid is one less thing to keep true.



## One rule per language, and why we measured it

`unbounded-export-query` exists twice: `unbounded-export-query.yml` (Python) and
`ts/unbounded-export-query.yml` (TypeScript). Same defect, same message, same provenance,
different patterns.

The obvious move is one rule declaring `languages: [python, typescript, javascript]`, because
semgrep genuinely does span 30+ languages. **It silently breaks the negation.** Same patterns,
only the languages list changed, run against the Python fixture:

| `languages:` | Findings |
|---|---|
| `[python]` | 12, 17 — correct |
| `[python, typescript, javascript]` | 12, 17, **22, 27** — the last two are the `# ok:` cases |

A pattern matches real syntax. `chunk_size=$N` is a Python keyword argument; the TypeScript
equivalent is a property inside an object literal. A negation written for one grammar does not
hold for the other, and when it stops matching, the rule starts flagging correct code — which
is precisely how a tool gets muted.

The tool ports. The decision ports. The pattern does not. `.github/skills/gates-draft` knows
this and emits one rule per detected language rather than one rule with a longer list.


## The rules

**`api/no-orm-above-service`** (Python) — the executable half of one line in `AGENTS.md`: "no
data-layer calls above `myapp.service`". The import-linter contract catches this when it
crosses a module boundary as an *import*; this catches the other half, where the object
arrived by another route and the *call* is the violation. Two tools, one rule, neither
sufficient alone.


**`unbounded-export-query`** (and its `ts/` twin) — this is what a custom org rule looks like, and why it is worth
more than anything you can install from a registry: **it exists because a human caught this
once**, in the PROJ-142 review. That is the harvest loop's third row — "something a human
caught that a machine could have" becomes a lint rule — and this is the file it becomes.


## What is deliberately NOT here

A rule for bare `except`. Ruff's `E722` already covers it, and two gates for one rule is how
you end up with contradictory verdicts on the same line and an argument about which tool is
authoritative. Restraint is part of the design.

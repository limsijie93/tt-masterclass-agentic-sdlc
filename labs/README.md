# labs/

Keyboard time you do on your own, after the recording. Six labs, about two and a half
hours in total, and the first three need no agent, no API key and no account.

```
make setup                      # once: .venv plus the pinned tier-1 toolchain
source .venv/bin/activate
python3 tools/lab.py            # the list, and where you are
python3 tools/lab.py start 01
```

| # | Lab | Segment | Needs | Time |
|---|---|---|---|---|
| 01 | [Prune the context file](01-prune-the-context-file/lab.md) | 05 | nothing | 20 min |
| 02 | [Make the gate actually bite](02-make-the-gate-bite/lab.md) | 06 | nothing | 20 min |
| 03 | [The test that lies](03-the-test-that-lies/lab.md) | 10 | nothing | 25 min |
| 04 | [Interrogate a real ticket](04-interrogate-a-real-ticket/lab.md) | 03 | an agent | 25 min |
| 05 | [Review a planted pull request](05-review-a-planted-pr/lab.md) | 09 | an agent | 40 min |
| 06 | [Implement one criterion](06-implement-one-criterion/lab.md) | 07 | an agent | 35 min |

Then the capstone, which has no checker and is the one that transfers:
[`LEARN.md`](../LEARN.md#when-you-want-reps-review-code-you-just-wrote), on your own repository.

## How they are built

**A lab is an eval case with a human as the engine.** [`tools/run_evals.py`](../tools/run_evals.py)
shells out to `$EVAL_ENGINE_CMD` and asserts properties of what came back;
[`tools/lab.py`](../tools/lab.py) does everything else identically and, in place of that one
call, prints the brief and waits for a person. Same file format, same frontmatter parser, same
assertion registry in [`tools/eval_assertions.py`](../tools/eval_assertions.py).

That is not a clever reuse, it is the only honest one available: what may be asserted about a
skill's output is exactly what may be asserted about yours. Shape, arity, stop conditions,
whether a citation resolves. Not whether an answer is *good* — model output and human output
are both prose, and prose is not checkable.

If a lab cannot be written as a case, the lab is wrong.

## How they are marked, which is the ladder again

| Tier | Marks | Verdict | How |
|---|---|---|---|
| 1 · machine | shape, arity, refusal, whether citations resolve | **blocks** — you are not done | `tools/eval_assertions.py` |
| 2 · key | did you find the planted thing | **comments** — here is what you missed | the same assertions, against a known answer |
| 3 · you | the judgment calls, and the sentence you write at the end | **decides** | `## What good looks like`, after you have attempted it |

You will meet the ladder twice: once as the thing being taught, and once as the thing marking
you. That is deliberate, and tier 3 being yours is not a cop-out — **nothing here judges
whether your answer is good.** Lab 05's decoy is the clearest case: the obvious check is a
banned word, it fails the answer key, and fixing it would mean guessing from keywords whether
a sentence is a finding or an aside. That is asserting *whether a finding is correct*, which
`evals/README.md` says may never be asserted. So it is not asserted.

## Two rules the checker holds itself to

**A no-op scores nought.** `lab.py check NN` on an untouched checkout scores 0/N for every
lab, and `tests/test_labs_are_wired.py` fails the build otherwise — against a clean worktree,
so that having actually done a lab does not fail your build.

This was not free. The first run of `check 01` on an untouched tree scored **3/7**: `max_lines`
and `banned_tokens` are both vacuously true of a file that was never written, because nought
lines is under every limit and nothing forbidden is in a file nobody wrote. That is the
`semgrep --test --config` false green and the no-op engine, a third time, in a third place, and
it looked like success. Eight assertions carry an existence guard now, and the test is what
found them.

Its positive companion: every lab's own answer key, applied verbatim, scores full marks.
Without that, "scores nought" is also satisfied by a lab whose checks can never pass at all.

The pair has a second effect nobody designed and everybody should keep: **a lab can only assert
things a set of files can satisfy.** Lab 06's first draft graded `git log` and `git diff`, and
failed both ends at once — the answer key cannot produce a commit history, and an untouched
checkout passed two of the checks anyway, because there is no diff, so nothing forbidden is in
it. Between them the two tests said *this lab is asserting the wrong things*, which is more than
either says alone.

**The report says whose fault it is.** When a check about a *stop condition* fails — the
assistant answered its own questions, or skipped the stop line — the report says that is a
finding about your assistant rather than about you. A learner on a weaker host must not read
it as their own failure. It is genuinely worth knowing: it is the one thing
[`LEARN.md`](../LEARN.md) tells you to watch for when you try a skill.

## The answers

The answer keys stay with the instructor. After you attempt a lab,
`python3 tools/lab.py solution NN` prints `## What good looks like`: that is where the
reasoning is, and the reasoning is what transfers.

## What your work is, and what is ours

Your files — `pruned.md`, `yours.ini`, `test_yours.py`, `specs/LAB-*`, `reviews/LAB-*`, and
every `report.md` — are gitignored. They are yours to keep, share or throw away. The fixtures and
the briefs are tracked, because they are the material.

`report.md` is worth sharing. It carries your score, every check with its reason, and a
`## What I would do differently` section that nothing fills in for you. Post it somewhere a
colleague will see it; that is the only accountability a self-guided lab has.

---
lab: 06
title: Implement one criterion
segment: 07
needs: agent
minutes: 35
solution_into: specs
assertions:
  - name: sections_in_order
    path: "specs/LAB-106.drift.md"
    sections: ["## Outside the touchpoints", "## Struck out"]
    hint: "Both sections are always present, in this order. `none` is a valid body — it says the question was asked."
  - name: file_mentions
    path: "specs/LAB-106.drift.md"
    needles: ["criterion 1"]
    hint: "Commits are named by the criterion they serve, and the drift file records them. `fix views` is not a criterion."
  - name: file_mentions
    tier: 2
    path: "specs/LAB-106.drift.md"
    needles: ["ExportResponse"]
    hint: "The dataclass gained a field. It is thirty lines from the touchpoint and the touchpoints do not name it — that is drift, in the same file, for a different reason."
  - name: file_mentions
    tier: 2
    path: "specs/LAB-106.drift.md"
    needles: ["ROWS_PER_SECOND"]
    hint: "You added a constant the spec names and does not place. Where it lives is a decision, and an undeclared decision is the kind a reviewer cannot see."
  - name: banned_tokens
    tier: 2
    path: "specs/LAB-106.drift.md"
    section: "## Outside the touchpoints"
    tokens: ["none"]
    hint: "An empty drift section on THIS lab means you did not look — three separate things land outside a three-line touchpoints list."
---

## Brief

This is the step the lecture teaches and never shows: the middle, between a spec and a pull
request. Everything either side of it produces a file. For a long time this produced commits and
nothing else, which is why segment 07 was the only one with no artifact in a practice whose
organising rule is that everything becomes a file.

`spec.md` is one acceptance criterion — the smallest thing that can be implemented, and
therefore the smallest thing that can drift. Implement it with `build-slice`, test first.

Two things are being measured, and only one of them is the code:

1. **Did the criterion get implemented, with a test that proves it, without breaking the
   suite?** That is tier 1 and it is the easy half.
2. **Did you notice what you touched that the plan did not name?** That is the drift file, and
   it is the artifact this lab exists for.

## Start

```
make setup && source .venv/bin/activate
git checkout -b lab/106
./scripts/sync-skills.sh --print build-slice | pbcopy
```

Paste that in, then the spec and touchpoints from this directory. If the skills are installed,
`/build-slice` with `specs/LAB-106.md` is enough — copy the two fixtures to `specs/` first, the
paths the skill declares:

```
mkdir -p specs
cp course/labs/06-implement-one-criterion/spec.md        specs/LAB-106.md
cp course/labs/06-implement-one-criterion/touchpoints.md specs/LAB-106.touchpoints.md
```

Work on a branch off `main`, and run these yourself before the checker — they are the tier-3
half, and nothing below grades them:

```
python3 -m pytest -q                       # the whole suite, not just the file you touched
git log --oneline main..HEAD -- myapp tests    # does the log read as the spec?
git diff main..HEAD --name-only                # is legacy.py in there? it must not be
```

```
python3 tools/lab.py check 06
```

**What the checker grades, and what it deliberately does not.** It grades
`specs/LAB-106.drift.md`, because that is this lab's artifact. It does not grade your commits or
your diff, and the reason is worth thirty seconds: the first version of this lab did, with
`git log ... | grep -qi criterion` and a check that `tests/test_exports.py` appeared in the
diff. Both **passed on an untouched checkout** — there is no diff, so nothing forbidden is in
it, and the suite was already green. A check that passes when you have done nothing is the
third sighting of that shape in this repository, and `tests/test_labs_are_wired.py` caught it
before the lab shipped.

## What good looks like

**The implementation is about eight lines**, and it is not the point.

`ROWS_PER_SECOND` next to `SYNC_ROW_THRESHOLD` in `service.py`, a small helper that divides and
rounds up with a floor of one, the field added to `ExportResponse`, and the 202 branch in
`views.py` populating it. One commit: `criterion 1 · queued export says how long to wait`.

The test that proves it uses a row count that is **not** an exact multiple of the rate. The
criterion says "rounded up", and an exact multiple passes whether you rounded up, down, or not
at all — the same trap as lab 03, arriving from the specification side instead of the review
side. A criterion that is only tested where the arithmetic is exact is a criterion nobody
verified.

**The drift, which is the artifact.** Three things will pull you outside the touchpoints, and
what to do about each differs:

| What | Why it happens | Where it goes |
|---|---|---|
| `ExportResponse` — the dataclass gains a field | The touchpoints name `views.py:41`, the 202 branch. The dataclass is thirty lines above it in the same file | Declare it. Same file, different reason for changing — that is exactly the kind of change a reviewer cannot infer from a diff |
| `ROWS_PER_SECOND` as a new constant | The spec names it and does not say where it lives | Declare it, with the clause: *the threshold it divides already lives here* |
| `myapp/service/reports/legacy.py` | It calls the same builder and Out of scope names it | **Do not touch it.** If you did, the drift file is the least of it |

An empty `## Outside the touchpoints` on this lab means you did not look. All three of those
land outside a three-line touchpoints list, and the list is not wrong — grounding happened
before anyone had implemented anything, which is the whole reason drift is a thing that gets
recorded rather than a thing that gets prevented.

**What the drift file buys downstream, concretely.** `code-review` step 2 asks *what did this
touch that the plan never mentioned?* Without this file it infers that from the diff, which
finds a file appearing where the spec did not expect one — and does **not** find the file the
spec *did* expect, changed in a way nothing predicted. In the worked ticket that second kind is
precisely what broke: four files changed, all inside the plan, and
`myapp/service/reports/legacy.py` was not among them, which is exactly why it broke.

**The two-strike rule, which you may not hit and should know anyway.** If two corrections have
not made the criterion pass, stop, write the strike-out into the drift file, and re-spec. It is
the one rule in this repository that was taught in prose, in exactly one place —
`course/tickets/PROJ-142/06-git-log.txt` — and enforced nowhere, until it became a stop condition in a
skill. What is usually wrong at the second failure is the criterion, not the code: a criterion
nobody can satisfy twice running was never assertable, and the fix is upstream.

**Then throw the branch away.** `git checkout main && git branch -D lab/106`. The eight lines
were never the deliverable.

<!-- Worked example. In a real repo this is specs/PROJ-142.touchpoints.md. Cited paths resolve
     against tooling/myapp/, which is real and deliberately minimal.
     See ./README.md for the canon and the slide-path-to-real-path map. -->

# specs/PROJ-142.touchpoints.md

Output of the grounding pass: read-only exploration, every claim carrying a `path:line`. Slide 13
shows this block below the separator, with the last entry revealed on a second build step.

```
touchpoints - PROJ-142

tooling/myapp/api/exports/views.py:41           entry point
tooling/myapp/service/exports/service.py:88     query builder
tooling/myapp/tasks/queue.py:12                 async path
tooling/tests/test_exports.py                   3 tests exist

(!) tooling/myapp/service/reports/legacy.py:210
    shares the same query - out of scope,
    but will break
```

## This file gets read three times

It is the most reused artifact in the whole chain, which is the argument for grounding being its
own file rather than a paragraph inside the spec:

1. **Drafting** uses it to bound scope. You cannot size a change you have not looked at.
2. **Building** diffs against it. `git diff --stat` against this list is the only thing that
   catches silent scope creep — see `06-git-log.txt`.
3. **Reviewing** uses it to know where to look, and to know what "outside the plan" means.

## The line that matters

`tooling/myapp/service/reports/legacy.py:210` is not in the ticket. Nobody asked for it. It was found by
searching for other callers of the query builder at `service.py:88`, which is step 2 of the
grounding pass and the step most likely to get skipped because nothing looked risky.

It is marked `(!)` rather than added to the work: out of scope for this ticket, but it will break.
That distinction is the whole value of the mark. It tells a reviewer where to look, it bounds the
diff, and it converts a Friday-night incident into a conversation on a Tuesday.

## What is deliberately absent

Ten citations at most, and this has five. A grounding pass that lists every file a search matched
has produced a directory listing, not a map — and a map nobody reads bounds nothing.

Note also that `tooling/myapp/repo/` appears nowhere here. The export reads through the service layer, and
the architecture contract in `course/templates/python/importlinter.example.ini` is what guarantees it keeps
doing so when the obvious optimisation is to reach past it.

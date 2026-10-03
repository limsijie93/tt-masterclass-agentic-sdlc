<!-- Worked example. In a real repo this is reviews/PROJ-142.review.md. Cited paths resolve against
     tooling/myapp/, which is real and deliberately minimal.

     ONE OF THE THREE FINDINGS BELOW IS WRONG, ON PURPOSE. The lecture polls the room on
     which. Do not "fix" it. The answer, and why that particular error is the right one to
     plant, is in ./README.md under a collapsed section. -->

# reviews/PROJ-142.review.md

Tier 2 · fresh session · PR #319 · spec `specs/PROJ-142.md`

Reviewed against 2 acceptance criteria and 5 declared touchpoints. 4 files changed, all
inside the declared touchpoints. 5 candidates triaged to 3.

---

### 1 · blocking: the legacy report is now unbounded

`tooling/myapp/service/reports/legacy.py:210` · relates to: `Out of scope`, and the `(!)` touchpoint

`build_export_query()` gained a `chunk_size` parameter in this change
(`tooling/myapp/service/exports/service.py:88`). The parameter defaults to `None`, and `None` means no
chunking. `legacy.py:210` calls the same builder and was not updated, so a query that was
previously bounded by the old implementation's fixed page size is now unbounded.

The spec names this file under `Out of scope` and the touchpoints marked it `(!) shares the
same query - out of scope, but will break`. Both were right. The change shipped anyway.

**Suggested action:** make `chunk_size` required, or default it to the old page size rather
than to unbounded. A default that means "no limit" is a footgun aimed at every existing
caller.

---

### 2 · the async job's execution path has no test

`tooling/myapp/tasks/queue.py:12` · relates to: acceptance criterion 2

Criterion 2 — `Returns 202 + job id when async` — is tested at the view: the 202 and the job
id are asserted in `tooling/tests/test_exports.py:88`. The job's own execution is not. Nothing
exercises the branch at `queue.py:12` that runs the export inside the worker, so a failure
there surfaces as a job that never completes rather than as a test failure.

**Suggested action:** one test that runs the job body synchronously and asserts the artifact
it produces. The polling loop is already covered by the bulk-import tests and does not need
duplicating.

---

### 3 · criterion 1 may not be measured by its test

`tooling/tests/test_exports.py:41` · relates to: acceptance criterion 1

Criterion 1 is `CSV completes under 30s at 1M rows`. The implementation now streams the
response rather than building it in memory
(`tooling/myapp/api/exports/views.py:41` returns a streaming response).

A timer around a request that returns a streaming response stops when the response object is
returned — that is, at first byte — not when the last row has been written. So the assertion
appears to measure time-to-completion and in fact measures time-to-first-byte, which for a
streamed response is close to constant regardless of row count. The criterion would pass at
1M rows and at 100M.

**Suggested action:** drain the stream inside the timed block before asserting.

---

> Advisory — not a merge gate. This review cannot judge domain rules, authorization or tenancy
> scoping, architectural fit, or whether this feature should exist. A human decides.

2 further observations withheld — ask for the full list.

---

## Notes on the shape of this output, not its content

**Three findings, one blocking.** Five candidates were triaged down. The two that were dropped
are counted, not deleted — that line is what stops triage becoming quiet omission, and it is
also what lets a reviewer ask for more when they want it.

**Exactly one blocking marker, and only because there was something to block on.** On a clean
pull request this file has zero findings and says so. A contract that requires one blocking
finding forces the skill to manufacture one, and manufacturing a blocking finding on good code
is the fastest possible route to being muted.

**What is not here.** No score. No letter grade. No style comments — `ruff`, `mypy`,
`lint-imports` and `semgrep` already ran and blocked at tier 1, and a tier-2 finding about
import order is tier-2 attention doing tier-1 work.

**What it could not have found.** Whether the export endpoint should be tenant-scoped. Whether
a synchronous path should exist at all. Whether retiring the legacy report in Q4 makes finding
1 urgent or irrelevant. Those are the reviewer's, and the footer says so on every run rather
than leaving it to be inferred.

**One finding here is wrong**, and that is the most useful thing about this artifact. A tool
that is right three times out of three teaches the room to defer to it. Tier 2 comments, tier 3
decides — and the reason is on this page.

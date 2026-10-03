# PROJ-142 — a ticket, start to finish

One ticket runs through every chapter of the masterclass, so the room watches the same piece of work
transform rather than twelve disconnected demos. This directory is that ticket, in order.

**Just watched the lecture?** [`LEARN.md`](../../../LEARN.md) walks these files in order with what
to notice in each, plus what to do next. This page is the index and the canon.

Read it top to bottom. Every file names, in its header, where it would live in a real repo — the
numbered filenames here are for reading order, not a layout to copy.

| # | File | Chapter | What it is |
|---|---|---|---|
| 00 | `00-agents-draft.md` | 2.1 | The bloated draft a "generate AGENTS.md from the repo" prompt produces. `course/templates/AGENTS.md` is what it looks like pruned. |
| 01 | `01-ticket.md` | 0.2 | The ticket as received. Vague, and typical. |
| 02 | `02-interrogation.md` | 1.2 | Five capped questions, each carrying the assumption it hides, then the stop. |
| 03 | `03-answers.md` | 1.2 | A human's answers. The input that makes drafting possible. |
| 04 | `04-touchpoints.md` | 1.2 | Grounding output, with the `(!)` hazard nobody asked about. |
| 05 | `05-spec.md` | 1.3 | The drafted spec. In a real repo: `specs/PROJ-142.md`. |
| 06 | `06-git-log.txt` | 2.3 | Commits named by acceptance criterion, and the diff stat. |
| 07 | `07-pr-body.md` | 3.3 | The four reviewer aids, generated for PR #319. |
| 08 | `08-review.md` | 3.2 | Tier-2 output: three findings, one blocking. **One is wrong.** |
| 09 | `09-tests-that-lie.md` | 3.3 | A tautological test, and the honest rewrite. |
| 10 | `10-harvest.md` | 4.1 | Three findings read, **one** proposal. In a real repo: `harvest/PROJ-142.md`, written before the branch is deleted. |

## The canon

Every artifact in this directory agrees on the following. `tooling/tests/test_example_consistency.py`
enforces it, because the lecture shows these files one after another and this audience will spot a
mismatch on screen.

| Fact | Value |
|---|---|
| Ticket | `PROJ-142` |
| Title | `Export report times out` |
| Acceptance criterion 1 | `CSV completes under 30s at 1M rows` |
| Acceptance criterion 2 | `Returns 202 + job id when async` |
| Spec PR | `#318` |
| Implementation PR | `#319` |
| Files changed | 4 |

Commits, oldest first:

```
f01a22  spec + touchpoints
3e7d55  criterion 1 · stream csv
8c1b09  criterion 2 · async job
a4f2e1  criterion 2 · status route
```

**The arithmetic is the punchline.** Four files changed: `views.py`, `service.py`, `queue.py`,
`test_exports.py`. `reports/legacy.py` is *not* among them — which is exactly why it breaks.

## The fictional service

The paths below belong to `tooling/myapp/`, which is a real package in this repository and small on
purpose. Each slide shows the tail of a path; the artifacts here show the whole thing, so the
contracts in the root `.importlinter` actually govern them.

**Every `path:line` below resolves.** `tooling/tests/test_example_consistency.py` opens each one and
fails if the cited line does not hold what the artifact says it holds — so a reader who opens
`tooling/myapp/service/exports/service.py` at line 88 finds the query builder. Before `tooling/myapp/` existed
these citations agreed with each other and with nothing else, which is consistency rather than
correctness.

| On the slide | In these artifacts | Layer |
|---|---|---|
| `exports/views.py:41` | `tooling/myapp/api/exports/views.py:41` | `myapp.api` |
| `exports/service.py:88` | `tooling/myapp/service/exports/service.py:88` | `myapp.service` |
| `tasks/queue.py:12` | `tooling/myapp/tasks/queue.py:12` | — |
| `reports/legacy.py:210` | `tooling/myapp/service/reports/legacy.py:210` | `myapp.service` |
| `tooling/tests/test_exports.py` | `tooling/tests/test_exports.py` | — |

`myapp.repo` holds the data access the service layer calls. It is never imported from `myapp.api`,
and the contract is what guarantees that rather than a sentence in a document.

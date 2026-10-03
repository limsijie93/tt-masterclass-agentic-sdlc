# PROJ-207 — the second ticket, and why a second one exists

[`PROJ-142`](../PROJ-142/README.md) is the ticket the lecture runs on. This is the second chain,
and it is here to answer the question a sharp room asks about the first one: *did that work
because the process is good, or because the example was built to make it look good?*

The way to answer that is a different domain with the same mechanisms, where the mechanisms
produce a **different outcome**. Everything below is the same pipeline. The story it tells is not.

| # | File | What it is |
|---|---|---|
| 01 | `01-ticket.md` | The ticket as received. Two symptoms that look unrelated and are one bug. |
| 02 | `02-interrogation.md` | Five capped questions, each with the assumption it hides, then the stop. |
| 03 | `03-answers.md` | A human's answers. Question 4 is the one that changed the work. |
| 04 | `04-touchpoints.md` | Grounding output, with the `(!)` hazard nobody asked about. |
| 05 | `05-spec.md` | The drafted spec. In a real repo: `specs/PROJ-207.md`, opened as PR #341. |
| 06 | `06-git-log.txt` | Commits named by criterion, and the fifth file that did *not* break. |
| 07 | `07-pr-body.md` | The reviewer aids, generated for PR #342. |
| 08 | `08-review.md` | Tier-2 output: three findings, one blocking. **One is wrong.** |
| 09 | `09-tests-that-lie.md` | A circular test with no mock in it, and the honest rewrite. |
| 10 | `10-harvest.md` | Three findings read, **one** proposal — the one the ledger had already half-earned. |

There is no `00-agents-draft.md` here. The context-file draft is a repository-level artifact
shown once, in segment 05, and a second copy of it would be a second thing to keep true.

## The canon

Every artifact in this directory agrees on the following, and
`tooling/tests/test_example_consistency.py` enforces it for this chain exactly as it does for the first.

| | |
|---|---|
| Ticket | `PROJ-207` |
| Criterion 1 | **Entitlement change visible within 60s** |
| Criterion 2 | **Returns 403 + upgrade_url when not entitled** |
| Hazard (out of scope) | `tooling/myapp/service/billing/upgrade.py:44` |
| Spec PR / implementation PR | `#341` / `#342` |
| Commits | `c03b6a`, `5d2f18`, `91ca80`, `b7e4d2` |

## What this chain shows that the first one cannot

**The hazard does not bite.** In the export ticket, four files changed, all inside the plan, the
diff was clean — and the untouched fifth file broke anyway, because a shared function's
behaviour moved underneath it. Here the fifth file is untouched and does *not* break, because
the fix went to the call site instead of the shared signature.

Same shape of hazard. Opposite outcome. The difference is entirely upstream of the diff: it is
question 4 of the interrogation, answered by a human in about four minutes. That is the
strongest available argument that the grounding step is load-bearing rather than ceremonial,
and it is only visible when you have two tickets to compare.

**The bug cannot be fixed.** Two callers want opposite behaviour from one helper and both are
right. So there is no correct value for the shared default, the instance gets fixed at one call
site, and the residual risk — a third caller inheriting silently — is addressed by a rule rather
than by a patch. The export ticket's finding had a fix that was declined for teaching reasons.
This one has no fix at all, which is the more common case in real code.

**The ledger pays out.** `unbounded-export-query.yml` exists because a human caught something
once. `fail-open-entitlement.yml` exists because `harvest/ledger.md` was *already holding* that
finding when the same shape arrived somewhere else. The first chain can assert that the harvest
loop compounds. Two chains demonstrate it.


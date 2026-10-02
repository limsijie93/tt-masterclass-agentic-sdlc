# Where the claims come from

Every load-bearing claim in the lecture and in this repository, and what stands behind it. Some
rows say `unsourced`. That is the point of the file — a repository arguing that verification is
the bottleneck should not assert numbers it cannot attribute, and the honest fix is to make the
distinction visible rather than to quietly stop repeating them.

Read this before putting a figure on a slide or in a skill body.

## The table

| Claim | Asserted in | Source |
|---|---|---|
| The same pull request reviewed twice can produce different verdicts | `code-review/SKILL.md`, `README.md`, slide 29 script | **Semgrep 2025** — same prompt, same codebase, *"vastly different results"* |
| An AI reviewer's findings are mostly false positives; it is not an oracle | `08-review.md` (planted), slides 32–33 | **Semgrep 2025** — 14% true positive, 86% false positive |
| A long context file degrades what the agent does; keep it short | `README.md`, `templates/AGENTS.md`, `00-agents-draft.md` | **Drew Breunig, *How Long Contexts Fail*** — poisoning, distraction, confusion, clash |
| A flaky gate destroys trust in about a week | `README.md` ×2, `evals/README.md`, `code-review/SKILL.md` | **Graphite** — ~5% false positives had *"a corrosive effect on engineers' trust"*. Direction confirmed; "a week" is ours |
| Forty comments is how a review bot gets muted in two weeks | `code-review/SKILL.md` | **Graphite** — same source, same caveat: their conclusion was opt-in and asynchronous, never blocking |
| Layered defence is required because capability gaps are unpredictable | the tier ladder, `README.md` | **CS146S week 1, the Swiss Cheese Model** — see below |
| +98% more PRs merged · +91% longer review · flat DORA | slide 7 | `unsourced here` — on-slide attribution to *Faros AI telemetry, 2026* only |
| PR size +154% · AI PRs wait 4.6× longer to be picked up | review-ladder script | `unsourced here` — same |
| `AGENTS.md` is an open standard under the Linux Foundation's Agentic AI Foundation, read by 20+ agents, adopted in 60,000+ repositories | `templates/AGENTS.md`, slide 19 | `unverified` — not checked against a primary source |
| The skill spec shipped December 2025; OpenAI and Microsoft supported it within 48 hours; 30+ tools read it | segment 02 script | `unverified` — same |
| `semgrep` spans 30+ languages | `README.md`, `gates-by-stack.md` | Vendor claim, taken at face value. Low stakes: nothing here depends on the exact number |
| One semgrep rule cannot span two languages when its patterns use language-specific syntax | `.semgrep/README.md` | **Measured here.** The only claim in this repo with primary evidence in it |
| Six skills cost roughly 240 tokens of always-loaded context | `README.md` | Estimate, from the name-and-description bytes. Not measured against a tokeniser |

## The three that changed what we can say

These came out of the reading lists for **Stanford CS146S · The Modern Software Developer**
(Mihail Eric) — see `Prior art` in `README.md`. Each replaces an assertion this repo was making
on its own authority.

**Non-determinism, which slide 29 states as fact.** Semgrep pointed two coding agents at real web
applications and found that running *the exact same prompt on the exact same codebase* repeatedly
often produced vastly different results. That is the argument for "never let an agent be the merge
gate", and until now it was ours to prove and we had not.

<https://semgrep.dev/blog/2025/finding-vulnerabilities-in-modern-web-apps-using-claude-code-and-openai-codex/>

**The false-positive rate, which reframes a teaching device as the common case.** The same study:
one agent produced 46 findings at a **14% true positive rate**, the other 21 findings at 18%. By
vulnerability class the spread is instructive — best on IDOR at 22%, worst where taint has to
cross files and functions, 5% on SQL injection and 16% on XSS. So `08-review.md`'s planted false
positive is not a trick to make a poll work; one wrong finding in three is *better* than the
measured rate. Say that over slide 33 and the lesson lands harder.

**Why a context file must stay short.** The repo says to prune under sixty lines and argues it by
assertion — "the four-hundred-line file nobody reads". There is a named taxonomy for what actually
goes wrong: context **poisoning** (a wrong fact enters and is reused), **distraction** (volume
crowds out the instruction), **confusion** (irrelevant content is treated as relevant), and
**clash** (two parts of the context contradict). That is a better answer than "nobody reads it",
because it explains why a *rotted* context file is worse than none — the failure is poisoning, and
it is active rather than passive.

**And a name for the shape of the ladder.** CS146S week 1 frames model reliability with the Swiss
Cheese Model: gaps in capability are unpredictable and not correlated across layers, so defence has
to be layered rather than perfected. That is the missing half of the ladder's justification.
`README.md` argues the *ordering* — cheapest attention first — and never says why there are four
layers instead of one good one. This is why.

## Still unsourced, and staying that way until someone checks

The four reframe figures on slide 7 and in the review-ladder script carry an on-slide attribution
and nothing else in this repository. Do not add a citation for them without reading the primary
source: the numbers are the emotional core of the cold open, they are quoted at senior engineers,
and the lecture's own thesis is that a claim nobody verified is a preference wearing a number.

Two options, and both are fine: read the Faros report and add the row, or drop to the figures that
are now sourced. What is not fine is repeating them in a *new* place — a skill body, a template, a
README — because that multiplies an unverified claim into the artifacts people copy.

The `AGENTS.md` adoption figures and the skill-spec timeline are the same shape, and lower stakes
because nothing in the repo depends on them being exact.

## How to add a row

Claim, where it is asserted, source. If the source is a measurement someone here took, say so and
name the file that holds it — `.semgrep/README.md` is the model. If there is no source, write
`unsourced` and leave it; a row that says `unsourced` is doing its job.

**A sourced replacement for the four `unsourced` rows exists, in a draft opening that is not
yet the deck.** It carries sample sizes and methods rather than a bare attribution, and a
source-strength hierarchy — telemetry large-n, survey large-n, survey small-n, controlled
experiment, practitioner, institutional — which is a better structure than the table above. It
is deliberately not merged in: a citation copied from a draft is a citation nobody checked, and
this file exists to stop exactly that.

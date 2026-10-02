<!-- Copy to specs/<TICKET>.md in your own repo.

     The six headings the lecture shows are the first six below. The rest are fields that
     earned their place by being the ones teams kept discovering they needed — keep them,
     drop them, but decide deliberately rather than by omission.

     One rule governs everything here: per-ticket detail in this file, per-repo truth in
     AGENTS.md, never both. The test is "would this still be true for the next ticket?" -->

# specs/<TICKET>.md · PR #<n>

| | |
|---|---|
| Ticket | `<TICKET>` |
| Owner | @<name> |
| Drafted | <YYYY-MM-DD> |
| Inputs | `specs/<TICKET>.answers.md`, `specs/<TICKET>.touchpoints.md` |

## Goal

<One sentence. A user-visible outcome, not an implementation. No "refactor", no "add a
service", no class names.>

## Acceptance criteria

<Numbered. Each names an observable and, where numeric, a number. Write the assertion before
you write the sentence — if you could not write an assertion for it, rewrite it.

Banned words, because no assertion exists for any of them: properly, performant, fast, clean,
robust, user-friendly.>

1. <criterion>
   - measured how: <the assertion, in one clause>
   - from: <the answer or touchpoint this came from>

## Out of scope

<MANDATORY. Never empty, minimum three entries. This is the field that prevents the most
rework and the one teams omit most often — an empty one is how three unasked-for features
arrive in the diff.

Draw from: options the answers rejected; every (!) hazard in the touchpoints; and the
adjacent thing a reader would otherwise assume is included.>

- <thing> — <why not, in one clause>

## Touchpoints

<Copied unchanged from specs/<TICKET>.touchpoints.md, citations intact. Do not re-explore.>

## Open questions

<Non-blocking only. Anything blocking goes back to interrogation.
This section MUST be empty before implementation starts.>

## Done when

<The observable state that ends the ticket.>

---

<!-- Fields below are not on the slides. They exist because teams kept finding they needed
     them. Delete the ones that do not apply to your work rather than leaving them blank. -->

## Constraints

<Rules this change must not break, especially the ones a machine enforces. Naming the
architecture contract here means the implementer meets it in the spec rather than in CI.>

## Known dependents / blast radius

<Every (!) hazard from the touchpoints, with the decision taken about each one. A hazard
found and not decided is worse than one never found: it looks handled.>

## Data and scale assumptions

<The numbers the criteria are measured at, and where they came from. "1M rows" is only a
criterion if someone can say why 1M.>

## Rollout

<Flag, migration, backfill, order of operations. Anything that makes this more than one
deploy belongs here, and probably means the spec should be split.>

## Observability

<What you will look at to know it worked in production, named specifically.>

## Assumptions

<What was assumed rather than asked, because it fell below the five-question cap. This is
where the questions that did not make the cut go, so they can be corrected in review
instead of discovered in an incident.>

## Commit slices

<One per acceptance criterion. This is what makes the pull request reviewable criterion by
criterion, and it is a two-minute habit that takes twenty minutes off someone else's day.>

- [ ] criterion 1 · <slice>

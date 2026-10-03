<!-- The STANDING half. Kept short on purpose: a 60-line template on every pull request is
     the 400-line context file all over again, and it gets skimmed for the same reason.
     The per-PR generated half is pasted between the GENERATED markers at the bottom. -->

Spec: `specs/<TICKET>.md`

## Acceptance criteria

<!-- Paste from the spec, one checkbox each, VERBATIM. Not a generic checklist — these are
     this pull request's criteria, and a reworded one makes the reviewer's comparison manual.
     If a box is unchecked, say why here rather than leaving it blank. -->

- [ ]

## Touchpoints

- Declared: `specs/<TICKET>.touchpoints.md`
- Actual: <!-- git diff --stat -->
- Outside the declared list, and why:

## Tier 1

- [ ] All the checks in `AGENTS.md` under Commands pass locally.
- [ ] **No test was modified in order to make an implementation pass.** If a test was wrong,
      it is called out above and was changed deliberately, not to get to green.

## For the reviewer

Once tiers 1 and 2 have run, three questions are left:

1. Does it satisfy every acceptance criterion?
2. What did it touch that the spec never mentioned?
3. Are the tests real, or tautologies?

## Evals

- [ ] If this PR changes a skill body, `AGENTS.md`, or a guard: paste the eval pass rate,
      before and after. The suite reports rather than blocks — **you** are the gate.
      See [`tooling/evals/README.md`](../tooling/evals/README.md).

## Harvest

- [ ] Did anything in this change belong somewhere permanent? If so, link the follow-up.
      `.github/skills/harvest` reads the review and drafts these; it proposes, you commit.
      A first sighting is logged in `harvest/ledger.md` and proposed on the second.

| What you noticed | Where it goes |
|---|---|
| A mistake the agent repeated | `AGENTS.md` |
| A field the spec kept missing | `course/templates/spec.md` |
| Something a human caught that a machine could have | a ruff rule, an `.importlinter` contract, a `.semgrep/` rule, or a test |
| A procedure used more than twice | a new skill in `.github/skills/` |
| A way an agent broke a skill's own contract, seen twice | an eval case |

<!-- BEGIN GENERATED -->
<!-- END GENERATED -->

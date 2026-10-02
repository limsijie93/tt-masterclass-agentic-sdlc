---
name: gates-draft
allowed-tools: Read, Grep, Glob, Write
description: >
  Run after stack-profile, to turn the prose rules in a context file into the executable
  checks that enforce them. Emits baselined configs for the detected stack and never turns
  anything on repo-wide.
---

## Purpose

Prose in a context file is a suggestion. An agent follows it most of the time, and "most of
the time" is not a standard — it is a coin flip repeated a hundred times a sprint.

The move is to take anything you can state as a machine-checkable rule out of prose and into
a config file. The same rule then does two jobs: it constrains the agent, and it blocks the
pull request. One source of truth, two enforcement points.

The reason this is a skill rather than a template is that **the decision ports and the
executable does not**. Which standards deserve a machine check is the same question in every
language. The tool that checks them is different in each one, and the differences are not
cosmetic — some have a layering primitive and some need one rule per direction; some can
expire a suppression and some cannot. A template can only ever be one language's answer.
A procedure can be every language's.

## When to use / when not to

Use once a stack profile exists and a human has corrected it, and once the prose rules you
want enforced are written down.

Do not use:

- Before a profile exists. Generating a config for a guessed stack is how a repository ends
  up with a checker nobody can run.
- To decide *which* standards matter. Read them out of the context file, or ask. This turns
  decisions into checks; it does not make them.
- To fix existing violations. Baseline them and stop.

## Inputs required

1. `gates/stack-profile.md`, with a human's corrections applied.
2. The repository's context file, for the prose rules to be made executable — in particular
   the architecture rule and any convention stated as a prohibition.

**Capabilities.** Reads files; writes configuration under `gates/draft/`; **runs no commands**. It drafts the checks and never turns one on — the baselining step is a human's, deliberately, and a skill that could run the checker is a skill that could decide the baseline.

## Procedure

1. **Verify the profile.** If it still carries `[ stopped - waiting for a human ]` and no
   corrections, stop: you would be generating from an unreviewed guess.
   *Done when:* the profile names a stack and at least one candidate gate.

2. **Take each prose rule and ask one question: could a machine check this?** Layering,
   public API surface, complexity ceiling, type discipline, security invariants,
   duplication. Anything that survives becomes a gate. Anything that does not stays prose,
   and say which ones those were — a rule that cannot be checked is not a failure, it is a
   thing tier 3 will always have to look at.
   *Done when:* every prose rule is marked executable or explicitly not.

3. **Choose the tool per standard, for the detected stack.** Prefer what the profile says is
   already present over introducing something new: an unused config in the repo is cheaper
   to turn on than a tool nobody has installed.
   *Done when:* every executable rule names a tool that runs on this stack.

4. **Write the contract, and baseline it in the same breath.** For every gate, emit the
   config *and* its baseline of existing violations, taken from the profile's counts. Every
   baseline entry carries a ticket reference.
   **Never emit a gate switched on repo-wide.** Turning a checker on across an established
   repository produces thousands of violations, nobody triages them, and the tool is
   discredited permanently. This kills more of these rollouts than any other single mistake.
   *Done when:* no gate is emitted without a baseline, or without an explicit note that the
   repository has zero existing violations.

5. **Make each suppression expire.** For every tool, find the setting that turns an
   unnecessary suppression into a failure, and switch it on. Without it a baseline is a
   permanent exemption with better paperwork; with it, fixing the code forces deleting the
   suppression. If a tool has no such setting, say so plainly rather than implying the
   ratchet exists.
   *Done when:* every gate names its ratchet, or states that it has none.

6. **Emit the hook config and the Commands block together.** They must name the same tools,
   reading the same configs. Not the same arguments — scope differs by design — the same
   tools.

7. **Stop.** A human prunes, decides the rollout order, and opens the pull request.

## Output contract

Written under `gates/`, one file per artifact, plus a summary:

```
gates/draft/<contract config>        the architecture contract, baselined
gates/draft/<tool config>            lint, type and complexity rules, baselined
gates/draft/pre-commit-config.yaml   the hooks, staged and scoped
gates/draft/AGENTS.commands.md       the Commands block to paste into the context file
gates/draft/README.md                what was generated, what was baselined, what to do first
```

`gates/draft/README.md` names, for every gate: the standard, the tool, the baseline size, the
ratchet setting, and the rollout order. Nothing is emitted outside `gates/draft/` — a skill
that writes directly into a repository's root config has taken a decision that was not its
to take.

## Stop conditions

- No stack profile, or an uncorrected one.
- A stack the profile could not identify.
- A prose rule you cannot map to any tool on this stack. Say which rule, and leave it prose.
- A gate whose baseline you cannot size. Emit the config disabled, with a note, rather than
  emitting it enabled and hoping.
- More than one ecosystem in the profile. Emit one draft per ecosystem, never a merged one.

## Anti-patterns

- Emitting a gate with no baseline, on a repository that is not new.
- Emitting a baseline with no ratchet, so it never shrinks.
- Introducing a tool the team does not use, because it is the one you know best.
- Writing into the repository's live config rather than a draft directory.
- Fixing violations to make a gate pass on the way in. That is a second change, hidden
  inside the first, and it will be reviewed as neither.
- Assuming two ecosystems can share one rule because they share a tool. Some can; the
  negations usually cannot. Check before claiming it.
- Treating the reference tables as exhaustive. They cover the ecosystems someone verified.

<!-- Per-ecosystem specifics — tools, config shapes, baseline mechanisms and which ratchets
     exist — are in references/gates-by-stack.md.

     That pointer is HERE and not in the Procedure on purpose. No step above depends on it:
     the procedure is a sequence of decisions, and an assistant with no repository access
     can still work through it from a pasted context file. The reference makes the answers
     precise for the two ecosystems this repo has worked examples for. -->

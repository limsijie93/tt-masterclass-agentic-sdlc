---
name: stack-profile
allowed-tools: Read, Grep, Glob, Write
description: >
  Run once per repository, before writing any gates. Detects the toolchain, the module
  layout and the checks that already exist, citing file:line for each, then stops for a
  human to correct it.
---

## Purpose

Every executable gate is language-specific. That is not a flaw in the design — a machine
check has to parse the language to check anything — but it means the first question is
always "what is this repository, actually?", and the answer is more surprising than teams
expect. Repos have a stated stack and a real one, and the gap between them is where a
generated config goes wrong.

This skill answers that question from evidence rather than from what someone remembers.
It writes down what it found, cites where it found it, and stops. Nothing is generated
from a guess.

The output is consumed once, at adoption, by the skill that drafts the gates. It is not a
per-ticket artifact and does not need regenerating unless the repository changes shape.

## When to use / when not to

Use before introducing gates to a repository that does not have them, or before adding a
language to one that does.

Do not use:

- Per ticket. This describes a repository, not a change.
- To decide *what* to enforce. That is a conversation between people, and its output is
  prose in the context file. This only reports what could enforce it.
- On a repository whose gates already exist and pass. There is nothing to profile; read the
  configs instead.

## Inputs required

1. Read access to the repository. No write access is needed and none should be used.
2. The repository's context file, if one exists, so the profile can note where the prose
   rules and the detected reality already disagree.

**Capabilities.** Reads files; writes `gates/stack-profile.md`; **runs no commands**. This one is worth stating plainly: the skill detects a toolchain, and the obvious way to detect a toolchain is to run it. It does not. Every claim is cited `file:line` from a file that was already there, which is what makes the profile checkable by the human who has to correct it.

## Procedure

1. **Find the manifests.** Look for the files that declare a toolchain, not the source
   files. Cite each with `path:line`:
   dependency manifests, lockfiles, formatter and linter configs, type-checker configs,
   test-runner configs, CI definitions, and any existing hook configuration.
   *Done when:* every claim about the stack points at a file that declares it.

2. **Record what is already enforced, and where.** A repository with a linter config and no
   CI step has a preference, not a gate. Say which of the two you found, per tool, because
   the difference decides whether the next step is adding a rule or adding enforcement.
   *Done when:* each tool found is marked as configured, enforced locally, enforced in CI,
   or configured but unenforced.

3. **Find the module layout.** The top-level source directories and the dependency
   direction that appears to hold between them. Do not assert an intended architecture —
   report the shape you observe and let a human name it.
   *Done when:* the layout is listed, with a note on any directory whose role is unclear.

4. **Estimate the debt, do not fix it.** For each standard that could be enforced, report
   roughly how many existing violations there would be. This is the number that decides
   between baselining and enforcing outright, and getting it wrong is what makes a rollout
   fail on day one.
   *Done when:* every candidate gate carries an order-of-magnitude count, or an explicit
   "not measured".

5. **Note the mismatches.** Anywhere the context file's prose and the evidence disagree —
   a command that no longer exists, a convention nothing enforces, a claim about coverage —
   list it. Aspirational rules are the worst content a context file can carry, and this is
   the cheapest moment to find them.

6. **Emit and stop.** Do not write a gate. Do not fix a violation. Do not add a hook. A
   human reads this, corrects it, and only then is anything generated.

## Output contract

`gates/stack-profile.md`, sections in this order:

```
# stack-profile - <repository>

## Stack
<language and runtime>   evidence: <path>:<line>

## Toolchain
<tool>  <role>  <configured | enforced locally | enforced in CI | unenforced>
        evidence: <path>:<line>

## Module layout
<directory>   <apparent role>

## Candidate gates
<standard>  <tool that could enforce it>  <approximate existing violations>

## Mismatches
<what the context file claims>  vs  <what the evidence shows>

[ stopped - waiting for a human ]
```

Every path is repo-relative. Where a stack is genuinely mixed, list each one rather than
picking a winner; a monorepo with two ecosystems needs two sets of gates, and flattening
that here hides it.

## Stop conditions

- **Always**, immediately after emitting.
- No manifest found anywhere. Say so and stop; a repository whose toolchain cannot be
  identified from its files needs a person, not a generated config.
- More than two ecosystems detected. Report them and stop — that is a monorepo question,
  and one profile cannot answer it well.
- The evidence contradicts the context file on something load-bearing, such as the test
  command. Report it as the first mismatch and stop.

## Anti-patterns

- Reporting the stack from the README rather than from a manifest. READMEs describe the
  repository someone intended.
- Asserting an intended architecture. You can see that `api` imports `service`; you cannot
  see whether that was the plan.
- Skipping the violation counts because they are tedious to estimate. That number is the
  single most decision-relevant thing in the file — it is the difference between a rollout
  that works and one that gets the tool thrown out in week two.
- Fixing anything. A profile that edits the repository is no longer a profile.
- Picking one language in a mixed repository to keep the output tidy.

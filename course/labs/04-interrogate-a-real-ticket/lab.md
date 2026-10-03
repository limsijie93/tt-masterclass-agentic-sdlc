---
lab: 04
title: Interrogate a real ticket
segment: 03
needs: agent
minutes: 25
solution_into: specs
assertions:
  - name: max_questions
    path: "specs/LAB-104.answers.md"
    limit: 5
    hint: "More than five questions is a sign this is more than one ticket — and a list nobody can answer in one sitting does not get answered."
  - name: every_question_has
    path: "specs/LAB-104.answers.md"
    fields: ["blocks", "assumes"]
    hint: "`assumes` is the field that makes a question answerable in seconds instead of in a meeting. Every question carries both."
  - name: every_answer_line_empty
    path: "specs/LAB-104.answers.md"
    hint: "Every `answer:` line must be empty. A skill that answers its own questions produces a confident artifact built on guesses."
  - name: contains_sentinel
    path: "specs/LAB-104.answers.md"
    hint: "The stop line is missing. Stopping is the mechanism — without it this is just a faster way to guess."
  - name: max_citations
    path: "specs/LAB-104.touchpoints.md"
    limit: 10
    hint: "Ten citations is a map. Sixty is a directory listing."
  - name: citations_resolve
    path: "specs/LAB-104.touchpoints.md"
    hint: "A cited line does not exist. This is the hallucination check, and it is the reason grounding is a separate step."
  - name: file_mentions
    tier: 2
    path: "specs/LAB-104.touchpoints.md"
    needles: ["tools/guard_test_edits.py"]
    hint: "Grounding did not find the thing the ticket is about."
  - name: file_mentions
    tier: 2
    path: "specs/LAB-104.touchpoints.md"
    needles: [".pre-commit-config.yaml"]
    hint: "You found one of the two places this runs. There is a second, and which one failed changes the whole fix."
  - name: file_mentions
    tier: 2
    path: "specs/LAB-104.touchpoints.md"
    needles: ["(!)"]
    hint: "No hazard marked. Search for what else shares this machinery before you conclude there is nothing."
---

## Brief

`ticket.md` is a real gap in this repository, reported the way real gaps are reported: by
somebody annoyed, in a thread, on a Friday. It is not badly written. It is missing everything
an implementer needs, and not through carelessness — the reporter was describing what happened,
not specifying a change.

Run `spec-interrogate` on it. You are looking for two things:

1. **Does it ask you something you had not thought of?**
2. **Does it stop?**

If it answers its own questions, the stop condition is the part that failed — and that is a
finding about your assistant, not about you. The checker below will say so when it happens.

This lab needs an agent and, depending on your setup, an API key. Labs 01 to 03 do not.

## Start

Paste-first works; installing is an optimisation.

```
./scripts/sync-skills.sh --print spec-interrogate | pbcopy
```

Paste that into whatever you use, then paste `course/labs/04-interrogate-a-real-ticket/ticket.md`
underneath it. If the skills are installed, `/spec-interrogate` is enough.

It must produce two files, at these exact paths:

```
specs/LAB-104.answers.md
specs/LAB-104.touchpoints.md
```

Both are gitignored. Do not answer the questions — the point is the shape of what came back,
and whether the grounding pass found the thing it had to find.

```
python3 tools/lab.py check 04
```

## What good looks like

**The questions.** Roughly these, in some order, each with the guess it hides:

| The question | The assumption it hides |
|---|---|
| Which of the two timings failed — write time or commit time? | that both were running, and that the guard is one thing |
| Is the fix to flip the existing guard to enforcing, or to close a hole in what it can see? | that a guard reporting and a guard blocking are the same feature |
| Does it block, or ask? | that "make it work" means "block" |
| What counts as weakening — is `assert True` the whole class, or the visible instance? | that the rule is about a string rather than about assertion count |
| Should the same rule cover a shell edit? | that it can |

Anything about naming, formatting or style is a question that failed the ranking: being wrong
about it changes the wording, not the implementation.

**The touchpoints, and the one that matters.** A shallow pass finds `tools/guard_test_edits.py`
and `.claude/settings.json` and stops, because those two are where the word "guard" appears.
They are one timing. The same script is also a `pre-commit` hook —
`.pre-commit-config.yaml`, `entry: python3 tools/guard_test_edits.py --staged` — and that is
the timing that runs on every host, for every developer, including the ones not using an
assistant at all.

Which one failed changes the entire fix, and you cannot ask the question until grounding has
found both. That is the order the skill insists on and the reason for it: *you cannot ask a
good question about a change you have not looked at.*

**The hazard.** `tools/guard_protected_paths.py` is wired through the same `PreToolUse` entry
in the same settings file, and it is the guard that protects the first guard. Change how the
hook is invoked and you have changed both. Nobody asked about it; you find it by searching for
what else shares the machinery, which is step 2 of the skill and the step people skip because
nothing looked risky.

There is a second hazard worth a `(!)` if you found it: `allowManagedHooksOnly: true` in
`course/templates/managed-settings.example.json` stops project-committed hooks from running at all.
The enterprise control that makes a guard trustworthy is the control that switches this guard
off.

**And the answer to the ticket, which you were right not to write.** The guard ships
`GUARD_MODE=log` by default. It saw the edit, reported it, and blocked nothing — on purpose,
because `course/templates/README.md` says measure for a week before enforcing and this is our own
gate. So "I thought it was on?" is answerable in one line by someone who knows, and no amount
of implementation would have been the right first move. That is what the interrogation buys:
four minutes of a human's time, spent before the work rather than after it.

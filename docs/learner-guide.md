# Learner's guide

How this repository maps onto the masterclass, lesson by lesson. Each lesson follows the same
four steps:

- **Watch** the lesson.
- **Read** the worked example.
- **Do** the lab, where there is one.
- **Copy** what you want into your own repository.

New here? [`LEARN.md`](../LEARN.md) helps you choose how deep to go. Skills not installed yet?
See [Install the skills](../README.md#install-the-skills).

## The whole masterclass on one page

One ticket, `PROJ-142` "Export report times out", runs through all three blocks.

```mermaid
flowchart LR
    start(["Start: LEARN.md"]) --> intro["Lessons 0–2<br/>Why the bottleneck moved"]
    intro --> b1
    subgraph b1["Block 1 · Specs"]
        direction TB
        l3["3 · The portable skill file"] --> l4["4 · Interrogate, then ground"] --> l5["5 · The spec as a reviewable artifact"]
    end
    b1 --> b2
    subgraph b2["Block 2 · Quality"]
        direction TB
        l6["6 · The repo contract"] --> l7["7 · Architecture rules"] --> l8["8 · Build in slices"]
    end
    b2 --> b3
    subgraph b3["Block 3 · Review"]
        direction TB
        l9["9 · The review ladder"] --> l10["10 · Fresh-context review"] --> l11["11 · Make the human's job smaller"]
    end
    b3 --> close["12 · Manager view + the harvest loop"]
    close --> yours(["Your own repo"])
```

## The four steps, and where each lives

```mermaid
flowchart LR
    watch["Watch<br/>the lesson"] --> read["Read<br/>example/PROJ-142/"]
    read --> doit["Do<br/>labs/ via tools/lab.py"]
    doit --> copy["Copy<br/>.github/skills/ · templates/ · examples/"]
    watch -. "replay a demo yourself" .-> demos["docs/demos.md"]
```

| Step | Where | How |
|---|---|---|
| Watch | the masterclass video | Each lesson below names the demos it shows |
| Replay a demo | [`docs/demos.md`](demos.md) | The exact commands, so you can run any demo yourself |
| Read | [`example/PROJ-142/`](../example/PROJ-142/) | Files `00`–`10`, in the order the lessons use them |
| Do | [`labs/`](../labs/) | `python3 tools/lab.py start NN`, then `check NN`, then `solution NN` |
| Copy | [`.github/skills/`](../.github/skills/), [`templates/`](../templates/), [`examples/`](../examples/) | Into your own repository, one pull request at a time |

## The chain the ticket goes through

Every skill reads the file the one before it wrote, and two of them stop for a human. This is
the backbone of lessons 4 to 12.

```mermaid
flowchart LR
    subgraph specs["Block 1 · Specs"]
        direction TB
        ticket["Ticket<br/>01"] --> si["spec-interrogate<br/>02 · 04"]
        si --> h1{{"A human answers<br/>03"}}
        h1 --> sd["spec-draft<br/>05"]
    end
    subgraph quality["Block 2 · Quality"]
        direction TB
        bs["build-slice<br/>06 · one commit per criterion"]
    end
    subgraph review["Block 3 · Review"]
        direction TB
        pb["pr-brief<br/>07"] --> cr["code-review, fresh session<br/>08"]
        cr --> h2{{"A human decides"}}
        h2 --> hv["harvest<br/>10"]
    end
    sd --> bs --> pb
    hv -. "a rule, a context-file line, a skill" .-> repo[("AGENTS.md · .semgrep/ · skills")]
    repo -. "the next ticket starts smarter" .-> ticket
```

The numbers are the files in [`example/PROJ-142/`](../example/PROJ-142/): `01-ticket.md`,
`02-interrogation.md`, `03-answers.md`, `04-touchpoints.md`, `05-spec.md`, `06-git-log.txt`,
`07-pr-body.md`, `08-review.md` and `10-harvest.md`.

Two of them are wrong on purpose: `08-review.md` has one false finding, and
`09-tests-that-lie.md` opens with a test that checks nothing. Find both yourself before the lessons reveal them.

## Opening · lessons 0–2

```mermaid
flowchart LR
    l0["0 · The bottleneck moved"] --> l1["1 · Cold open: the wrong table"] --> l2["2 · One ticket, three blocks"]
    l1 --- f1["01-ticket.md<br/>myapp/repo/analytics.py"]
    l2 --- f2["docs/reference-card.md"]
```

| Lesson | Read | Do | Copy |
|---|---|---|---|
| 0 · The bottleneck moved | [`LEARN.md`](../LEARN.md) | — | — |
| 1 · Cold open | [`01-ticket.md`](../example/PROJ-142/01-ticket.md), then [`myapp/repo/analytics.py`](../myapp/repo/analytics.py), the table the agent wrongly picks. Demo D1 | — | — |
| 2 · The map | [`docs/reference-card.md`](reference-card.md), "The chain" | — | Pin the card up |

## Block 1 · Specs: lessons 3–5

```mermaid
flowchart LR
    l3["3 · Skill file"] --> l4["4 · Interrogate, then ground"] --> l5["5 · Spec as artifact"]
    l3 --- r3["SKILL.template.md"]
    l4 --- r4["02 · 03 · 04"]
    l4 --- d4["Lab 04"]
    l5 --- r5["05-spec.md<br/>templates/spec.md"]
```

| Lesson | Read | Do | Copy |
|---|---|---|---|
| 3 · The portable skill file | [`SKILL.template.md`](../.github/skills/_template/SKILL.template.md), and one real skill, [`spec-interrogate`](../.github/skills/spec-interrogate/SKILL.md). Demo D11 | Try one skill: [`LEARN.md`](../LEARN.md) step 2 | [Install the skills](../README.md#install-the-skills) |
| 4 · Interrogate, then ground | [`02-interrogation.md`](../example/PROJ-142/02-interrogation.md), [`03-answers.md`](../example/PROJ-142/03-answers.md), [`04-touchpoints.md`](../example/PROJ-142/04-touchpoints.md). Demo D13 | [Lab 04 · Interrogate a real ticket](../labs/04-interrogate-a-real-ticket/lab.md) | `spec-interrogate` |
| 5 · The spec as a reviewable artifact | [`05-spec.md`](../example/PROJ-142/05-spec.md). Demo D14 | — | [`templates/spec.md`](../templates/spec.md), `spec-draft` |

## Block 2 · Quality: lessons 6–8

```mermaid
flowchart LR
    l6["6 · Repo contract"] --> l7["7 · Architecture rules"] --> l8["8 · Build in slices"]
    l6 --- d6["Lab 01: prune the context file"]
    l7 --- d7["Lab 02: make the gate bite"]
    l8 --- d8["Lab 06: implement one criterion"]
    l6 --- c6["templates/AGENTS.md"]
    l7 --- c7[".importlinter · .pre-commit-config.yaml · .semgrep/"]
```

| Lesson | Read | Do | Copy |
|---|---|---|---|
| 6 · The repo contract | [`00-agents-draft.md`](../example/PROJ-142/00-agents-draft.md) (166 lines generated), then [`examples/python/AGENTS.md`](../examples/python/AGENTS.md) (75 kept). Demos D3, D12 | [Lab 01 · Prune the context file](../labs/01-prune-the-context-file/lab.md) | [`templates/AGENTS.md`](../templates/AGENTS.md) |
| 7 · Architecture rules the agent can't argue with | [`.importlinter`](../.importlinter), [`.pre-commit-config.yaml`](../.pre-commit-config.yaml), [`.semgrep/`](../.semgrep/). Demos D4, D8, D10, D17 | [Lab 02 · Make the gate actually bite](../labs/02-make-the-gate-bite/lab.md) | `stack-profile`, then `gates-draft`, on your repo |
| 8 · Build in slices, watch the churn | [`06-git-log.txt`](../example/PROJ-142/06-git-log.txt). Demo D5 | [Lab 06 · Implement one criterion](../labs/06-implement-one-criterion/lab.md) | `build-slice` |

Labs 01–03 need nothing installed. Labs 04–06 need an assistant, so they come last.

## Block 3 · Review: lessons 9–11

```mermaid
flowchart LR
    l9["9 · Review ladder"] --> l10["10 · Fresh-context review"] --> l11["11 · Human's job smaller"]
    l9 --- r9[".github/workflows/review.yml"]
    l10 --- d10["Lab 05: review a planted PR"]
    l11 --- d11["Lab 03: the test that lies"]
    l11 --- r11["07-pr-body.md<br/>09-tests-that-lie.md"]
```

| Lesson | Read | Do | Copy |
|---|---|---|---|
| 9 · The review ladder | [`review.yml`](../.github/workflows/review.yml), [`pull_request_template.md`](../.github/pull_request_template.md), [`CODEOWNERS`](../.github/CODEOWNERS) | — | The PR template and `CODEOWNERS` |
| 10 · Tier 2: fresh-context review | [`08-review.md`](../example/PROJ-142/08-review.md). One finding is wrong: which one? Demo D6 | [Lab 05 · Review a planted pull request](../labs/05-review-a-planted-pr/lab.md) | `code-review` |
| 11 · Make the human's job smaller | [`07-pr-body.md`](../example/PROJ-142/07-pr-body.md), [`09-tests-that-lie.md`](../example/PROJ-142/09-tests-that-lie.md). Demos D7, D9, D15 | [Lab 03 · The test that lies](../labs/03-the-test-that-lies/lab.md) | `pr-brief` |

## Close · lesson 12

```mermaid
flowchart LR
    finding["A finding in a review"] --> harvest["harvest proposes a home"]
    harvest --> ctx["AGENTS.md line"]
    harvest --> rule[".semgrep/ rule"]
    harvest --> skill["A new skill"]
    rule --> catch["Caught by a machine next time"]
```

| Lesson | Read | Do | Copy |
|---|---|---|---|
| 12 · What the manager sees, and the harvest loop | [`10-harvest.md`](../example/PROJ-142/10-harvest.md), [`harvest/ledger.md`](../harvest/ledger.md), and the rule the loop produced, [`.semgrep/unbounded-export-query.yml`](../.semgrep/unbounded-export-query.yml). Demo D16 | Run `harvest` at the end of your next real ticket | `harvest`, [`templates/governance.example.md`](../templates/governance.example.md) |

## After the masterclass

```mermaid
flowchart LR
    a["1 · One AGENTS.md, under 60 lines, with an owner"] --> b["2 · pre-commit on changed lines"] --> c["3 · One architecture contract"]
```

Three pull requests, each under an hour. The short version is in the README's
[90-minute path](../README.md#the-90-minute-path-if-you-only-do-one-thing). Want more practice? Work through
the second worked ticket, [`example/PROJ-207/`](../example/PROJ-207/), the same way.

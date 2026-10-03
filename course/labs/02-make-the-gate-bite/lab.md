---
lab: 02
title: Make the gate actually bite
chapter: "2.2"
needs: no-agent
minutes: 20
solution_into: course/labs/02-make-the-gate-bite
assertions:
  - name: file_mentions
    path: "course/labs/02-make-the-gate-bite/yours.ini"
    needles: ["type = forbidden"]
    hint: "A layers contract cannot express this rule. A different contract type can."
  - name: command_exits
    cmd: "cd course/labs/02-make-the-gate-bite && lint-imports --config yours.ini 2>&1 | grep -q 'shop.api.bad'"
    code: 0
    needs: ["lint-imports"]
    hint: "Your contract has to name shop.api.bad as a violation. Right now it does not."
  - name: command_exits
    tier: 2
    cmd: "cd course/labs/02-make-the-gate-bite && test -f yours.ini && ! (lint-imports --config yours.ini 2>&1 | grep -q 'shop.api.good')"
    code: 0
    needs: ["lint-imports"]
    hint: "Your contract flags shop.api.good, which is the CORRECT path through the layers. Read what it says about indirect imports."
---

## Brief

`shop/` is three layers and four modules. `shop/api/bad.py` imports `shop/repo/queries.py`
directly, skipping the service layer — the exact thing "make the export faster" produces when
nobody is looking, and the thing slide 22 and the PROJ-142 spec both say `lint-imports` catches.

Run the contract as the slide writes it:

```
cd course/labs/02-make-the-gate-bite
lint-imports --config layers-only.ini
```

It says **KEPT**.

That is not a bug in the fixture and it is not a bug in import-linter. It is the gap between a
rule someone believes is enforced and a rule that is enforced, and it sat in this repository
for weeks — on a slide, in a spec, and in a demo script — inside a project whose entire thesis
is that a standard a machine cannot check is a preference. It was a preference.

**Write the contract that catches it.** Then check it does not catch anything else.

## Start

Activate the toolchain first, or `lint-imports` is not on your path:

```
make setup                 # once
source .venv/bin/activate
```

Then:

```
cd course/labs/02-make-the-gate-bite
lint-imports --config layers-only.ini        # KEPT. Read shop/api/bad.py and be annoyed.
cp layers-only.ini yours.ini                 # edit yours.ini, not the fixture
```

Add to `yours.ini` the contract that fails on `shop.api.bad`. The import-linter documentation
lists the contract types; you want the one that expresses "these modules may never import
those", not the one that expresses an ordering.

**Then run it again and read every line of the output, not just the exit code.** There is a
second failure mode here and it is the one that gets gates deleted. The check below will tell
you if you hit it, but seeing it yourself in the output is the lab.

```
./lab check 02
```

## What good looks like

```ini
[importlinter:contract:api-never-calls-repo]
name = The API layer goes through the service layer
type = forbidden
source_modules =
    shop.api
forbidden_modules =
    shop.repo
allow_indirect_imports = true
```

**Half one: `layers` does not forbid skipping a layer.** It forbids a *lower* layer importing a
*higher* one — `repo` importing `api`. `api -> repo` runs with the grain of the ordering, so
the contract is satisfied. Every team that writes a layers contract believes it bought the
no-skipping rule. It did not, and nothing tells you, because a contract that is KEPT looks
exactly like a contract that is working.

The rule you wanted needs a `forbidden` contract, which is about pairs of modules rather than
about an order.

**Half two, and this is the one that costs you the gate.** Without `allow_indirect_imports`,
`forbidden` reports **indirect** chains too. So it flags

```
shop.api.good -> shop.service.orders -> shop.repo.queries
```

which is the correct path through the layers and the entire reason the architecture exists.
Your gate now fails on healthy code. What happens next is not a debate about the contract: the
first person in a hurry deletes it, and they are right to, because a gate that fires on correct
code is worse than no gate. A flaky gate destroys trust in about a week; a wrong one destroys
it in one pull request.

`allow_indirect_imports = true` says *direct imports only*. One line, and it is the difference
between a rule and an obstacle.

**How this was actually found.** Not by reading the documentation — by adding the import to the
real application and watching `lint-imports` pass. The claim had been on a slide and in a spec
for weeks. Nothing but running it against real code could have shown it, which is the argument
for the application existing at all. The root `.importlinter` carries both contracts with the reasoning in comments.

**The transferable version.** Before you write the artifact that claims a gate enforces
something, make the gate fail. A gate you have only ever seen pass is a gate you have not
tested — you have tested that it compiles.

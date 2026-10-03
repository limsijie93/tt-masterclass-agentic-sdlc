# Convenience only. AGENTS.md is the source of truth for what the gates are.
#
# That is the inverse of the usual advice, and it is deliberate. The primary reader of the
# Commands section is an agent, and `make tier1` is one line an agent can RUN but cannot
# READ INTO: when it fails, the agent sees a failed make target rather than `mypy`, and
# cannot reason about which gate broke or re-run just that one. Raw tool names are also what
# a new engineer has to learn eventually.
#
# So: the tool names live in AGENTS.md, and these targets are a shortcut for humans who
# would rather type four characters.

.PHONY: help setup tier1 lint types test skills rules mutate fmt labs

help:
	@echo "setup   create .venv and install the pinned tier-1 toolchain"
	@echo "tier1   every deterministic check, in the order they should run"
	@echo "lint    ruff format + ruff check"
	@echo "types   mypy"
	@echo "test    pytest"
	@echo "skills  the skill portability + chain checks, and symlink drift"
	@echo "rules   the semgrep rules' own unit tests"
	@echo "mutate  the mutation gate on tooling/myapp/, scoped to what this branch changed"
	@echo "fmt     ruff format, writing changes"
	@echo "labs    the self-guided labs, and where you are in them"

# The dependency set was implicit until the labs needed it: `make tier1` wants ruff, mypy,
# semgrep, lint-imports and pytest, and nothing said so. requirements-dev.txt pins them to the
# same versions .pre-commit-config.yaml does.
setup:
	python3 -m venv .venv
	.venv/bin/pip install --quiet --upgrade pip
	.venv/bin/pip install --quiet -r requirements-dev.txt
	@echo "done. activate with: source .venv/bin/activate"

tier1: lint types skills rules test mutate

lint:
	ruff format --check tooling/scripts tooling/tools tooling/tests
	ruff check tooling/scripts tooling/tools tooling/tests

types:
	mypy tooling/scripts tooling/tools tooling/tests

test:
	pytest -q

skills:
	python3 tooling/scripts/lint_skills.py --check-agents
	./tooling/scripts/sync-skills.sh --check

# NOTE the exact form. `semgrep --test --config .semgrep/ .semgrep/` reports success even
# with a deliberately broken fixture — see .semgrep/README.md.
rules:
	semgrep test .semgrep/

# Diff-scoped against origin/main, per the 24 September decision. On main the diff is empty
# and this is a no-op; on a branch it runs only the tooling/myapp/ files that branch touched, which
# is two seconds rather than the twenty-six a whole-package run costs. If origin/main is not
# fetched the tool says so and falls back to every file — slow, still correct, never silent.
mutate:
	python3 tooling/tools/mutate.py --since origin/main

fmt:
	ruff format tooling/scripts tooling/tools tooling/tests

labs:
	./lab

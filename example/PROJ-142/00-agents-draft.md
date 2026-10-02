<!-- Worked example, and the one file here that is deliberately BAD.

     This is the first draft a "read the repo and write me an AGENTS.md" prompt produces for
     the fictional myapp service. It is 150-odd lines and about 12 of them are load-bearing.
     examples/python/AGENTS.md is what it looks like after pruning.

     Segment 05 says the pruning IS the teaching. Diff this against examples/python/AGENTS.md
     and the teaching is a diff rather than an assertion. Do not "improve" this file. -->

# AGENTS.md — generated draft

## Project Overview

myapp is a Python web application. It is built with Python and uses a modern Python stack. The
project follows standard Python conventions and best practices. The codebase is organised into
several modules, each with its own responsibility. This document provides guidance for AI agents
working in this repository.

## Repository Structure

```
myapp/
  api/            API layer
    exports/      Exports API
      views.py    Views for exports
      urls.py     URL routing for exports
    reports/      Reports API
    accounts/     Accounts API
    __init__.py
  service/        Service layer
    exports/      Export services
      service.py  Export service
    reports/      Report services
      legacy.py   Legacy report service
    accounts/
    __init__.py
  repo/           Repository layer
    exports.py
    accounts.py
    __init__.py
  tasks/          Background tasks
    queue.py      Task queue
  settings/       Settings
tests/            Tests
docs/             Documentation
vendor/           Vendored dependencies
scripts/          Scripts
migrations/       Database migrations
```

## Technology Stack

- Python 3.12.4
- ruff 0.6.2 for linting and formatting
- mypy 1.11.1 for type checking
- pytest 8.3.2 for testing
- import-linter 2.0 for architecture checks
- PostgreSQL 15.4 for the database
- Redis 7.2 for the task queue

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`
6. Run the migrations
7. Start the development server

## Commands

- `pytest -q` runs the test suite
- `ruff check .` lints the codebase
- `ruff format .` formats the codebase
- `mypy myapp` type-checks the codebase
- `lint-imports` checks the architecture contracts
- `python manage.py runserver` starts the development server
- `python manage.py migrate` applies migrations
- `python manage.py makemigrations` creates migrations
- `python manage.py shell` opens a shell
- `python manage.py collectstatic` collects static files
- `pip install -r requirements.txt` installs dependencies
- `pip freeze > requirements.txt` updates dependencies

## Architecture

The application follows a layered architecture. The API layer handles HTTP requests and
responses. The service layer contains the business logic. The repository layer handles data
access. The task layer handles background processing.

Layers should generally be respected. The API layer should usually call the service layer, and
the service layer should usually call the repository layer. Try to avoid calling the repository
layer directly from the API layer where possible.

## Coding Standards

- We always write tests for new code.
- All functions have docstrings.
- We use conventional commits for all commit messages.
- Code coverage is maintained above 90%.
- We follow PEP 8.
- Use meaningful variable names.
- Keep functions small and focused.
- Prefer composition over inheritance.
- Follow the single responsibility principle.
- Don't repeat yourself (DRY).
- Write self-documenting code.
- Handle errors gracefully.
- Use type hints where appropriate.
- Avoid premature optimisation.
- Comment complex logic.

## Testing

Tests live in `tests/`. Run them with pytest. Write unit tests for individual functions and
integration tests for workflows. Mock external dependencies. Aim for high coverage. Test edge
cases. Use fixtures for shared setup. Follow the arrange-act-assert pattern.

## Python Best Practices

- Use list comprehensions where they are more readable than loops
- Prefer `pathlib` over `os.path`
- Use context managers for resources
- Use f-strings for formatting
- Avoid mutable default arguments
- Use `enumerate` instead of manual counters
- Use `dataclasses` for simple data containers

## Git Workflow

Create a feature branch. Make your changes. Write tests. Open a pull request. Get a review.
Merge. Delete the branch.

## Deployment

The application is deployed to production via the CI pipeline.

---

## What got cut, and why

The pruned result is `examples/python/AGENTS.md`, 46 lines of content. This draft is about 150. Almost none of
the deletions were about length — each one fails a specific test.

| Cut | Why |
|---|---|
| **Project Overview** | "myapp is a Python web application built with Python" changes nothing an agent does. It is tokens spent on a sentence the file's own existence already implies. |
| **Repository Structure** | The agent can list the directory. Restating it means it is now wrong the first time someone adds a module, and a stale map is worse than no map. |
| **Technology Stack versions** | `ruff 0.6.2`, `PostgreSQL 15.4`. These rot within a month, and then the file is confidently lying. Versions belong in the lockfile, which cannot drift. |
| **Development Setup** | Belongs in the README, for humans. An agent is not creating your virtualenv. |
| **Commands**, trimmed 12 → 5 | Kept the tier-1 gates. Cut `makemigrations`, `collectstatic`, `pip freeze` — an agent that runs those unprompted has caused a problem, not solved one. |
| **Architecture**, rewritten | "Layers should generally be respected… try to avoid where possible" is a suggestion, and a suggestion is a coin flip repeated a hundred times a sprint. The rewrite states the rule flatly and names the file that enforces it. |
| **"We always write tests"** | The repo has 61% coverage. This is aspirational, and aspirational rules are the worst possible content: you are describing a codebase that does not exist, and the agent believes you. |
| **"All functions have docstrings"** | They do not. Same failure. |
| **"We use conventional commits"** | `git log` says otherwise. Same failure. |
| **"Coverage above 90%"** | It is 61%. Three aspirational claims in one section is how a context file loses an agent's trust in the only way that matters — silently. |
| **Coding Standards**, 15 → 4 | Kept the four that are specific to this codebase and checkable. Cut DRY, SOLID, "meaningful variable names", "avoid premature optimisation" — generic advice the model already has, spending your context window to tell it something it knows. |
| **Python Best Practices** | Every line is in the training data. Delete the whole section. |
| **Git Workflow / Deployment** | Generic, and not what an agent needs mid-task. |
| **Added: the fixture gotcha** | Not in the draft, because a generator cannot know it. `tests/test_exports.py` is slow on purpose and someone will "fix" it by shrinking the fixture, destroying the thing under test. This is the single most valuable line in the pruned file, and a human had to write it. |
| **Added: the no-editing-tests rule** | Also not in the draft. The agent will try it, so the prohibition has to be explicit. |

That last pair is the point of the whole exercise. Generation gets you a starting draft in
thirty seconds. **The value is in what a human adds and removes afterwards** — and the two most
useful lines in the final file were not in the generated one at all.

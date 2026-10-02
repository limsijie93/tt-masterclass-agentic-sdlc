<!-- WORKED EXAMPLE — Python. Copy to AGENTS.md at your repository root.

     The stack-neutral skeleton is templates/AGENTS.md. This file is that skeleton filled in
     for the fictional `myapp` Python service, so it is consistent with
     examples/python/importlinter.example.ini and the example/PROJ-142 chain.

     The TypeScript equivalent is examples/typescript/AGENTS.md. Neither is more canonical
     than the other — they are two fills of one shape, which is the point of the shape.

     You do not have to write this by hand. `.github/skills/gates-draft` generates the
     Commands and Architecture sections for whatever stack it finds.

     SLIDE 19 QUOTES THE BODY BELOW VERBATIM. Do not reword it without updating the deck in
     the same pull request.

     Slide 19's card shows three commands (pytest, ruff check, lint-imports). Segment 08's
     tier-1 line names five. The SIX below are what is actually enforced by
     examples/python/pre-commit-config.yaml — the slide's card and the tier-1 line are both
     earlier, shorter drafts. If the slide is updated, update it to six.

     This list is not maintained by hand-checking. tools/check_commands_sync.py fails the
     build if the tool set here and the tool set in the matching pre-commit config diverge,
     and it caught semgrep missing from this section on its first run.

     TARGET: under 60 lines for what you COPY — this instructional comment is not part of it.
     If a line does not change what an agent does, delete it. The failure mode is the
     400-line file nobody reads, and a rotted context file is worse than none because it
     teaches the agent to lie about your codebase. -->

# AGENTS.md · reviewed in PR, owned by @<name>

## Commands

Run these before showing me any code. Fix what they report, then tell me what you changed
and what you could not fix.

```
ruff format .
ruff check . --fix
mypy myapp
lint-imports
semgrep scan --config .semgrep/ --error
pytest -q
```

## Architecture

`myapp.api` → `myapp.service` → `myapp.repo`, never the reverse.

This is not advice. It is a contract in `.importlinter`, it fails the build, and it is the
same rule you are reading — one source of truth, two enforcement points.

`myapp.tasks` may call `myapp.service`. It may not call `myapp.api`.

## Conventions

- Typed throughout. `mypy` runs strict on changed files.
- No bare `except`.
- No data-layer calls above `myapp.service`. Views ask the service; the service asks the repo.
- Query builders take an explicit chunk size. Defaults that mean "unbounded" are how a report
  page falls over at scale.

## Gotchas

- Migrations autogenerate on boot in development. A stray model change becomes a migration you
  did not ask for.
- `tests/test_exports.py` uses a generated 1M-row fixture. It is slow by design; do not "fix"
  it by shrinking the fixture, because the row count is the thing under test.

## Do not touch

- `vendor/`
- Generated protobuf modules (`*_pb2.py`, `*_pb2_grpc.py`)
- Any test, in order to make an implementation pass. If a test is wrong, say so and stop.
  A suite edited into greenness is worse than no suite.

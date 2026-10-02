<!-- WORKED EXAMPLE — TypeScript. Copy to AGENTS.md at your repository root.

     The same skeleton as templates/AGENTS.md, and the same fill as
     examples/python/AGENTS.md, for a TypeScript service. Read the two fills side by side:
     the sections are identical, the commands are not, and that is the entire relationship
     between a portable shape and a non-portable toolchain.

     `.github/skills/gates-draft` generates the Commands and Architecture sections from
     whatever `stack-profile` detected. Then prune by hand — the pruning is the part that
     matters.

     TARGET: under 60 lines for what you copy. -->

# AGENTS.md · reviewed in PR, owned by @<name>

## Commands

Run these before showing me any code. Fix what they report, then tell me what you changed
and what you could not fix.

```
prettier --write .
eslint --fix --max-warnings 0 --report-unused-disable-directives
tsc --noEmit -p tsconfig.json
depcruise --config .dependency-cruiser.cjs src
semgrep scan --config .semgrep/ --error
vitest run
```

## Architecture

`src/api` → `src/service` → `src/repo`, never the reverse.

This is not advice. It is a contract in `.dependency-cruiser.cjs`, it fails the build, and it
is the same rule you are reading — one source of truth, two enforcement points.

`src/tasks` may call `src/service`. It may not call `src/api`.

Note: dependency-cruiser has no single "layers" primitive, so the ordering above is three
`forbidden` rules rather than one block. Same rule, more lines.

## Conventions

- Typed throughout. `tsc --strict`, and `noUncheckedIndexedAccess` is on.
- Suppress with `@ts-expect-error`, never `@ts-ignore`. The first expires once the underlying
  error is gone; the second never does, which makes it permanent debt with no owner.
- No data-layer calls above `src/service`. Handlers ask the service; the service asks the repo.
- Query builders take an explicit `chunkSize`. A default meaning "unbounded" is how a report
  page falls over at scale.

## Gotchas

- `vitest run` uses a generated 1M-row fixture in the export tests. It is slow by design; do
  not "fix" it by shrinking the fixture, because the row count is the thing under test.
- `tsc` checks the whole project, so it cannot be scoped to changed files. A green pre-commit
  does not mean an untouched file still compiles — CI is the backstop.

## Do not touch

- `node_modules/`, `dist/`
- Generated clients (`src/generated/`)
- Any test, in order to make an implementation pass. If a test is wrong, say so and stop.
  A suite edited into greenness is worse than no suite.

# Gates by stack

The prose-to-executable table, per ecosystem. Tier-3 disclosure: nothing loads this at
startup, and no step of any skill's procedure depends on it — read the row for the stack
`stack-profile` detected, ignore the rest.

Covers **Python** and **TypeScript / JavaScript**. Those are the two this repo has worked
examples for, and a reference file that names a tool nobody verified is worse than a missing
row. Add a column when you have somewhere to point.

---

## The shape that ports

Six standards worth enforcing. **This list is the portable part** — the decision about what
deserves a machine check is the same in every language. Only the right-hand columns change.

| Standard | Prose version (weak) | Python | TypeScript / JS |
|---|---|---|---|
| Layering / dependency direction | "api never imports from repo" | `import-linter` | `dependency-cruiser` |
| Public API surface | "don't use internal modules" | `ruff` TID + `banned-api` | `dependency-cruiser` + `eslint no-restricted-imports` |
| Complexity ceiling | "keep functions small" | `ruff` C901 | `eslint complexity` |
| Type discipline | "add type hints" | `mypy --strict` | `tsc --strict` |
| Security invariants | "validate input" | `semgrep` | `semgrep` *(same tool)* |
| Duplication | "DRY" | `jscpd` | `jscpd` *(same tool)* |

Two of the six are the same tool in both columns. Semgrep covers 30+ languages and jscpd is
language-agnostic by design, so the "custom org rules" layer — the most valuable one, because
nobody else can write it for you — needs no new tool when you add a language.

**It still needs a new rule.** See the semgrep section below: sharing the tool is not sharing
the pattern, and assuming otherwise fails in a way that flags correct code.

---

## Layering

The one worth doing first, because it is the standard teams argue about most and the one
prose is worst at holding.

|  | Python | TypeScript / JS |
|---|---|---|
| Tool | `import-linter` | `dependency-cruiser` |
| Config | `.importlinter` (INI) or `pyproject.toml` | `.dependency-cruiser.cjs` |
| Layers primitive | **Yes** — `type = layers`, one block for the whole order | **No** — express as one `forbidden` rule per illegal direction |
| Baseline | `ignore_imports`, one line per violation | `options.exclude.path` |
| **Ratchet** | `unmatched_ignore_imports_alerting = error` | **None built in** |
| Worked example | `course/templates/python/importlinter.example.ini` | `course/templates/typescript/dependency-cruiser.config.cjs` |

**The asymmetry matters and is easy to miss.** import-linter has a single `layers` contract
that expresses a whole ordering; dependency-cruiser needs N rules for N illegal directions, so
three layers is three rules. And import-linter's ratchet — an ignore that no longer matches
anything fails the build, so the suppression deletes itself — has no dependency-cruiser
equivalent. A dependency-cruiser baseline is a permanent exemption unless you build the
ratchet yourself against a committed violation count.

Do not describe these as equivalent when porting. They enforce the same rule with different
guarantees.

## Type discipline

|  | Python | TypeScript / JS |
|---|---|---|
| Tool | `mypy` | `tsc` |
| Strict switch | `strict = true` | `"strict": true` |
| Baseline | `[[tool.mypy.overrides]]` + `ignore_errors`, per module | `exclude` by path, or a second looser tsconfig |
| **Ratchet** | `warn_unused_ignores = true` | `@ts-expect-error` *(expires by design)* |
| Diff-scoped | `mypy --follow-imports=silent <changed>` | `tsc` is whole-project; scope via `tsc --build` and project refs |

**TypeScript's ratchet is a suppression choice, not a setting.** `@ts-expect-error` fails once
the error it suppresses is gone; `@ts-ignore` never expires. So the ratchet is: use
`@ts-expect-error` everywhere and ban the other with eslint's `ban-ts-comment`. That is the
direct analogue of `RUF100` and `warn_unused_ignores`, and it is the single highest-value line
in a TypeScript gates setup.

**Python diff-scopes cleanly; TypeScript does not.** `tsc` type-checks a project, not a file
list, so "only the changed files" is not really available. Lean harder on the baseline.

## Complexity, duplication, secrets, formatting

|  | Python | TypeScript / JS |
|---|---|---|
| Format | `ruff format` | `prettier` |
| Lint | `ruff check` | `eslint` |
| Complexity | `ruff` C901, `[tool.ruff.lint.mccabe]` | `eslint` `complexity` rule |
| Unused suppression ratchet | `RUF100` | `eslint --report-unused-disable-directives` |
| Duplication | `jscpd` | `jscpd` |
| Secrets | `detect-secrets` | `detect-secrets` |
| Tests | `pytest` | `vitest` / `jest` |
| Changed-line coverage | `diff-cover` | `jest --changedSince` + `diff-cover` on lcov |

`eslint --report-unused-disable-directives` is the third member of the ratchet family, after
`RUF100` and `warn_unused_ignores`. **All three are the same idea: make the suppression itself
expire.** If you take one thing from this file into a new language, find that language's
version of this line first.

## Custom org rules

Same tool both columns: **`semgrep`**. This is the row worth the most and the one people skip.
A rule you write because a human caught something once beats anything from a registry, because
it encodes a mistake your team actually makes.

**One rule per language, not one rule for both — and this is worth measuring rather than
assuming.** Semgrep spans 30+ languages, so declaring
`languages: [python, typescript, javascript]` on a single rule looks like the obvious move. It
silently breaks negations:

| Same patterns, different `languages:` | Findings on the Python fixture |
|---|---|
| `[python]` | lines 12, 17 — **correct** |
| `[python, typescript, javascript]` | lines 12, 17, 22, 27 — **22 and 27 are the `# ok:` cases** |

The cause is that a pattern matches real syntax. `chunk_size=$N` is a Python keyword argument;
the TypeScript equivalent is a property in an object literal. A negation written for one
grammar cannot hold for the other, and when it silently stops matching, the rule flags correct
code — the failure mode that gets a tool muted.

So what ports is the **decision** and the **triage**, never the pattern. The two rules share an
id stem, a message and a `rule-family` tag; each keeps its own patterns and its own fixture.

Worked examples: `.semgrep/unbounded-export-query.yml` (Python) and
`.semgrep/ts/unbounded-export-query.yml` (TypeScript). Both are unit-tested, and both were
verified by sabotage rather than by passing.

## The framework that holds it together

`pre-commit` is **not** a Python tool, despite the name and the ecosystem it came from. It
manages hooks written in Python, Node, Go, Rust, Ruby and Docker, and it is the reason the
tier-1 layer ports even though none of the tools inside it do.

Worked examples: `course/templates/python/pre-commit-config.yaml`,
`course/templates/typescript/pre-commit-config.yaml`. Note how similar they look — that similarity is
the portable part.

---

## Rolling any of this out

Do not switch a checker on across an established repository. Read
[`course/templates/README.md`](../../../../course/templates/README.md) first — that trap kills more of these
adoptions than any other single mistake, and the ratchet lines above are what make a baseline
shrink instead of ossify.

# examples/

One directory per ecosystem. Each is the same set of shapes from [`templates/`](../templates/),
filled in with a real toolchain.

**Neither is canonical.** They are two fills of one shape, and having two is the only way to
show which parts of the shape actually port.

| | Python | TypeScript / JS |
|---|---|---|
| Context file | `python/AGENTS.md` | `typescript/AGENTS.md` |
| Architecture contract | `python/importlinter.example.ini` | `typescript/dependency-cruiser.config.cjs` |
| Lint / type / complexity | `python/pyproject.toml` | `typescript/tsconfig.gates.json` |
| Hooks | `python/pre-commit-config.yaml` | `typescript/pre-commit-config.yaml` |

`tools/check_commands_sync.py` checks each directory on its own terms: the tools named in that
ecosystem's `AGENTS.md` Commands must be the tools its `pre-commit-config.yaml` enforces.
Comparing them *across* ecosystems would be meaningless, so it does not.

## Read the two side by side

That is what these are for. Three things become obvious that no amount of prose establishes:

**The structure is identical.** Both hook configs have the same six tier-1 hooks in the same
order, the same `stages`, the same `pass_filenames` choices, and the same two language-agnostic
repos at the bottom. Both context files have the same sections. That similarity is the portable
part, and it is the whole argument for `templates/` existing.

**The tools share nothing.** Not one linter, formatter, type checker or test runner is the same.
Only `semgrep`, `detect-secrets` and `pre-commit` itself appear in both columns.

**The differences are not cosmetic.** Three that cost something when porting, each called out in
the files themselves:

- `import-linter` has a `layers` primitive expressing a whole ordering; `dependency-cruiser`
  needs one rule per illegal direction, so three layers is three rules.
- `import-linter` can expire a baseline entry once the violation is fixed;
  `dependency-cruiser` cannot, so its baseline is permanent unless you build the ratchet.
- `mypy` can check a file subset; `tsc` checks a project, so the TypeScript column cannot
  diff-scope its type check and leans harder on the baseline instead.

## Adding an ecosystem

A directory with an `AGENTS.md` and a `pre-commit-config.yaml`. `check_commands_sync.py` picks
it up automatically, and skips any directory missing either file — so a partial addition fails
nothing while you work on it.

Then add a column to
[`gates-by-stack.md`](../.github/skills/gates-draft/references/gates-by-stack.md) — but only
for tools you have actually run. **A reference file that names the wrong tool is worse than a
missing row**, because someone will trust it.

## You should not be writing these by hand

`.github/skills/stack-profile` detects what a repository is; `.github/skills/gates-draft`
writes the stack-specific parts. These directories are what its output should look like once a
human has pruned it.

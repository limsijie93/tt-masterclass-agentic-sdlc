# course/templates/

**Stack-neutral shapes** to copy into your own repository. Nothing here names a language,
because the shape of a contract ports and its content does not.

Filled-in versions live in [`python/`](python/) and [`typescript/`](typescript/) — one
directory per ecosystem, each one the same shapes with a real toolchain in them. Neither ecosystem is more canonical than
the other; they are two fills of one shape, which is the whole point of having a shape.

You should not fill these in by hand. `.github/skills/stack-profile` detects what your repo
actually is and `.github/skills/gates-draft` writes the stack-specific parts. That is the
division this repo is built around: **the procedure is portable, the executable is not.**

Nothing here runs against this repo, even though `tooling/myapp/` now exists: these files are
stack-neutral shapes, and the live versions of them are elsewhere (the root `.importlinter`,
the root `.pre-commit-config.yaml`). So every file here is illustrative, and each carries a
header saying what to rename it to.

## Copy in this order

The order matters, because each step makes the next one cheaper and because the first three
are under an hour each.

| # | Copy | To | What it buys |
|---|---|---|---|
| 1 | `AGENTS.md` | `AGENTS.md` at your repo root | Every agent reads the same repo truth. Generate the Commands and Architecture sections with `gates-draft`, prune below 60 lines, put a name in the H1. |
| 2 | `pre-commit-config.example.yaml` | `.pre-commit-config.yaml` | Tier 1, on the developer's machine, scoped to changed files. |
| 3 | your stack's config from [`course/templates/`](./) | your project config | The rules the gates enforce, in one place, so they cannot drift. |
| 4 | your stack's architecture contract from [`course/templates/`](./) | `.importlinter` / `.dependency-cruiser.cjs` | The layering rule you argue about most, as a check that fails the build. |
| 5 | `CODEOWNERS.example` | `.github/CODEOWNERS` | A named owner, so the context file does not rot. |
| 5b | `managed-settings.example.json` | a system path — see below | Turns the repo's guards from a convention into a control. Needs an administrator, not a pull request. |
| 6 | `spec.md` | `specs/<TICKET>.md` per ticket | The plan becomes reviewable before code exists. |
| 7 | `governance.example.md` | `docs/agentic-governance.md` | Visibility, then limits, then four metrics — and the trust boundary, which is the row nobody else claims. Last on purpose: every row needs a month of measurement or a named owner, and both are cheaper once 1–6 are real. |

## Read this before you turn anything on

**Turning a checker on across an established repository produces thousands of violations,
nobody triages them, and the tool is discredited permanently.** This kills more of these
rollouts than any other single mistake. `mypy --strict` switched on repo-wide on day one is
how the initiative dies in week two.

There are three ways through, and they are not equally good:

1. **A baseline in a reviewed config file** — `per-file-ignores`, `[[tool.mypy.overrides]]`,
   `ignore_imports`. Best, because the baseline shrinks visibly in pull-request diffs and
   somebody has to look at it.
2. **A baseline in a generated file** — acceptable, but it is invisible debt. Nobody reads it.
3. **Diff-scoped checking** — only the lines that changed. Necessary for speed, but it leaves
   the existing debt unmeasured, so it is the optimisation and not the strategy.

Use all three, in that order of preference.

**Then make the suppression expire.** This is the part teams miss, and it is three lines of
config:

| Tool | The line |
|---|---|
| ruff | `RUF100` in `select` — an unnecessary `noqa` becomes a failure |
| mypy | `warn_unused_ignores = true` |
| import-linter | `unmatched_ignore_imports_alerting = error` |

All three are the same idea: once the underlying problem is fixed, the suppression itself
starts failing the build, so it gets deleted. Without them a baseline is just a permanent
exemption with better paperwork.

## A gentler first step

Before adding any gate, spend a week measuring. `ruff check . --exit-zero --statistics` tells
you the shape of the problem without writing to a single file. `ruff check --add-noqa` is the
opposite — it edits every offending file, and a 4,000-file commit is a poor first impression
for an initiative you want people to like.


---

## Enterprise: settings a developer cannot override

`.claude/settings.json` in a repository is a **convention, not a control.** It is overridable by
`.claude/settings.local.json`, and it is deletable in a pull request. That is fine for a
convention — but if the answer to "what stops someone turning the guards off" is "we'd notice in
review", you have a preference, not a gate. This repo makes that distinction constantly
(`stack-profile` step 2: a linter config with no CI step is a preference).

The thing that makes it a control is a **managed settings file**, deployed by an administrator
to every machine. Claude Code applies managed settings above every other level, and nothing a
user, project, or `--settings` value sets overrides them.

`managed-settings.example.json` is the shape. It is the one template here that **cannot be
verified inside this repo** — it is not read from a repository at all — so the values below were
checked against the published documentation rather than by running them.

### Where the file goes

| OS | Path |
|---|---|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux and WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` |

**Not `C:\ProgramData\ClaudeCode\`.** That is a legacy path and is explicitly not read. It is
the kind of detail that produces a policy everyone believes is deployed and which was never
loaded — so verify enforcement after deploying rather than assuming.

There are other delivery mechanisms — MDM profiles, an `HKLM\SOFTWARE\Policies\ClaudeCode`
registry value, and server-managed settings from the console. Only server-managed settings reach
a cloud session; a file on the developer's disk does not.

### The three locks

| Key | Effect |
|---|---|
| `allowManagedPermissionRulesOnly` | Only managed permission rules apply. Without it, `permissions.allow` **merges** across scopes, so a local file can widen what the policy allows. |
| `allowManagedHooksOnly` | Restricts which hooks run to the managed ones. |
| `disableSideloadFlags` | Rejects `--plugin-dir`, `--plugin-url`, `--agents` and `--mcp-config` at startup — the flags that would otherwise load agents and MCP servers the policy never approved. |

Two more worth knowing: `allowManagedMcpServersOnly`, and `strictPluginOnlyCustomization`, which
blocks skills, agents, hooks and MCP servers from user and project sources — `true` locks all
four, an array names which.

### The tension you have to resolve deliberately

**`allowManagedHooksOnly: true` stops this repo's committed guards from running.** The guards
live in `.claude/settings.json`, which is a project source, and that is exactly what the lock
excludes. The same applies to `strictPluginOnlyCustomization`, which would stop the committed
skills in `.github/skills/` from loading at all.

So the enterprise control that makes a guard trustworthy is the same control that switches off a
guard a team committed to their own repository. That is not a bug to work around — it is the
policy working. Resolve it on purpose, one of three ways:

1. **Promote the guards.** Deploy the guard scripts to a system path and reference them from
   managed settings, as the example does. The policy owns them; teams cannot vary them.
2. **Leave the locks off for hooks.** Keep `allowManagedPermissionRulesOnly` and
   `disableSideloadFlags`, skip `allowManagedHooksOnly`. Project guards keep working, and a team
   can still disable its own — which is acceptable when the guard is advice rather than policy.
3. **Both, at different tiers.** Managed hooks for what must never vary (credentials, deploy
   authorization); project guards for what a team should own (its own test discipline).

Picking without noticing the interaction is how a fleet ends up with guards nobody realises are
inert. This section exists so the choice is visible.

### Verify, do not assume

A managed settings file that is misplaced, misnamed, or malformed fails in a direction worth
knowing: for most keys, an invalid managed value is treated as its **most restrictive**
setting rather than ignored — `allowManagedHooksOnly` is treated as `true` until fixed. So a
typo tends to lock things down rather than open them up, which is the right default and also
means a broken policy can look like a broken installation. Confirm enforcement on a real machine
after deploying.

## Filled in for a stack: `python/` and `typescript/`

One directory per ecosystem. Each is the same set of shapes as this folder, filled in with a
real toolchain.

**Neither is canonical.** They are two fills of one shape, and having two is the only way to
show which parts of the shape actually port.

| | Python | TypeScript / JS |
|---|---|---|
| Context file | `python/AGENTS.md` | `typescript/AGENTS.md` |
| Architecture contract | `python/importlinter.example.ini` | `typescript/dependency-cruiser.config.cjs` |
| Lint / type / complexity | `python/pyproject.toml` | `typescript/tsconfig.gates.json` |
| Hooks | `python/pre-commit-config.yaml` | `typescript/pre-commit-config.yaml` |

`tooling/tools/check_commands_sync.py` checks each directory on its own terms: the tools named in that
ecosystem's `AGENTS.md` Commands must be the tools its `pre-commit-config.yaml` enforces.
Comparing them *across* ecosystems would be meaningless, so it does not.

### Read the two side by side

That is what these are for. Three things become obvious that no amount of prose establishes:

**The structure is identical.** Both hook configs have the same six tier-1 hooks in the same
order, the same `stages`, the same `pass_filenames` choices, and the same two language-agnostic
repos at the bottom. Both context files have the same sections. That similarity is the portable
part, and it is the whole argument for this folder existing.

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

### Adding an ecosystem

A directory with an `AGENTS.md` and a `pre-commit-config.yaml`. `check_commands_sync.py` picks
it up automatically, and skips any directory missing either file — so a partial addition fails
nothing while you work on it.

Then add a column to
[`gates-by-stack.md`](../../.github/skills/gates-draft/references/gates-by-stack.md) — but only
for tools you have actually run. **A reference file that names the wrong tool is worse than a
missing row**, because someone will trust it.

### You should not be writing these by hand

`.github/skills/stack-profile` detects what a repository is; `.github/skills/gates-draft`
writes the stack-specific parts. These directories are what its output should look like once a
human has pruned it.

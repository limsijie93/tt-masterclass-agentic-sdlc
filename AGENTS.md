# AGENTS.md · owned by @limsijie93 · changes go through a PR

Companion repo for the lecture **Agentic SDLC: Specs → Quality → Review**.

## Commands

Run these before showing me any code. Fix what they report, then tell me what you changed and
what you could not fix.

```
pre-commit run --all-files
python3 scripts/lint_skills.py --check-agents
./scripts/sync-skills.sh --check
semgrep test .semgrep/
python3 tools/check_commands_sync.py
pytest -q
python3 tools/mutate.py --since origin/main
```

`make tier1` runs all of them. `AGENTS.md` is the source of truth for what they are; the
Makefile is a shortcut.

## Architecture

This repo ships a **deliberately minimal application**, plus the material that teaches
against it. `myapp/` is not a product: it exists to fail in five specific ways (see
`docs/demos.md`) and has no auth, no migrations and no deployment. Five kinds of thing live
here:

- `myapp/` — the application. Layered `api -> service -> repo`, with `tasks` outside that
  order. The layering is enforced by `.importlinter`, not by this document.
- `.github/skills/` — the canonical skill files. Real files, and the only copies you edit.
  Each declares its capabilities twice: prose in `## Inputs required`, which is the contract,
  and `allowed-tools` in the frontmatter, which is one host's fill. They must agree;
  `lint_skills.py` check 11 fails the build if they do not.
  `build-slice` is the implementation step; it writes `specs/<T>.drift.md`, which
  `code-review` reads. It is the only skill granted a shell. It cannot be evaluated by
  `evals/` beyond its stop conditions, because the eval invocation allowlists no shell —
  `evals/README.md` says why.
- `.claude/`, `.cursor/`, `.agents/` — symlinks into `.github/skills/`. Never edit through them.
- `templates/` — copy-me shapes. **Stack-neutral: nothing here names a language.**
- `examples/` — one directory per ecosystem, each a fill of those shapes for a fictional
  service. `python/` and `typescript/`.
- `example/PROJ-142/` — a worked ticket, start to finish. Fixtures, not code.
- `labs/` — self-guided keyboard time. Several fixtures there are **deliberately wrong** and
  must stay wrong; `labs/AGENTS.md` names them. `tools/lab.py` marks them, and a lab is an
  eval case with a human in place of `$EVAL_ENGINE_CMD`.

## Conventions

- Markdown, one sentence per line where a line is likely to be quoted or diffed.
- Paths in artifacts are repo-relative. Never absolute, never `~`.
- Skill bodies name no vendor or host — no `Claude`, `Cursor`, `Copilot`, `VS Code`. Say the
  capability instead ("search the repository read-only").

## Gotchas

- **"Guard" and "hook" are different things here, deliberately.** A *hook* is a `pre-commit`
  hook, at commit time. A *guard* is `tools/guard_*.py`, at write time, wired through
  `.claude/settings.json`. Keeping the words apart matters because
  `tools/check_commands_sync.py` parses what it calls the hook config, and a second meaning
  makes half a dozen sentences in this repo ambiguous.

- **The lecture slides quote several files here verbatim.** `examples/python/AGENTS.md` and
  `examples/python/importlinter.example.ini` are typeset onto slides 19 and 22 character for
  character. Changing their wording breaks the deck, so a wording change needs the slide
  updated in the same PR. Check with the deck owner before rewording either.
  (Their *paths* are safe to change — those cards are tabbed with the filename you rename
  TO, not with a path in this repo.)
- The `templates/` and `examples/` files are deliberately **not** dotfiles. Two files named
  `.pre-commit-config.yaml` in one checkout confuses both `pre-commit` and the reader.
- One semgrep rule cannot cover Python and TypeScript when its patterns use
  language-specific syntax. Declaring both languages silently breaks negations — see
  `.semgrep/README.md`. One rule per language, sharing an id stem.
- **`myapp` is a real package now, and that changed which files may be dotfiles.** The root
  `.importlinter` is live and enforced. `templates/` and `examples/` still must NOT be given
  root-level dotfile names — they are stack-neutral shapes and fills, and two files named
  `.pre-commit-config.yaml` in one checkout confuses both `pre-commit` and the reader.

- **A `layers` contract does not forbid skipping a layer.** It forbids lower importing higher,
  which means `myapp.api -> myapp.repo` passes it. The rule that actually blocks the shortcut
  is the `forbidden` contract in `.importlinter`, and it needs
  `allow_indirect_imports = true` or it fires on the legitimate `api -> service -> repo` path.
  Both facts were established by running the tool, not by reading the docs.

## Do not touch

- `examples/python/AGENTS.md` and `examples/python/importlinter.example.ini` wording — see
  Gotchas. The deck quotes both verbatim.
- **Any test, in order to make an implementation pass.** If a test is wrong, say so and stop.
  A suite edited into greenness is worse than no suite. This is no longer only prose:
  `tools/guard_test_edits.py` checks it at write time and at commit time.

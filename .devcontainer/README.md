# .devcontainer/

One reason: **setup is what kills a self-guided lab.** Not the content, not the time — the
half hour between cloning and the first command working, which happens before anyone has seen
anything worth staying for.

`make setup` is the same thing without a container and works fine on a machine that already
has Python 3.12. This exists for the machine that does not, and for Windows, where the
alternative is explaining that `tooling/scripts/sync-skills.sh` needs symlink support and Developer
Mode, or `--copy`.

## What it gives you

Python 3.12, the pinned tier-1 toolchain from `requirements-dev.txt` — ruff, mypy, semgrep,
import-linter, pytest, pre-commit — the hooks installed, and `.venv/bin` on `PATH` so
`lint-imports` and `pytest` are there when a lab calls them.

Labs 01 to 03 need nothing else. Labs 04 and 05 need an assistant and, depending on your
setup, an API key; neither is baked in here, because a container that ships credentials is a
container nobody should run.

## Open it

**GitHub Codespaces** — *Code → Codespaces → Create codespace*. Nothing to install.

**Locally** — Docker plus the Dev Containers extension, then *Reopen in Container*.

Then:

```
./lab
```

## Two honest limits

The image is pinned to a **major** version (`1-3.12-bookworm`) rather than a digest, so it
moves. That is the usual trade: a digest is reproducible and goes stale silently, a tag drifts
and stays patched. The versions that actually decide whether tier 1 passes are pinned exactly,
in `requirements-dev.txt`, against the same revs `.pre-commit-config.yaml` uses.

And this file has not been run on Windows or in Codespaces by anyone here. It is assembled
from the documented behaviour of the base image, which is the same standard
`course/templates/managed-settings.example.json` is held to and is worth saying out loud rather than
discovering. If it fails for you, that is a bug and a one-line fix; say so.

# tooling/

> **Existing assets, not course material.** Everything here already existed to run the
> masterclass. You use it through commands in [`../course/`](../course/), such as `./lab start 01`;
> you don't edit it for a lab.

| Folder | What it is |
|---|---|
| [`myapp/`](myapp/) | The practice application the labs and demos break on purpose: one SQLite table, a decoy, and three layers (`api → service → repo`). The worked tickets cite its line numbers, so an edit here moves a citation. Imported as `myapp`, with `tooling/` on the path |
| [`tools/`](tools/) | The lab runner (`lab.py`, which `./lab` calls), the edit guards, the eval harness, and the checks `make tier1` runs |
| [`scripts/`](scripts/) | Skill tooling: `sync-skills.sh` links the skills into each assistant, `lint_skills.py` checks them, `package_skills.py` zips them for Claude Desktop |
| [`tests/`](tests/) | The repository's own test suite. It keeps the tickets, labs and docs consistent with each other and with `myapp/` |
| [`evals/`](evals/) | Test cases for the skills themselves: do they still do what they say? |

Run everything with `make tier1` from the repository root.

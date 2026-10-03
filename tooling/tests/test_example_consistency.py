"""Hold each worked example to one set of facts.

The lecture shows these artifacts one after another, on slides, to senior engineers. A row
count that differs between the spec and the review, or an acceptance criterion reworded
between the spec and the pull request body, is the kind of thing this audience notices and
that costs more credibility than it saves effort.

TWO CHAINS NOW. PROJ-142 is the ticket the lecture runs on; PROJ-207 is the second one, which
exists to show the same mechanisms reaching a different outcome. Every invariant below applies
to both, which is the point of parametrising rather than copying: a rule that holds for one
example and not the other is a rule about that example, not about the pipeline.

This is a test over ARTIFACTS, not over application code, so it does not need a sample app to
exist. It is also the check that stops a mismatch reaching a slide.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from conftest import instructor_only

EXAMPLES = Path(__file__).resolve().parents[2] / "course" / "tickets"


@dataclass(frozen=True)
class Chain:
    """One worked ticket's canon. The README in each directory is the human-readable copy."""

    ticket: str
    ac1: str
    ac2: str
    hazard: str
    commits: tuple[str, ...]
    spec_pr: str
    impl_pr: str
    files: tuple[str, ...]
    rule: str
    #: Ticket NUMBERS this chain's harvest may cite as an earlier sighting.
    priors: frozenset[str] = field(default_factory=frozenset)
    #: Files allowed to name a prior ticket. The harvest always may — counting a second
    #: sighting requires naming the first. A README may, because it is the map and points at
    #: the other chain. Anywhere else, a foreign ticket id is drift rather than citation.
    may_cite: frozenset[str] = field(default_factory=lambda: frozenset({"10-harvest.md"}))

    @property
    def directory(self) -> Path:
        return EXAMPLES / self.ticket

    def read(self, name: str) -> str:
        return (self.directory / name).read_text(encoding="utf-8")

    @property
    def number(self) -> str:
        return self.ticket.split("-")[1]


COMMON = (
    "README.md",
    "AGENTS.md",
    "01-ticket.md",
    "02-interrogation.md",
    "03-answers.md",
    "04-touchpoints.md",
    "05-spec.md",
    "06-git-log.txt",
    "07-pr-body.md",
    "08-review.md",
    "09-tests-that-lie.md",
    "10-harvest.md",
)

CHAINS = (
    Chain(
        ticket="PROJ-142",
        ac1="CSV completes under 30s at 1M rows",
        ac2="Returns 202 + job id when async",
        hazard="tooling/myapp/service/reports/legacy.py:210",
        commits=("f01a22", "3e7d55", "8c1b09", "a4f2e1"),
        spec_pr="#318",
        impl_pr="#319",
        # 00-agents-draft.md is this chain only: the context-file draft is a repository-level
        # artifact shown once in chapter 2.1, not a per-ticket one.
        files=COMMON[:2] + ("00-agents-draft.md",) + COMMON[2:],
        rule=".semgrep/unbounded-export-query.yml",
        priors=frozenset({"098"}),
    ),
    Chain(
        ticket="PROJ-207",
        ac1="Entitlement change visible within 60s",
        ac2="Returns 403 + upgrade_url when not entitled",
        hazard="tooling/myapp/service/billing/upgrade.py:44",
        commits=("c03b6a", "5d2f18", "91ca80", "b7e4d2"),
        spec_pr="#341",
        impl_pr="#342",
        files=COMMON,
        rule=".semgrep/fail-open-entitlement.yml",
        priors=frozenset({"142"}),
        may_cite=frozenset({"10-harvest.md", "README.md"}),
    ),
)


def test_every_file_in_the_chain_exists() -> None:
    for chain in CHAINS:
        missing = [n for n in chain.files if not (chain.directory / n).is_file()]
        assert not missing, f"{chain.ticket} is missing chain files: {missing}"


def test_no_stray_files_in_the_chain() -> None:
    for chain in CHAINS:
        on_disk = {p.name for p in chain.directory.iterdir() if p.is_file()}
        unexpected = on_disk - set(chain.files)
        assert not unexpected, f"{chain.ticket}: unexpected {unexpected}"


def test_acceptance_criteria_are_byte_identical_across_artifacts() -> None:
    """A reworded criterion makes the reviewer's comparison manual instead of automatic."""
    for chain in CHAINS:
        for name in ("05-spec.md", "07-pr-body.md"):
            body = chain.read(name)
            assert chain.ac1 in body, f"{chain.ticket}/{name} does not carry AC1 verbatim"
            assert chain.ac2 in body, f"{chain.ticket}/{name} does not carry AC2 verbatim"


def test_the_review_references_a_criterion_by_number_not_by_rewording() -> None:
    for chain in CHAINS:
        review = chain.read("08-review.md").lower()
        assert "acceptance criterion 1" in review, chain.ticket
        assert "acceptance criterion 2" in review, chain.ticket


def test_the_hazard_path_is_identical_everywhere_it_appears() -> None:
    """The (!) file is the through-line of each example. One spelling only."""
    for chain in CHAINS:
        for name in ("04-touchpoints.md", "05-spec.md", "07-pr-body.md", "08-review.md"):
            assert chain.hazard in chain.read(name), f"{chain.ticket}/{name} lacks the hazard path"


def test_the_hazard_is_marked_out_of_scope_in_the_spec() -> None:
    for chain in CHAINS:
        spec = chain.read("05-spec.md")
        out_of_scope = spec.split("## Out of scope", 1)[1].split("\n## ", 1)[0]
        leaf = chain.hazard.rsplit("/", 1)[1].split(":")[0]
        assert leaf in out_of_scope, f"{chain.ticket}: {leaf} not named out of scope"


def test_commit_shas_match_between_the_log_and_nothing_else_contradicts_them() -> None:
    for chain in CHAINS:
        log = chain.read("06-git-log.txt")
        for sha in chain.commits:
            assert sha in log, f"{chain.ticket}: {sha} missing from the git log fixture"


def test_the_log_declares_four_changed_files() -> None:
    for chain in CHAINS:
        assert "4 files changed" in chain.read("06-git-log.txt"), chain.ticket


def test_the_hazard_is_not_among_the_changed_files() -> None:
    """The arithmetic IS the punchline: the hazard file is not in the four."""
    for chain in CHAINS:
        log = chain.read("06-git-log.txt")
        changed = log.split("THE FOUR FILES", 1)[1].split("Compare that", 1)[0]
        leaf = chain.hazard.rsplit("/", 1)[1].split(":")[0]
        assert leaf not in changed, f"{chain.ticket}: {leaf} is among the changed files"


def test_pr_numbers_are_consistent() -> None:
    for chain in CHAINS:
        assert chain.spec_pr in chain.read("05-spec.md"), chain.ticket
        assert chain.impl_pr in chain.read("07-pr-body.md"), chain.ticket
        assert chain.impl_pr in chain.read("08-review.md"), chain.ticket


def test_the_review_has_exactly_three_findings() -> None:
    for chain in CHAINS:
        headings = re.findall(r"^### (\d) · ", chain.read("08-review.md"), flags=re.M)
        assert headings == ["1", "2", "3"], f"{chain.ticket}: got {headings}"


def test_exactly_one_finding_is_marked_blocking() -> None:
    """The contract is 0-3 findings and AT MOST one blocking. Never manufacture one."""
    for chain in CHAINS:
        headings = re.findall(r"^### \d · (.*)$", chain.read("08-review.md"), flags=re.M)
        blocking = [h for h in headings if h.startswith("blocking:")]
        assert len(blocking) == 1, f"{chain.ticket}: got {blocking}"


def test_the_review_carries_the_advisory_footer_verbatim() -> None:
    for chain in CHAINS:
        review = chain.read("08-review.md")
        assert "Advisory — not a merge gate." in review, chain.ticket
        assert "A human decides." in review, chain.ticket


@instructor_only
def test_the_planted_answer_is_hidden_behind_a_details_block() -> None:
    """It must not be visible on a slide, or the poll is spoiled."""
    for chain in CHAINS:
        readme = chain.read("README.md")
        assert "<details>" in readme, chain.ticket
        assert "Finding 3" in readme.split("<details>", 1)[1], chain.ticket


def test_the_interrogation_caps_at_five_questions() -> None:
    for chain in CHAINS:
        block = chain.read("02-interrogation.md").split("```", 1)[1].split("```", 1)[0]
        numbered = re.findall(r"^(\d)  ", block, flags=re.M)
        assert numbered == ["1", "2", "3", "4", "5"], f"{chain.ticket}: got {numbered}"


def test_every_interrogation_question_has_both_fields() -> None:
    for chain in CHAINS:
        block = chain.read("02-interrogation.md").split("```", 1)[1].split("```", 1)[0]
        assert block.count("blocks   ") == 5, chain.ticket
        assert block.count("assumes  ") == 5, chain.ticket


def test_the_interrogation_stops() -> None:
    for chain in CHAINS:
        block = chain.read("02-interrogation.md")
        assert "[ stopped - waiting for a human ]" in block, chain.ticket


def test_every_answer_is_filled_in_the_answers_file() -> None:
    for chain in CHAINS:
        block = chain.read("03-answers.md").split("```", 1)[1].split("```", 1)[0]
        assert block.count("answer:") == 5, chain.ticket
        # An `answer:` with nothing after it on the line would stop spec-draft.
        assert not re.search(r"answer:\s*$", block, flags=re.M), chain.ticket


# The harvest step cites PRIOR tickets on purpose: every one of its rules is about
# repetition, so a proposal has to name the earlier sighting it is counting. Those are the
# only foreign ticket ids allowed in a chain, and they are listed per chain rather than
# pattern-matched so a typo in a chain's own id still fails.


def test_the_ticket_id_is_used_consistently() -> None:
    for chain in CHAINS:
        for name in chain.files:
            for found in re.findall(r"PROJ[-_ ]?(\d+)", chain.read(name)):
                if name in chain.may_cite and found in chain.priors:
                    continue
                assert (
                    found == chain.number
                ), f"{chain.ticket}/{name} references PROJ-{found}, not {chain.ticket}"


def test_only_the_declared_files_may_cite_a_prior_ticket() -> None:
    """A stray ticket id anywhere else in a chain is drift, not a citation."""
    for chain in CHAINS:
        for name in chain.files:
            if name in chain.may_cite:
                continue
            strays = set(re.findall(r"PROJ[-_ ]?(\d+)", chain.read(name))) - {chain.number}
            assert not strays, f"{chain.ticket}/{name} cites {strays}"


def test_fixtures_with_deliberate_errors_are_protected_by_the_nested_context_file() -> None:
    """Without this, the first agent pointed at the repo 'fixes' the planted finding."""
    for chain in CHAINS:
        agents = chain.read("AGENTS.md")
        assert "08-review.md" in agents, chain.ticket
        assert "09-tests-that-lie.md" in agents, chain.ticket


# --- The stack examples ------------------------------------------------------------------
#
# course/tickets/PROJ-142/ is one ticket through the pipeline. course/templates/ has one folder per
# ecosystem. Different things, confusingly adjacent names, so the assertions live together
# to make the distinction hard to miss.

ECOSYSTEMS = ("python", "typescript")
STACK_EXAMPLES = Path(__file__).resolve().parents[2] / "course" / "templates"


def test_every_ecosystem_has_the_pair_the_checker_needs() -> None:
    for name in ECOSYSTEMS:
        directory = STACK_EXAMPLES / name
        assert (directory / "AGENTS.md").is_file(), f"{name} has no AGENTS.md"
        assert (directory / "pre-commit-config.yaml").is_file(), f"{name} has no hook config"


def test_templates_name_no_language() -> None:
    """course/templates/ is the stack-neutral shape. A tool name in it defeats the point."""
    leaked = []
    for path in (Path(__file__).resolve().parents[2] / "course" / "templates").glob("*"):
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8").lower()
        for tool in ("ruff", "mypy", "pytest", "lint-imports", "eslint", "vitest"):
            # course/templates/README.md may name tools when explaining the ratchet; the configs
            # and the AGENTS.md skeleton may not.
            if tool in body and path.name != "README.md":
                leaked.append(f"{path.name}: {tool}")
    assert not leaked, f"stack-neutral templates name a toolchain: {leaked}"


def test_both_ecosystems_share_the_same_hook_structure() -> None:
    """The similarity between the two fills IS the portable part. Assert it."""
    import re as _re

    counts = {}
    for name in ECOSYSTEMS:
        body = (STACK_EXAMPLES / name / "pre-commit-config.yaml").read_text(encoding="utf-8")
        live = "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))
        counts[name] = len(_re.findall(r"^\s*-\s*id:", live, flags=_re.M))
    assert len(set(counts.values())) == 1, f"hook counts diverged: {counts}"


def test_the_semgrep_rules_are_split_per_language() -> None:
    """One rule declaring both languages breaks the negation — see .semgrep/README.md."""
    root = Path(__file__).resolve().parents[2] / ".semgrep"
    py_rule = (root / "unbounded-export-query.yml").read_text(encoding="utf-8")
    ts_rule = (root / "ts" / "unbounded-export-query.yml").read_text(encoding="utf-8")
    assert "languages: [python]" in py_rule
    assert "typescript" not in py_rule.split("metadata:")[0]
    assert "languages: [typescript, javascript]" in ts_rule


# --- the loop closes --------------------------------------------------------------------


def test_the_harvest_artifact_reads_the_review() -> None:
    """Before this file existed, reviews/<T>.review.md was consumed by nothing and the
    pipeline ended at 'merged'. The whole point of the harvest step is that it does not."""
    for chain in CHAINS:
        harvest = chain.read("10-harvest.md")
        assert "finding 1" in harvest, chain.ticket
        assert f"harvest/{chain.ticket}.md" in harvest, chain.ticket


def test_the_harvest_proposes_but_does_not_commit() -> None:
    for chain in CHAINS:
        harvest = chain.read("10-harvest.md")
        assert "[ stopped - a human commits these ]" in harvest, chain.ticket
        assert "does not commit anything" in harvest, chain.ticket


def test_most_observations_are_logged_rather_than_proposed() -> None:
    """The restraint IS the mechanism: every harvest rule is about repetition, so a first
    sighting is logged and not proposed. A harvest that proposes everything is how a context
    file reaches 400 lines and stops being read."""
    for chain in CHAINS:
        harvest = chain.read("10-harvest.md")
        assert "Logged, not proposed" in harvest, chain.ticket
        assert harvest.count("first sighting") >= 2, chain.ticket


def test_the_one_proposal_routes_to_a_machine_check_not_to_prose() -> None:
    """Prefer the cheapest destination that can hold it: a rule in prose is a suggestion."""
    for chain in CHAINS:
        harvest = chain.read("10-harvest.md")
        proposals = harvest.split("## Proposals", 1)[1].split("## Logged", 1)[0]
        assert ".semgrep/" in proposals, chain.ticket
        assert "AGENTS.md" not in proposals, chain.ticket


def test_the_shipped_rule_carries_the_provenance_the_harvest_recorded() -> None:
    """The semgrep rule says where it came from; the harvest artifact is that decision."""
    for chain in CHAINS:
        rule = (REPO / chain.rule).read_text(encoding="utf-8")
        assert f"{chain.ticket} review, finding 1" in rule, chain.ticket


# --- The citations resolve --------------------------------------------------------------------
#
# Everything above checks the artifacts against EACH OTHER. These check them against the
# application, which only became possible when tooling/myapp/ started existing. Before that, every
# `path:line` in the worked example was a shared fiction that agreed with itself.
#
# This is the difference between consistent and correct, and it is the reason the citations are
# worth trusting on a slide: a reader who opens tooling/myapp/service/exports/service.py at line 88
# finds the query builder, because a test fails if they would not.

REPO = Path(__file__).resolve().parents[2]

#: Every `path:line` an artifact points a reader at, and the token that must be on that line.
CITED_LINES = {
    "tooling/myapp/api/exports/views.py:41": "def export_report(",
    "tooling/myapp/service/exports/service.py:88": "def build_export_query(",
    "tooling/myapp/service/reports/legacy.py:210": "build_export_query(",
    "tooling/myapp/tasks/queue.py:12": "def run_export_job(",
    "tooling/tests/test_exports.py:41": "def test_csv_export_completes",
    "tooling/tests/test_exports.py:88": "def test_oversized_export_returns_202",
    # PROJ-207. The entitlement chain cites seven lines; all seven are pinned here for the
    # same reason the export chain's are — a citation nothing checks is a slide that goes
    # wrong six weeks later, quietly, while every artifact still agrees with every other.
    "tooling/myapp/api/entitlements/views.py:37": "def feature_view(",
    "tooling/myapp/service/entitlements/service.py:70": "def resolve_entitlements(",
    "tooling/myapp/service/entitlements/service.py:89": "def has_feature(",
    "tooling/myapp/repo/entitlements/queries.py:43": "def fetch_entitlements(",
    "tooling/myapp/service/billing/upgrade.py:44": "has_feature(",
    "tooling/tests/test_entitlements.py:48": "def test_an_entitlement_change_is_visible",
    "tooling/tests/test_entitlements.py:72": "def test_an_unentitled_account_gets_403",
}

CITATION = re.compile(r"tooling/(?:myapp|tests)/[A-Za-z0-9_/]+\.py:\d+")


def _line_at(citation: str) -> str:
    path, _, lineno = citation.rpartition(":")
    body = (REPO / path).read_text(encoding="utf-8").splitlines()
    index = int(lineno) - 1
    assert 0 <= index < len(body), f"{path} has {len(body)} lines; {citation} is out of range"
    return body[index]


def test_every_cited_line_holds_what_the_artifacts_say_it_holds() -> None:
    wrong = [
        f"{citation} -> {_line_at(citation)!r} (expected to contain {token!r})"
        for citation, token in CITED_LINES.items()
        if token not in _line_at(citation)
    ]
    assert not wrong, "citations point at the wrong line: " + "; ".join(wrong)


def test_no_artifact_cites_a_line_this_test_does_not_know_about() -> None:
    """A new citation must be added to CITED_LINES, or it is unverified.

    Without this the map silently falls behind: someone cites service.py:120 in an artifact,
    nothing checks it, and the slide is wrong six weeks later. The failure message tells you
    exactly which line to pin.
    """
    found: set[str] = set()
    for chain in CHAINS:
        for name in chain.files:
            found.update(CITATION.findall(chain.read(name)))
    unknown = sorted(found - set(CITED_LINES))
    assert not unknown, f"cited but unverified — add to CITED_LINES: {unknown}"


def test_each_hazard_line_really_is_a_second_caller_of_its_shared_helper() -> None:
    """The whole spine depends on this and nothing else asserted it.

    `legacy.py:210` is the `(!)` grounding found, the reason a clean diff still broke
    something, and finding 1 of the review. If that line ever stops calling the shared
    builder, four artifacts and three slides become fiction — quietly, because they would all
    still agree with each other.
    """
    assert "build_export_query(" in _line_at("tooling/myapp/service/reports/legacy.py:210")
    assert "chunk_size=" in _line_at("tooling/myapp/service/reports/legacy.py:210"), (
        "the follow-up landed: this caller must pass chunk_size explicitly, "
        "or .semgrep/unbounded-export-query.yml should be failing the build"
    )

    # PROJ-207's hazard. Same structural role, and the assertion is the inverse of the one
    # above in a way worth noticing: here the second caller passes the argument EXPLICITLY
    # and passes the unsafe value on purpose, because an upgrade page should be optimistic.
    # If this line ever stops saying default=True, the spec's out-of-scope section, answer 4
    # and the whole argument for why the shared default could not be flipped become fiction.
    assert "has_feature(" in _line_at("tooling/myapp/service/billing/upgrade.py:44")
    assert "default=True" in _line_at("tooling/myapp/service/billing/upgrade.py:44"), (
        "the second caller must keep its explicit optimistic default, "
        "or course/tickets/PROJ-207/03-answers.md answer 4 no longer describes this code"
    )

<!-- Copy to docs/agentic-governance.md in your own repo, or wherever your platform notes live.

     STACK-NEUTRAL, and that costs something here. Every other template in this directory
     describes a shape whose content varies; this one describes a shape whose content is a
     PURCHASING DECISION. So the vendor rows are placeholders and the thresholds are blank,
     because a default budget is worse than no budget: somebody adopts it, nobody owns it,
     and the first invoice is the conversation.

     Fill it in with a named owner per row, or delete the row. A governance document with an
     unowned row is the thing it is supposed to prevent. -->

# Agentic governance — <TEAM>

Owner: `<@handle>` · Reviewed: `<YYYY-MM-DD>` · Next review: `<YYYY-MM-DD>`

The question this answers is not "are we using AI responsibly". It is **"what would tell us if
we were not, and who would see it?"** Three instruments, in the order they pay off.

## 1 · Visibility — before any limit

You cannot set a budget for a spend you have not measured, and a limit set on a guess gets
raised the first time it bites, which teaches everyone that limits are negotiable.

| What | Where it goes | Owner |
|---|---|---|
| Per-developer spend, weekly | `<dashboard>` | `<@handle>` |
| Per-repository spend, weekly | `<dashboard>` | `<@handle>` |
| Token volume by model | `<dashboard>` | `<@handle>` |
| Failed / retried runs | `<dashboard>` | `<@handle>` |

**Instrument first, for one month, before setting a single threshold.** This is the same advice
`templates/README.md` gives about turning a checker on, and it fails the same way when skipped.

If your assistants emit OpenTelemetry, a collector plus any OTLP-compatible backend is the
cheapest route — no per-tool integration, and the same pipeline your services already use. If
they do not, a proxy in front of the model API is the fallback, and it is also where limits
live below.

## 2 · Limits — one number, one owner, one alert

| Limit | Value | Enforced by | Alerts | Owner |
|---|---|---|---|---|
| Per-developer monthly ceiling | `<>` | `<proxy / vendor console>` | `<channel>` | `<@handle>` |
| Per-repository monthly ceiling | `<>` | `<>` | `<channel>` | `<@handle>` |
| Per-run ceiling | `<>` | `<>` | `<channel>` | `<@handle>` |
| Models permitted | `<>` | `<>` | — | `<@handle>` |

**A ceiling with no alert is a surprise, not a control.** Route alerts to a channel a person
reads, not to a dashboard a person visits.

**Pin the models.** Not for cost — for comparability. A metric collected across a model change
is two metrics with one name, and every trend below becomes unreadable at the point you most
want to read it.

## 3 · Adoption metrics — four, and what each one is for

Chosen so that gaming one moves another in the wrong direction. Review them together or not at
all.

| Metric | Reads | Watch for |
|---|---|---|
| **Share of merged PRs with a spec** | is the practice real, or one person's habit | Rising while review time also rises — specs written to satisfy the metric |
| **Median time in review** | the bottleneck the whole thesis is about | Falling because reviews got shallower, not because PRs got smaller |
| **Change failure rate** | whether faster is also worse | Flat while incident severity climbs — count is not weight |
| **Tier-1 catches per PR** | whether the gates are doing the work | Falling to zero: either the code improved or somebody excluded a path |

**None of these is a target.** They are read together, quarterly, by the owner named at the top.
A metric with a target attached becomes a metric people manage rather than a metric that tells
you something — and the one below is what that looks like in this specific domain.

**The one to never adopt: lines or PRs per developer.** Output rose and every downstream measure
got worse; rewarding output directly enlarges the queue that is already the constraint. A pull
request produced twice as fast that sits four times as long is a loss the person who produced it
cannot see.

## 4 · The boundary, which is not a metric

Written here because it is the row a manager is accountable for and nobody else will claim.

| Question | Answer | Owner |
|---|---|---|
| What can an agent read? | `<>` | `<@handle>` |
| What can it write, without a human in between? | `<>` | `<@handle>` |
| What can it reach on the network? | `<>` | `<@handle>` |
| Who approves a new skill, MCP server, or plugin? | `<>` | `<@handle>` |
| Where is that approval recorded? | `<>` | `<@handle>` |

An agent that reaches private data, processes untrusted content, **and** can communicate
externally is exploitable by indirect prompt injection, acting with the developer's privileges.
Any two of the three is a much smaller problem than all three. If the answers above give you all
three, that is the finding.

A skill file is a document your agent obeys, supplied by whoever wrote it. Review one the way
you review a dependency, because that is what it is.

## What this document is not

It is not a policy that changes no file. If nothing in your repository or your proxy changes as
a result of filling this in, nothing has been governed — the same rule as everywhere else here:
**anything you can only ask for, you don't have.**

# harvest ledger

Append-only. One line per observation, including the ones that were **not** proposed — those
are the point. Every rule in the harvest table is about repetition ("a mistake the agent
*repeats*", "a procedure used more than *twice*", "seen *twice*"), and a single ticket cannot
see repetition. This file is the memory that makes the second sighting countable.

It is `harvest`'s own prior output, fed back as its input. The only skill here whose input is
its own output, because learning requires memory.

Do not edit or reorder past lines. A ledger someone has tidied cannot be counted.

```
<date>      <TICKET>   <destination-or-none>   <observation>
```

---

2026-06-11  PROJ-098   none                    Page-size default of None meant "every row";
                                               reviewer caught it by hand. First sighting of a
                                               default that means "no limit".

2026-08-24  PROJ-142   .semgrep/               Chunk-size default of None meant "unbounded"; a
            unbounded-export-query.yml         shared caller inherited it. SECOND sighting of
                                               the shape logged above, which is what made it
                                               proposable — one sighting is an anecdote.
2026-08-24  PROJ-142   none                    The async job's execution branch shipped with no
                                               test. First sighting.
2026-08-24  PROJ-142   none                    A tier-2 finding reasoned about a streamed
                                               response without reading the test body. First
                                               sighting of that reviewer failure mode.

2026-09-24  PROJ-207   .semgrep/               has_feature default of True meant "grant it"; the
            fail-open-entitlement.yml          gate inherited it for one commit. SECOND sighting
                                               of "a shared helper whose most dangerous argument
                                               is optional, and whose default is the unsafe
                                               value" — first was PROJ-142's chunk_size, logged
                                               above. Different module, different argument, same
                                               shape, which is what made it proposable.
2026-09-24  PROJ-207   none                    A tier-2 review was refuted by a file the spec
                                               deliberately excluded from its context. First
                                               sighting: the reviewer read everything it was
                                               given and the answer was not in it.
2026-09-24  PROJ-207   none                    An invalidation hook shipped with no test for the
                                               empty-cache case. First sighting.

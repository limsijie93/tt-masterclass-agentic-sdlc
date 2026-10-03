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

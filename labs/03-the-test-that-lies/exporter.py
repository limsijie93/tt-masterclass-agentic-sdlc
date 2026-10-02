"""LAB 03 FIXTURE — the code under test. Do not edit it; edit your test.

One function, one documented default, and the default is the footgun the worked ticket is
about: `size=None` means "one chunk of everything", which is fine until a caller inherits it
on a table with a million rows in it.
"""

from __future__ import annotations


def chunk(rows: list[str], size: int | None = None) -> list[list[str]]:
    """Split `rows` into chunks of at most `size`.

    `size=None` means no limit: one chunk containing everything. That is the documented
    behaviour, it is what the existing callers rely on, and it is also how this function
    ends up streaming a million rows into memory.
    """
    if not rows:
        return []
    if size is None:
        return [list(rows)]
    return [rows[i : i + size] for i in range(0, len(rows), size)]

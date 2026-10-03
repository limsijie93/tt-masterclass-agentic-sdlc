"""LAB 03 FIXTURE — a test that passes and verifies nothing. Do not fix it; write a new one.

It is not a strawman. This is the most common shape of tautological test there is: the mock
is configured with the answer a few lines above the assertion that checks for it.
"""

from __future__ import annotations

from unittest.mock import Mock


def test_rows_are_chunked() -> None:
    exporter = Mock()
    exporter.chunk.return_value = [["a", "b"], ["c"]]

    result = exporter.chunk(["a", "b", "c"], size=2)

    assert result == [["a", "b"], ["c"]]
    assert len(result) == 2

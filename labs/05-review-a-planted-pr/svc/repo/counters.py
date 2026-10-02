"""A counter store. Increments are atomic; that is the only guarantee it makes."""

from __future__ import annotations

_STORE: dict[str, int] = {}


def increment(key: str) -> int:
    """Increment and return the new value. Atomic in the real store."""
    _STORE[key] = _STORE.get(key, 0) + 1
    return _STORE[key]


def reset() -> None:
    _STORE.clear()

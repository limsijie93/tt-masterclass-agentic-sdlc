"""Entitlement checks.

The middle layer, and the only one allowed to reach `myapp.repo`. `.importlinter` blocks the
view from reading the entitlements table directly.

Entitlements are read once, when an account's session starts, and held for the session.
"""

from __future__ import annotations

import sqlite3

from myapp.repo.entitlements import queries

#: account_id -> the flags read at login.
_SESSIONS: dict[int, frozenset[str]] = {}


def start_session(connection: sqlite3.Connection, account_id: int) -> frozenset[str]:
    """Read this account's flags once, at login, and keep them for the session."""
    flags = queries.fetch_entitlements(connection, account_id)
    _SESSIONS[account_id] = flags
    return flags


def end_session(account_id: int) -> None:
    """Log out: forget the flags read at login."""
    _SESSIONS.pop(account_id, None)


def has_feature(
    connection: sqlite3.Connection,
    account_id: int,
    flag: str,
    default: bool = True,
) -> bool:
    """Whether this account may use this flag.

    `default` is returned when the account has no entitlements on record.
    """
    flags = _SESSIONS.get(account_id)
    if flags is None:
        flags = start_session(connection, account_id)
    if not flags:
        return default
    return flag in flags

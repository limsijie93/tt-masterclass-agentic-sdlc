# Fixture for fail-open-entitlement. Not application code, not collected by pytest.
# Run: semgrep --test --config .semgrep/ .semgrep/


def has_feature(connection, account_id, flag, default=True):
    """Stand-in for the real helper at myapp/service/entitlements/service.py:89."""
    return default


def the_bug(connection, account):
    # ruleid: fail-open-entitlement
    return has_feature(connection, account, "advanced_export")


def the_bug_with_other_kwargs(connection, account):
    # ruleid: fail-open-entitlement
    return has_feature(connection, account, flag="sso")


def the_fix_refusing(connection, account):
    # ok: fail-open-entitlement
    return has_feature(connection, account, "advanced_export", default=False)


def the_fix_allowing(connection, account):
    # The upgrade page's case. Explicitly optimistic is fine; the rule is about saying so,
    # not about which value you pick.
    # ok: fail-open-entitlement
    return has_feature(connection, account, "advanced_export", default=True)


# --- Qualified calls. The form every real caller in myapp/ uses, and the form that made the
# --- sibling rule match nothing for weeks while its own fixture passed.


class service:  # noqa: N801 - a stand-in for the module, so the qualified form is parseable
    has_feature = staticmethod(has_feature)


def the_bug_qualified(connection, account):
    # ruleid: fail-open-entitlement
    return service.has_feature(connection, account, "advanced_export")


def the_fix_qualified(connection, account):
    # ok: fail-open-entitlement
    return service.has_feature(connection, account, "advanced_export", default=False)

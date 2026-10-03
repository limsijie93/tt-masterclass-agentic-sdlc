# Fixture for unbounded-export-query. Not application code, not collected by pytest.
# Run: semgrep --test --config .semgrep/ .semgrep/


def build_export_query(tenant, chunk_size=None):
    """Stand-in for the real builder at tooling/myapp/service/exports/service.py:88."""
    return (tenant, chunk_size)


def the_bug(tenant):
    # ruleid: unbounded-export-query
    return build_export_query(tenant)


def the_bug_with_other_kwargs(tenant, fmt):
    # ruleid: unbounded-export-query
    return build_export_query(tenant, format=fmt)


def the_fix(tenant):
    # ok: unbounded-export-query
    return build_export_query(tenant, chunk_size=5000)


def the_fix_with_other_kwargs(tenant, fmt):
    # ok: unbounded-export-query
    return build_export_query(tenant, format=fmt, chunk_size=5000)


# --- Qualified calls. The form every real caller in tooling/myapp/ uses, and the form the original
# --- pattern silently failed to match. Do not delete these.


class _ServiceModule:
    build_export_query = staticmethod(build_export_query)


service = _ServiceModule()


def the_bug_qualified(tenant):
    # ruleid: unbounded-export-query
    return service.build_export_query(tenant)


def the_fix_qualified(tenant):
    # ok: unbounded-export-query
    return service.build_export_query(tenant, chunk_size=5000)

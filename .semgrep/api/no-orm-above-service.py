# Fixture for no-orm-above-service. Not application code and not collected by pytest —
# it exists so `semgrep --test .semgrep/` can prove the rule fires where it should and
# stays quiet where it should not.
#
# This file sits under a path matching the rule's `paths.include` on purpose.

from myapp.service.exports import service


def export_rows_badly(request, session, Account):
    # ruleid: no-orm-above-service
    rows = Account.objects.filter(tenant=request.tenant)

    # ruleid: no-orm-above-service
    more = session.query(Account)

    # ruleid: no-orm-above-service
    raw = session.execute("select 1")

    return rows, more, raw


def export_rows_properly(request):
    # ok: no-orm-above-service
    return service.build_export(tenant=request.tenant, chunk_size=5000)

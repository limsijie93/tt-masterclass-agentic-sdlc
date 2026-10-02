"""A view that reaches straight into the data layer, skipping the service layer.

This is the violation the whole lab is about, and it is the one a `layers` contract does not
catch. It is also exactly what "make the export faster" produces when nobody is looking.
"""

from shop.repo.queries import rows_for_account


def handle(account_id: str) -> list[str]:
    return rows_for_account(account_id)

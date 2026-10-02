"""The service layer. This is the legitimate route to the data layer."""

from shop.repo.queries import rows_for_account


def orders_for_account(account_id: str) -> list[str]:
    return rows_for_account(account_id)

"""A view that goes through the service layer. HEALTHY. Nothing may flag this."""

from shop.service.orders import orders_for_account


def handle(account_id: str) -> list[str]:
    return orders_for_account(account_id)

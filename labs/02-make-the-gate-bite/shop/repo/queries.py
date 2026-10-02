"""The data layer. Everything above is supposed to reach it through the service layer."""


def rows_for_account(account_id: str) -> list[str]:
    return [account_id]

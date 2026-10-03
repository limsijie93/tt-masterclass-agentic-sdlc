# LAB-104 — A weakened test got through

| | |
|---|---|
| Type | Bug |
| Priority | High |
| Reporter | A teammate, in a thread, on a Friday |
| Assignee | — |

Someone replaced two assertions in a test file with `assert True` and it landed on `main`.
Nobody noticed for a day.

We have a guard for exactly this. I thought it was on? Can we make it actually work — I do not
want to find out about the next one from a customer.

<!-- Worked example. The ticket as received, copied out of the tracker and pasted into a file.
     Cited paths resolve against tooling/myapp/, which is real and deliberately minimal.
     See ./README.md for the canon and the path map. -->

# PROJ-142 — Export report times out

| | |
|---|---|
| Type | Bug |
| Priority | High |
| Reporter | Priya N. (Customer Success) |
| Assignee | — |
| Sprint | 2026-08-3 |

## Description

Customers on larger accounts are reporting that the export report times out. One of them sat on
the loading spinner for over two minutes before getting an error page. It used to be fine.

Can we make the export faster? Ideally it should just work regardless of how much data they have.

---

## What is worth noticing about this ticket

It is not a bad ticket. It is a **typical** one — written by someone describing a customer's
experience, not specifying an implementation. Everything an implementer needs is missing, and
none of it is missing through carelessness:

- Which export? The product has several.
- How much data is "larger accounts"? The fix for 50k rows and 5M rows is not the same fix.
- Is "times out" a gateway timeout, a browser timeout, or a database statement timeout?
- Is a slower-but-complete answer acceptable, or must the response stay fast?
- "It should just work regardless of how much data they have" is a wish, not a criterion. There
  is no assertion you could write for it.

Hand this to an agent as-is and it does not ask any of that. It guesses, plausibly and
confidently, and the guesses are invisible in the output — which is the whole subject of the
lecture's cold open.

The next file is what asking looks like.

<!-- LAB 05 FIXTURE. In a real repo this is specs/LAB-105.touchpoints.md, written by
     spec-interrogate before any code existed. -->

touchpoints - LAB-105

course/labs/05-review-a-planted-pr/svc/api/middleware.py:9       the request path
course/labs/05-review-a-planted-pr/svc/service/limits.py:8       per-plan limits
course/labs/05-review-a-planted-pr/svc/repo/counters.py:8        the counter store
course/labs/05-review-a-planted-pr/tests/test_limits.py:1        existing coverage

(!) course/labs/05-review-a-planted-pr/svc/api/admin.py:8
    Shares limit_for. A naive limiter would start throttling internal callers
    during an incident - out of scope, must not regress.

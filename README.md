# safeship-demo

> Test PR — verifying the SafeShip Action posts its inline comment cleanly on a freshly-opened PR.

Live demonstration of [SafeShip](https://www.safeship.dev) — a regression-prevention tool for AI agents — running against a tiny Python agent.

## What's in here

- **`demo_agent.py`** — a 3-step support-triage agent (classify intent → look up order → draft reply). The reply confirms the customer's refund using the order's actual total. The agent was once buggy: it hallucinated `$249.00` instead of using the looked-up `$24.99`. SafeShip captured that failing trace in production and generated a regression test from it.
- **`safeship.yaml`** — points the SafeShip CI runner at `demo_agent:run`.
- **`.github/workflows/safeship.yml`** — runs the SafeShip Action on every PR. The Action fetches every accepted regression test, replays this agent against each one's recorded input, and fails the PR if any test would reproduce the original failure.

## The two demo PRs

1. **PR #1 — "feature: warmer greeting"**. Adds a friendly opener to the reply. The refund amount is still drawn from `lookup_order.output.total`, so the regression test passes. ✅ The Action posts a `1 passed` comment and lets the PR merge.
2. **PR #2 — "refactor: simpler reply formatter"**. The refactor accidentally hardcodes `$249.00` — the exact failure SafeShip caught originally. The Action replays the test, the assertion `output contains input.order.total` is false, and the PR is blocked. ❌ The Action posts a `1 failed` comment with the assertion reason and a link back to the original failing run on the SafeShip dashboard.

## Try it yourself

```bash
git clone https://github.com/ego-debug/safeship-demo
cd safeship-demo
pip install "git+https://github.com/ego-debug/SafeShip.git#subdirectory=sdks/python"
export SAFESHIP_API_KEY=sk_live_...   # from /app/onboarding on safeship.dev
safeship test
```

Edit `demo_agent.py`, break the assertion, run `safeship test` again, watch it fail.

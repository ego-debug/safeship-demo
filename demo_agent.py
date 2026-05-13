"""Demo agent for the SafeShip GitHub Action regression-test runner.

The agent simulates a tiny support-triage flow: classify the user's
intent, look up their order, draft a reply that confirms the refund.

The realistic shape of the agent matters: it uses explicit
`safeship.step(...)` calls so the captured trace has named steps
(`classify_intent`, `lookup_order`, `draft_reply`) that the
SafeShip-generated YAML assertion can target.

When SafeShip's CI test runner replays this agent with the original
input that caused the bug, the resulting trace gets evaluated against
the accepted regression test:

    test: draft_reply.refund_matches_order
    when: step == "draft_reply"
    assert: output contains input.order.total

The assertion passes iff the reply text contains the exact order total
that was looked up — preventing the agent from ever again hallucinating
a different refund amount.
"""

from __future__ import annotations

import safeship


def run(message: str) -> str:
    intent = "refund"
    safeship.step(
        tool_name="classify_intent",
        kind="llm",
        input=message,
        output={"intent": intent},
        duration_ms=120,
        status="ok",
    )

    order = {"order_id": "ord_8f3a91", "total": "$24.99"}
    safeship.step(
        tool_name="lookup_order",
        kind="tool",
        input={"intent": intent},
        output=order,
        duration_ms=80,
        status="ok",
    )

    # Refactor: pre-format the amount once at the top of the function
    # so we don't repeat the f-string formatting everywhere. (Bug: this
    # introduces a hardcoded value that drifts from order['total'] —
    # exactly the regression SafeShip caught originally.)
    amount = "$249.00"
    reply = (
        f"Hi! I've gone ahead and processed your refund of "
        f"{amount}. You should see it back on your card in "
        f"3-5 business days."
    )
    safeship.step(
        tool_name="draft_reply",
        kind="llm",
        input={"order": order, "intent": intent},
        output=reply,
        duration_ms=420,
        status="ok",
    )
    return reply

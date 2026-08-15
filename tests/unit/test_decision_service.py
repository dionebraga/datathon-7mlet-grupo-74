"""Decision-service tests: guardrails, reason codes, audit logging."""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.unit


def test_decision_has_reason_codes_and_version(trained_service):
    rec = trained_service.decide(context={"age": 66, "poutcome": "success", "euribor3m": 0.8})
    assert rec.arm_id.startswith("OFF_")
    assert rec.reason_codes
    assert "MARGIN_WEIGHTED" in rec.reason_codes
    assert rec.policy_version == "v1"
    assert rec.arm_id in rec.eligible_arms


def test_default_and_loan_client_never_offered_credit(trained_service):
    rec = trained_service.decide(
        context={"age": 30, "default": "yes", "loan": "yes", "poutcome": "nonexistent"}
    )
    assert "OFF_LOAN_PREAPP" not in rec.eligible_arms
    assert "OFF_CC_CASHBACK" not in rec.eligible_arms
    assert "ELIGIBILITY_FILTERED" in rec.reason_codes


def test_decision_is_audited(trained_service, tmp_path):
    trained_service.audit_path = tmp_path / "audit.jsonl"
    rec = trained_service.decide(context={"age": 40, "poutcome": "failure"})
    lines = trained_service.audit_path.read_text(encoding="utf-8").splitlines()
    assert lines, "decision must be appended to the audit log"
    logged = json.loads(lines[-1])
    assert logged["decision_id"] == rec.decision_id
    assert logged["arm_id"] == rec.arm_id


def test_decide_requires_context_or_id(trained_service):
    with pytest.raises(ValueError):
        trained_service.decide()


def test_decision_ids_unique_across_service_instances(trained_service):
    """Two services running side by side must not mint the same decision_id.

    The API and the CLI are routinely up at the same time, and each builds its
    own DecisionService. While the id was a bare per-instance counter both
    emitted `dec_00000001`, and the audit log ended up with 230 records under
    3 distinct ids — which makes the log unauditable, the one thing it exists
    to be.
    """
    from adaptive_offers.policy.decision_service import DecisionService

    other = DecisionService(
        policy=trained_service.policy,
        metadata=trained_service.metadata,
        catalog=trained_service.catalog,
    )
    ctx = {"age": 41, "poutcome": "success"}
    ids = [s.decide(context=ctx, log=False).decision_id for s in (trained_service, other) for _ in range(3)]

    assert len(set(ids)) == len(ids), f"decision_id collision: {ids}"
    assert all(i.startswith("dec_") for i in ids)


def test_expected_reward_factors_are_recorded(trained_service):
    """`expected_p` and `margin` must be present and multiply back to the reward.

    Without them the assistant inferred a probability from the policy's raw
    ridge `estimates` — which can be negative — and reported it as P(conversão).
    """
    rec = trained_service.decide(context={"age": 66, "poutcome": "success"}, log=False)

    assert 0.0 <= rec.expected_p <= 1.0, "expected_p must be a probability"
    assert rec.margin > 0
    assert abs(rec.expected_p * rec.margin - rec.expected_reward) < 0.05

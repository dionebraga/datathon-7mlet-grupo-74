"""Doubly Robust Off-Policy Evaluation — estimator math + gate invariants."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from adaptive_offers.evaluation.ope import (
    _bootstrap_ci,
    doubly_robust,
    fit_reward_model,
    promotion_gate,
)


# --- pure helpers (fast, no bundle) ---------------------------------------- #
def test_bootstrap_ci_contains_mean_and_ordered():
    rng = np.random.default_rng(0)
    vals = rng.normal(10.0, 2.0, size=500)
    lo, hi = _bootstrap_ci(vals, n_boot=300, alpha=0.05, rng=rng)
    assert lo < hi
    assert lo <= vals.mean() <= hi


def test_bootstrap_ci_empty():
    rng = np.random.default_rng(0)
    assert _bootstrap_ci(np.array([]), rng=rng) == (0.0, 0.0)


def test_reward_model_rare_arm_falls_back_to_global_mean():
    # arm "RARE" has < min_samples rows -> no fitted weights -> global mean.
    n = 100
    ctx = np.random.default_rng(1).normal(size=(n, 3))
    ev = pd.DataFrame({
        "offer_id": ["A"] * 95 + ["RARE"] * 5,
        "reward": [100.0] * 95 + [0.0] * 5,
    })
    rm = fit_reward_model(ev, ctx, min_samples=40)
    assert "A" in rm.weights and "RARE" not in rm.weights
    assert rm.predict(ctx[0], "RARE") == pytest.approx(rm.global_mean)


def test_reward_model_predicts_signal():
    # reward = 5 * x0 ; the ridge fit for arm A should track it.
    rng = np.random.default_rng(2)
    ctx = rng.normal(size=(400, 2))
    reward = 5.0 * ctx[:, 0]
    ev = pd.DataFrame({"offer_id": ["A"] * 400, "reward": reward})
    rm = fit_reward_model(ev, ctx, ridge=0.1)
    preds = np.array([rm.predict(c, "A") for c in ctx])
    assert np.corrcoef(preds, reward)[0, 1] > 0.9


# --- estimators + gate on a small real bundle ------------------------------ #
@pytest.fixture(scope="module")
def small_bundle():
    from adaptive_offers.data.preprocessing import load_processed
    from adaptive_offers.data.synthetic import CONTEXT_FEATURES, generate

    proc = load_processed().head(2500).reset_index(drop=True)
    bundle = generate(processed=proc, seed=42)
    return proc, bundle, CONTEXT_FEATURES


def _frozen(name, proc, bundle, ctx_feats, seed=123):
    from adaptive_offers.bandits.registry import build_policy
    from adaptive_offers.simulation.environment import build_arms, run_simulation

    arms = build_arms(bundle.catalog)
    pol = build_policy(name, arms, context_dim=len(ctx_feats), seed=seed)
    run_simulation(pol, proc, bundle, horizon=2000, seed=seed)
    return pol


def test_dr_ci_contains_point_estimate(small_bundle):
    proc, bundle, cf = small_bundle
    lin = _frozen("linucb", proc, bundle, cf)
    d = doubly_robust(lin, proc, bundle, n_boot=150, seed=0)
    lo, hi = d["v_dr_ci"]
    assert lo <= hi
    assert lo <= d["v_dr"] <= hi
    assert 0.0 <= d["match_rate"] <= 1.0
    assert d["effective_sample"] > 0
    assert d["n_events"] > 0


def test_dr_reduces_variance_vs_ips(small_bundle):
    proc, bundle, cf = small_bundle
    lin = _frozen("linucb", proc, bundle, cf)
    d = doubly_robust(lin, proc, bundle, n_boot=100, seed=0)
    # DR should not have materially higher variance than IPS on this data.
    assert d["var_reduction_vs_ips"] >= -0.05


def test_promotion_gate_structure(small_bundle):
    proc, bundle, cf = small_bundle
    cand = _frozen("linucb", proc, bundle, cf)
    inc = _frozen("baseline", proc, bundle, cf)
    g = promotion_gate(cand, inc, proc, bundle, n_boot=100, seed=0)
    assert g["decision"] in {"PROMOTE", "HOLD"}
    assert isinstance(g["passed"], bool)
    # decision must be consistent with the lower-bound rule
    assert g["passed"] == (g["candidate_dr_lower"] >= g["incumbent_dr"])


def test_reward_model_shared_is_deterministic(small_bundle):
    proc, bundle, cf = small_bundle
    lin = _frozen("linucb", proc, bundle, cf)
    rm = fit_reward_model(bundle.events, bundle.contexts)
    a = doubly_robust(lin, proc, bundle, reward_model=rm, n_boot=100, seed=7)
    b = doubly_robust(lin, proc, bundle, reward_model=rm, n_boot=100, seed=7)
    assert a["v_dr"] == b["v_dr"]

"""Doubly Robust Off-Policy Evaluation (OPE) — value a *new* policy from logs.

The hardest question in a bandit system is: *is this new policy better, before we
expose real customers to it?* Off-policy evaluation answers it from data logged by
a stochastic **logging policy** (with recorded propensities), without deploying.

We build three estimators on top of the recorded propensities:

* **IPS / SNIPS** — importance-weighted reward (already unbiased, high variance).
* **Direct Method (DM)** — a fitted reward model ``Q̂(x, a)``; low variance but
  biased if the model is wrong.
* **Doubly Robust (DR)** — ``Q̂(x, π(x)) + 1{π(x)=a}/p · (r − Q̂(x, a))``. It is
  **consistent if EITHER the reward model OR the propensities are correct** (the
  "doubly robust" property) and has **lower variance than IPS**.

**Bootstrap confidence intervals** quantify uncertainty. The **promotion gate**
(:func:`promotion_gate`) only promotes a candidate when its DR **lower confidence
bound** beats the incumbent's DR point estimate — a statistically honest,
A/B-free promotion criterion (Etapa 7).

References: Dudík, Langford & Li (2011), *Doubly Robust Policy Evaluation and
Learning*; Jiang & Li (2016).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from adaptive_offers.bandits.base import Policy
from adaptive_offers.data.synthetic import SyntheticBundle, eligible_arms


# --------------------------------------------------------------------------- #
# Reward model Q̂(x, a) — per-arm ridge (the Direct Method component)
# --------------------------------------------------------------------------- #
@dataclass
class RewardModel:
    """Per-arm linear reward model with a global-mean fallback for rare arms."""

    weights: dict[str, np.ndarray]
    global_mean: float

    def predict(self, ctx: np.ndarray, arm_id: str) -> float:
        w = self.weights.get(arm_id)
        if w is None:
            return self.global_mean
        return float(np.dot(w, ctx))


def fit_reward_model(
    events: pd.DataFrame, contexts: np.ndarray, *, ridge: float = 1.0, min_samples: int = 40
) -> RewardModel:
    """Fit ``reward ~ context`` per logged arm via ridge regression (closed form).

    Uses only numpy (no hard sklearn dependency): θ_a = (XᵀX + λI)⁻¹ Xᵀr on the
    events where arm ``a`` was shown. Arms with too few samples fall back to the
    global mean reward (bias-safe; DR still corrects via the IPS term).
    """
    rewards = events["reward"].to_numpy(dtype=float)
    arms = events["offer_id"].to_numpy()
    global_mean = float(rewards.mean()) if len(rewards) else 0.0
    dim = contexts.shape[1] if contexts.size else 0
    weights: dict[str, np.ndarray] = {}
    for arm_id in np.unique(arms):
        mask = arms == arm_id
        if int(mask.sum()) < min_samples or dim == 0:
            continue
        X = contexts[mask]
        y = rewards[mask]
        A = X.T @ X + ridge * np.eye(dim)
        try:
            theta = np.linalg.solve(A, X.T @ y)
        except np.linalg.LinAlgError:
            continue
        weights[str(arm_id)] = theta
    return RewardModel(weights=weights, global_mean=global_mean)


# --------------------------------------------------------------------------- #
# Per-event contributions for IPS / DM / DR
# --------------------------------------------------------------------------- #
def _contributions(
    policy: Policy,
    processed: pd.DataFrame,
    bundle: SyntheticBundle,
    reward_model: RewardModel,
) -> dict[str, np.ndarray]:
    """Compute per-event IPS, DM and DR contribution arrays for ``policy``."""
    events = bundle.events
    catalog = bundle.catalog
    contexts = bundle.contexts
    n = len(events)
    ips = np.zeros(n)
    dm = np.zeros(n)
    dr = np.zeros(n)
    match = np.zeros(n)
    inv_p = np.zeros(n)
    for i in range(n):
        ev = events.iloc[i]
        ctx = contexts[i]
        elig = [a.offer_id for a in eligible_arms(processed.iloc[i], catalog)]
        target = policy.select(ctx, elig).arm_id
        logged = str(ev["offer_id"])
        r = float(ev["reward"])
        p = max(float(ev["propensity"]), 1e-6)
        q_target = reward_model.predict(ctx, target)
        q_logged = reward_model.predict(ctx, logged)
        m = 1.0 if target == logged else 0.0
        w = m / p
        match[i] = m
        inv_p[i] = w
        ips[i] = w * r
        dm[i] = q_target
        dr[i] = q_target + w * (r - q_logged)
    return {"ips": ips, "dm": dm, "dr": dr, "match": match, "inv_p": inv_p}


def _bootstrap_ci(
    values: np.ndarray, *, n_boot: int = 800, alpha: float = 0.05, rng: np.random.Generator
) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of ``values``."""
    n = len(values)
    if n == 0:
        return (0.0, 0.0)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = values[idx].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (float(lo), float(hi))


def doubly_robust(
    policy: Policy,
    processed: pd.DataFrame,
    bundle: SyntheticBundle,
    *,
    reward_model: RewardModel | None = None,
    n_boot: int = 800,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, Any]:
    """Off-policy value of ``policy`` via IPS, SNIPS, Direct Method and DR + CIs."""
    rm = reward_model or fit_reward_model(bundle.events, bundle.contexts)
    c = _contributions(policy, processed, bundle, rm)
    rng = np.random.default_rng(seed)
    n = len(c["ips"])
    sum_w = float(c["inv_p"].sum())
    snips = float((c["ips"]).sum() / sum_w) if sum_w > 0 else 0.0
    # Effective sample size of the importance weights (variance diagnostic).
    ess = float(sum_w ** 2 / np.square(c["inv_p"]).sum()) if sum_w > 0 else 0.0
    out = {
        "policy": policy.name,
        "n_events": n,
        "match_rate": round(float(c["match"].mean()), 4) if n else 0.0,
        "effective_sample": round(ess, 1),
        "v_ips": round(float(c["ips"].mean()), 3),
        "v_snips": round(snips, 3),
        "v_dm": round(float(c["dm"].mean()), 3),
        "v_dr": round(float(c["dr"].mean()), 3),
    }
    lo_ips, hi_ips = _bootstrap_ci(c["ips"], n_boot=n_boot, alpha=alpha, rng=rng)
    lo_dr, hi_dr = _bootstrap_ci(c["dr"], n_boot=n_boot, alpha=alpha, rng=rng)
    out["v_ips_ci"] = (round(lo_ips, 3), round(hi_ips, 3))
    out["v_dr_ci"] = (round(lo_dr, 3), round(hi_dr, 3))
    # Variance reduction of DR vs IPS (per-event), the key DR selling point.
    var_ips = float(c["ips"].var())
    var_dr = float(c["dr"].var())
    out["var_reduction_vs_ips"] = round(1 - var_dr / var_ips, 4) if var_ips > 0 else 0.0
    return out


def promotion_gate(
    candidate: Policy,
    incumbent: Policy,
    processed: pd.DataFrame,
    bundle: SyntheticBundle,
    *,
    n_boot: int = 800,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, Any]:
    """A/B-free promotion decision via DR-OPE with confidence intervals.

    Promote the candidate only if its DR **lower confidence bound** is at least
    the incumbent's DR point estimate — i.e. the candidate is *statistically not
    worse* off-policy. Shares one reward model so both are scored consistently.
    """
    rm = fit_reward_model(bundle.events, bundle.contexts)
    cand = doubly_robust(candidate, processed, bundle, reward_model=rm,
                         n_boot=n_boot, alpha=alpha, seed=seed)
    inc = doubly_robust(incumbent, processed, bundle, reward_model=rm,
                        n_boot=n_boot, alpha=alpha, seed=seed)
    cand_lb = cand["v_dr_ci"][0]
    passed = cand_lb >= inc["v_dr"]
    return {
        "candidate": candidate.name,
        "incumbent": incumbent.name,
        "candidate_dr": cand["v_dr"],
        "candidate_dr_lower": cand_lb,
        "incumbent_dr": inc["v_dr"],
        "passed": bool(passed),
        "decision": "PROMOTE" if passed else "HOLD",
        "detail": cand,
        "incumbent_detail": inc,
    }

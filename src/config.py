# src/config.py
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

STATES: List[str] = ["exploring", "evaluating", "high_intent", "idle", "churn_risk"]
EVENT_TYPES: List[str] = [
    "landing", "search", "category_view", "item_view", "wishlist", "compare",
    "add_to_cart", "remove_from_cart", "checkout_start", "purchase", "exit"
]
ARCHETYPES: List[str] = ["browser", "researcher", "decisive", "bargain_hunter"]
DEVICES: List[str] = ["mobile", "desktop", "tablet"]
REFERRERS: List[str] = ["search", "ads", "direct", "email", "social"]

PRICE_BUCKETS: List[Tuple[float, float, str]] = [
    (0, 20, "0_20"),
    (20, 50, "20_50"),
    (50, 100, "50_100"),
    (100, 200, "100_200"),
    (200, 1e9, "200_plus"),
]

@dataclass(frozen=True)
class GenConfig:
    seed: int = 7
    n_users: int = 800
    # sessions per user
    sessions_min: int = 5
    sessions_max: int = 30
    # events per session
    events_min: int = 5
    events_max: int = 60
    # noise injection
    noise_rate: float = 0.03
    # base time window (days)
    span_days: int = 30

def state_transition_matrix_v0() -> np.ndarray:
    """
    Row-stochastic matrix P(next_state | current_state).
    Order matches STATES.
    """
    idx = {s: i for i, s in enumerate(STATES)}
    P = np.zeros((len(STATES), len(STATES)), dtype=float)

    def set_row(s: str, probs: Dict[str, float]) -> None:
        r = idx[s]
        for t, p in probs.items():
            P[r, idx[t]] = p
        # normalize
        P[r] = P[r] / P[r].sum()

    set_row("exploring", {
        "exploring": 0.55,
        "evaluating": 0.28,
        "idle": 0.10,
        "churn_risk": 0.04,
        "high_intent": 0.03,
    })
    set_row("evaluating", {
        "evaluating": 0.50,
        "high_intent": 0.18,
        "exploring": 0.18,
        "idle": 0.08,
        "churn_risk": 0.06,
    })
    set_row("high_intent", {
        "high_intent": 0.55,
        "evaluating": 0.15,
        "idle": 0.10,
        "exploring": 0.08,
        "churn_risk": 0.12,
    })
    set_row("idle", {
        "idle": 0.60,
        "exploring": 0.20,
        "evaluating": 0.10,
        "churn_risk": 0.08,
        "high_intent": 0.02,
    })
    set_row("churn_risk", {
        "churn_risk": 0.62,
        "idle": 0.18,
        "exploring": 0.12,
        "evaluating": 0.06,
        "high_intent": 0.02,
    })
    return P

def archetype_weights() -> Dict[str, float]:
    # population mix
    return {"browser": 0.40, "researcher": 0.25, "decisive": 0.20, "bargain_hunter": 0.15}

def initial_state_distribution(archetype: str) -> Dict[str, float]:
    # starting state bias
    if archetype == "decisive":
        return {"exploring": 0.40, "evaluating": 0.20, "high_intent": 0.25, "idle": 0.10, "churn_risk": 0.05}
    if archetype == "researcher":
        return {"exploring": 0.35, "evaluating": 0.40, "high_intent": 0.10, "idle": 0.10, "churn_risk": 0.05}
    if archetype == "bargain_hunter":
        return {"exploring": 0.35, "evaluating": 0.30, "high_intent": 0.10, "idle": 0.10, "churn_risk": 0.15}
    # browser
    return {"exploring": 0.55, "evaluating": 0.20, "high_intent": 0.05, "idle": 0.15, "churn_risk": 0.05}

def event_emission_probs(state: str, archetype: str) -> Dict[str, float]:
    """
    P(event_type | state, archetype).
    Keep it interpretable; we'll refine later.
    """
    base = {
        "landing": 0.05, "search": 0.10, "category_view": 0.15, "item_view": 0.35,
        "wishlist": 0.05, "compare": 0.08, "add_to_cart": 0.08, "remove_from_cart": 0.03,
        "checkout_start": 0.04, "purchase": 0.02, "exit": 0.05
    }

    if state == "exploring":
        base.update({"category_view": 0.20, "item_view": 0.38, "compare": 0.05, "add_to_cart": 0.05, "purchase": 0.005, "exit": 0.06})
    elif state == "evaluating":
        base.update({"compare": 0.16, "wishlist": 0.10, "item_view": 0.32, "add_to_cart": 0.06, "purchase": 0.01, "exit": 0.05})
    elif state == "high_intent":
        base.update({"add_to_cart": 0.18, "checkout_start": 0.14, "purchase": 0.10, "compare": 0.06, "exit": 0.04, "item_view": 0.25})
    elif state == "idle":
        base.update({"exit": 0.18, "item_view": 0.28, "category_view": 0.10, "compare": 0.03, "purchase": 0.002})
    elif state == "churn_risk":
        base.update({"exit": 0.16, "remove_from_cart": 0.08, "add_to_cart": 0.10, "compare": 0.10, "purchase": 0.006})

    # archetype tweaks
    if archetype == "researcher":
        base["compare"] *= 1.4
        base["wishlist"] *= 1.2
    elif archetype == "decisive":
        base["add_to_cart"] *= 1.4
        base["checkout_start"] *= 1.2
        base["compare"] *= 0.7
    elif archetype == "bargain_hunter":
        base["search"] *= 1.5
        base["remove_from_cart"] *= 1.4
        base["purchase"] *= 0.9

    # renormalize
    s = sum(base.values())
    return {k: v / s for k, v in base.items()}

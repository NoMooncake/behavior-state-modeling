# src/generate_data.py
from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.config import (
    GenConfig, STATES, EVENT_TYPES, ARCHETYPES, DEVICES, REFERRERS, PRICE_BUCKETS,
    state_transition_matrix_v0, archetype_weights, initial_state_distribution, event_emission_probs
)

def _choice(rng: np.random.Generator, items: List[str], probs: Dict[str, float]) -> str:
    p = np.array([probs[i] for i in items], dtype=float)
    p = p / p.sum()
    return rng.choice(items, p=p).item()

def _bucket_price(price: float) -> str:
    for lo, hi, name in PRICE_BUCKETS:
        if lo <= price < hi:
            return name
    return "unknown"

def _sample_category_and_price(rng: np.random.Generator) -> Tuple[str, float]:
    categories = ["shoes", "tops", "pants", "outerwear", "bags", "beauty", "electronics", "home"]
    cat = rng.choice(categories).item()
    # simple log-normal-ish price by category
    base = {
        "beauty": (np.log(18), 0.35),
        "tops": (np.log(35), 0.45),
        "pants": (np.log(55), 0.40),
        "shoes": (np.log(75), 0.40),
        "bags": (np.log(110), 0.50),
        "outerwear": (np.log(130), 0.55),
        "home": (np.log(60), 0.55),
        "electronics": (np.log(180), 0.60),
    }
    mu, sigma = base[cat]
    price = float(np.exp(rng.normal(mu, sigma)))
    price = float(max(5.0, min(price, 800.0)))
    return cat, round(price, 2)

def _timing_params(state: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Return (dwell_mu_sigma, gap_mu_sigma) for lognormal in seconds.
    """
    # (mu, sigma) in log-space
    if state == "exploring":
        return (np.log(12), 0.55), (np.log(4), 0.65)
    if state == "evaluating":
        return (np.log(18), 0.60), (np.log(6), 0.75)
    if state == "high_intent":
        return (np.log(10), 0.50), (np.log(3), 0.55)
    if state == "idle":
        return (np.log(6), 0.60), (np.log(40), 0.90)
    # churn_risk
    return (np.log(8), 0.65), (np.log(18), 0.95)

def generate(cfg: GenConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(cfg.seed)
    P = state_transition_matrix_v0()
    state_idx = {s: i for i, s in enumerate(STATES)}

    # users
    arch_w = archetype_weights()
    archetypes = list(arch_w.keys())
    arch_probs = np.array([arch_w[a] for a in archetypes], dtype=float)
    arch_probs = arch_probs / arch_probs.sum()

    users = []
    for ui in range(cfg.n_users):
        user_id = f"u_{ui:06d}"
        archetype = rng.choice(archetypes, p=arch_probs).item()
        device = rng.choice(DEVICES, p=[0.62, 0.33, 0.05]).item()
        users.append({"user_id": user_id, "archetype": archetype, "device_default": device})
    users_df = pd.DataFrame(users)

    # time window
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=cfg.span_days)

    events_rows = []
    sessions_rows = []

    sid_counter = 0

    for u in users:
        n_sessions = int(rng.integers(cfg.sessions_min, cfg.sessions_max + 1))
        # sample session start times
        session_starts = rng.uniform(0, cfg.span_days, size=n_sessions)
        session_starts = np.sort(session_starts)

        for s_i in range(n_sessions):
            sid_counter += 1
            session_id = f"s_{cfg.seed}_{sid_counter:07d}"
            user_id = u["user_id"]
            archetype = u["archetype"]
            device = u["device_default"]

            session_start = start + timedelta(days=float(session_starts[s_i]))
            t = session_start

            init_dist = initial_state_distribution(archetype)
            state = _choice(rng, STATES, init_dist)

            referrer = rng.choice(REFERRERS, p=[0.45, 0.18, 0.20, 0.07, 0.10]).item()

            n_events = int(rng.integers(cfg.events_min, cfg.events_max + 1))
            purchased = 0

            # session-level tracking
            items_seen = set()
            cats_seen = set()
            counts = {et: 0 for et in EVENT_TYPES}
            total_dwell = 0.0
            total_gap = 0.0
            cart = set()

            last_item = None

            for e_i in range(n_events):
                # emit event
                probs = event_emission_probs(state, archetype)
                event_type = _choice(rng, EVENT_TYPES, probs)

                # simple “terminal” handling
                if purchased == 1:
                    event_type = "exit"

                # sample item/category/price
                if event_type in ("landing", "search", "category_view"):
                    category, price = _sample_category_and_price(rng)
                    item_id = f"item_{int(rng.integers(0, 12000)):06d}"
                else:
                    # bias revisits during evaluating
                    if state == "evaluating" and last_item is not None and rng.random() < 0.35:
                        item_id = last_item
                    else:
                        item_id = f"item_{int(rng.integers(0, 12000)):06d}"
                    category, price = _sample_category_and_price(rng)

                last_item = item_id

                items_seen.add(item_id)
                cats_seen.add(category)

                # timing
                (d_mu, d_sig), (g_mu, g_sig) = _timing_params(state)
                dwell = float(np.exp(rng.normal(d_mu, d_sig)))
                gap = float(np.exp(rng.normal(g_mu, g_sig))) if e_i > 0 else 0.0

                # noise injection
                is_noise = 1 if rng.random() < cfg.noise_rate else 0
                if is_noise:
                    # occasional extreme gap or weird event spikes
                    if rng.random() < 0.6:
                        gap *= float(rng.uniform(3.0, 10.0))
                    if rng.random() < 0.2:
                        event_type = rng.choice(["compare", "remove_from_cart", "exit"]).item()

                # cart logic (lightweight)
                if event_type == "add_to_cart":
                    cart.add(item_id)
                elif event_type == "remove_from_cart":
                    if cart:
                        cart.remove(rng.choice(list(cart)).item())

                if event_type == "purchase":
                    purchased = 1

                # advance time
                t = t + timedelta(seconds=gap + dwell)

                # record row
                events_rows.append({
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": t.isoformat().replace("+00:00", "Z"),
                    "event_index": e_i,
                    "event_type": event_type,
                    "item_id": item_id,
                    "category": category,
                    "price": price,
                    "price_bucket": _bucket_price(price),
                    "dwell_time_s": round(dwell, 3),
                    "gap_time_s": round(gap, 3),
                    "referrer": referrer if e_i == 0 else "",
                    "device": device,
                    "state_true": state,
                    "is_noise": is_noise,
                })

                counts[event_type] += 1
                total_dwell += dwell
                total_gap += gap

                # transition state for next event
                cur = state_idx[state]
                nxt = rng.choice(STATES, p=P[cur]).item()
                state = nxt

                # optional early stop: exit ends the session
                if event_type == "exit":
                    break

            session_end = t
            n_rows = sum(counts.values())
            conversion = 1 if counts["purchase"] > 0 else 0

            # v0 hesitation index (interpretable)
            hesitation_index = (
                0.8 * counts["compare"]
                + 0.4 * counts["wishlist"]
                + 0.6 * counts["remove_from_cart"]
                + 0.002 * total_gap
            ) / max(1, n_rows)

            # path signature (compressed)
            path = [k for k, v in counts.items() for _ in range(v)]
            # keep it short and readable
            path_signature = "->".join([p for p in path[:18]]) + ("->..." if len(path) > 18 else "")

            sessions_rows.append({
                "user_id": user_id,
                "session_id": session_id,
                "archetype": archetype,
                "session_start": session_start.isoformat().replace("+00:00", "Z"),
                "session_end": session_end.isoformat().replace("+00:00", "Z"),
                "n_events": n_rows,
                "unique_items": len(items_seen),
                "unique_categories": len(cats_seen),
                "n_item_view": counts["item_view"],
                "n_compare": counts["compare"],
                "n_add_to_cart": counts["add_to_cart"],
                "n_remove_from_cart": counts["remove_from_cart"],
                "n_checkout_start": counts["checkout_start"],
                "n_purchase": counts["purchase"],
                "conversion": conversion,
                "total_dwell_time_s": round(total_dwell, 3),
                "total_gap_time_s": round(total_gap, 3),
                "hesitation_index": round(float(hesitation_index), 5),
                "path_signature": path_signature,
            })

    events_df = pd.DataFrame(events_rows)
    sessions_df = pd.DataFrame(sessions_rows)
    meta_df = pd.DataFrame([asdict(cfg)])

    return events_df, sessions_df, meta_df

def main() -> None:
    cfg = GenConfig()
    events_df, sessions_df, meta_df = generate(cfg)

    out_dir = os.path.join("data", "sample", "v0_1")
    os.makedirs(out_dir, exist_ok=True)

    events_path = os.path.join(out_dir, "events_sample.csv")
    sessions_path = os.path.join(out_dir, "sessions_sample.csv")
    meta_path = os.path.join(out_dir, "generation_meta.csv")

    # keep sample size manageable for git
    # if you want smaller: take a slice by users
    events_df.to_csv(events_path, index=False)
    sessions_df.to_csv(sessions_path, index=False)
    meta_df.to_csv(meta_path, index=False)

    print(f"Wrote: {events_path} ({len(events_df):,} rows)")
    print(f"Wrote: {sessions_path} ({len(sessions_df):,} rows)")
    print(f"Wrote: {meta_path}")

if __name__ == "__main__":
    main()

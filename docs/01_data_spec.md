# Data Specification (v0)

This project uses a **semi-synthetic e-commerce clickstream** dataset to study:
1) **decision paths** (browse → compare → cart → purchase / exit),
2) **behavioral states** and **state transitions** (explainable, mechanism-first),
3) early signals for **drop-off / churn risk** and “**high activity but low intent**”.

The dataset is designed to be:
- reproducible (seeded generation)
- realistic enough to support EDA and inference
- controllable (we can vary transition matrices, noise, and user archetypes)
- explainable (state → behavior distribution → transitions)

---

## 1. Entities

### 1.1 User
A user has a stable **archetype** controlling tendencies such as:
- exploration depth
- comparison tendency
- purchase propensity
- patience / time gaps
- price sensitivity

### 1.2 Session
A session is a time-bounded group of events. We generate `session_id` directly, and can also re-derive sessions via an inactivity threshold as a validation step.

### 1.3 Event
Each row is one interaction event (clickstream-like).

---

## 2. Event Schema (events.csv)

| column | type | example | description |
|---|---|---:|---|
| user_id | string | u_000123 | user identifier |
| session_id | string | s_2025..._0001 | session identifier |
| timestamp | string (ISO) | 2025-12-26T10:12:33Z | event time (UTC) |
| event_index | int | 7 | position within the session |
| event_type | string | view | event category (see list below) |
| item_id | string | item_004982 | item being interacted with |
| category | string | shoes | product category |
| price | float | 79.99 | item price |
| price_bucket | string | 50_100 | bucket derived from price |
| dwell_time_s | float | 12.4 | time spent on current step/page |
| gap_time_s | float | 3.1 | time since previous event |
| referrer | string | search | entry source for first event (optional for later events) |
| device | string | mobile | device type (mobile/desktop/tablet) |
| state_true | string | evaluating | latent state used to generate this event (for evaluation) |
| is_noise | int | 0 | whether this row was injected noise/anomaly |

### 2.1 event_type vocabulary (v0)
- `landing`
- `search`
- `category_view`
- `item_view`
- `wishlist`
- `compare`
- `add_to_cart`
- `remove_from_cart`
- `checkout_start`
- `purchase`
- `exit`

---

## 3. Session Summary Schema (sessions.csv)

One row per session.

| column | description |
|---|---|
| user_id, session_id | keys |
| session_start, session_end | timestamps |
| n_events | number of events |
| unique_items, unique_categories | diversity |
| n_item_view, n_compare, n_add_to_cart, n_purchase | counts |
| conversion | 1 if purchase occurs |
| total_dwell_time_s, total_gap_time_s | timing totals |
| hesitation_index | custom metric (see below) |
| path_signature | a compressed string representation of the path |

### 3.1 hesitation_index (v0 definition)
A simple interpretable index:
- higher if many `compare` / repeated `item_view`
- higher if long gaps before cart/checkout
- higher if cart churn occurs (add/remove loops)

(Exact formula in `src/features.py`, but this is the conceptual definition.)

---

## 4. Latent Behavioral States (state_true)

We define 5 states to support explainable modeling.

1. `exploring`: broad browsing, many category/item views, low cart actions
2. `evaluating`: increased compare, revisits, moderate gaps, narrowing categories
3. `high_intent`: cart/checkout events more likely, shorter gaps to checkout
4. `idle`: sparse actions, long gaps, often exits without clear decision
5. `churn_risk`: repeated low-quality sessions, cart churn, exits, low progression

**Important:** `state_true` is used only for evaluation and controlled experiments.
A core goal is to recover meaningful states from observed behavior.

---

## 5. State → Behavior Distributions (v0 intuition)

- exploring: `category_view/item_view/search` dominate, higher diversity
- evaluating: `compare/wishlist/item_view` dominate, higher revisits
- high_intent: `add_to_cart/checkout_start/purchase` more likely, shorter time-to-action
- idle: `item_view` sparse, long `gap_time_s`, higher `exit`
- churn_risk: cart churn (`add_to_cart/remove_from_cart`), exits, shallow browsing

---

## 6. State Transition Matrix (v0 draft)

Transitions are defined at the **event level** (state may change between events).
Example intuition (not all probabilities shown here):
- exploring → evaluating is common after repeated item_view
- evaluating → high_intent occurs when cart actions begin
- any state → idle may happen due to interruptions (long gaps)
- idle → exploring can happen when user returns
- churn_risk is more likely after repeated failed sessions

The exact matrix is stored in `src/config.py` and versioned in generation notes.

---

## 7. User Archetypes (v0)

We simulate 4 archetypes to ensure meaningful variation:

- `browser`: high exploration, low conversion
- `researcher`: high evaluating/compare, moderate conversion
- `decisive`: short paths, high conversion
- `bargain_hunter`: high search, price sensitivity, cart churn possible

Archetypes influence:
- state transition biases
- event distributions within states
- timing distributions (gap/dwell)
- conversion likelihood

---

## 8. Noise / Anomalies (v0)

We inject a small proportion of noisy events:
- anomalous long gaps
- random event_type spikes (e.g., compare bursts)
- occasional missing-like behavior (optional later)

Noise is flagged by `is_noise`.

---

## 9. Known Limitations (v0)

- We do not model inventory constraints, promotions, or recommendation exposure loops yet.
- We simplify product semantics: categories and prices are sampled from distributions.
- We assume time is UTC and do not model daily seasonality in v0 (can be added later).

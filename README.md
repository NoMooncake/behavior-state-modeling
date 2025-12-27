# Decision Path Modeling in E-commerce Sessions

This project explores how user decision-making behavior in e-commerce sessions can be better understood through **decision path structure** rather than raw activity metrics.

Using a semi-synthetic clickstream dataset, we demonstrate that *how* and *when* users commit matters far more than *how much* they interact.

---

## Motivation

Traditional behavioral analytics often rely on scalar metrics such as:
- number of clicks
- session duration
- total page views

However, these metrics frequently fail to distinguish between:
- high engagement with low intent
- decisive behavior with minimal interaction

This project investigates whether **decision path structure** and **commitment semantics** provide stronger explanatory power for conversion outcomes.

---

## Dataset

We use a semi-synthetic e-commerce clickstream dataset generated to reflect realistic user behavior patterns.

- **Event-level data**: timestamped user actions (view, compare, add-to-cart, checkout, purchase, exit)
- **Session-level aggregation**: derived behavioral features and path representations
- **Path signature**: compressed representation of action sequences within a session

The dataset is fully reproducible and designed to support structural analysis of decision processes.

---

## Analytical Approach

The analysis proceeds in four stages:

1. **Baseline EDA**
   - Validate that session length and activity volume alone do not explain conversion.
2. **Decision Path Structure**
   - Abstract raw clickstreams into interpretable path patterns.
3. **Commitment Semantics**
   - Distinguish between soft commitment (add-to-cart) and hard commitment (checkout or purchase).
4. **Decision Framework Construction**
   - Combine path structure and commitment strength into a unified behavioral framework.

Throughout the analysis, emphasis is placed on interpretability and rule-based reasoning rather than black-box modeling.

---

## Key Findings

1. **Path length alone does not distinguish conversion outcomes.**  
   Converted and non-converted sessions exhibit nearly identical distributions of interaction volume.

2. **Decision path structure provides strong separation of user intent.**  
   Commitment-touch paths show an order-of-magnitude higher conversion rate than browsing-only or comparison-augmented paths.

3. **Comparison-heavy behavior is associated with decision friction.**  
   Sessions with extensive comparison actions display higher hesitation and lower conversion.

4. **Soft commitment is a weak signal of purchase intent.**  
   Add-to-cart actions, regardless of timing, do not reliably predict conversion.

5. **Hard commitment forms a decisive behavioral boundary.**  
   Checkout and purchase actions correspond to the highest conversion rates, shortest paths, and lowest hesitation.

---

## Decision Path Framework

Based on these findings, we propose a qualitative decision framework:

- **Browsing-only paths**  
  Passive exploration with minimal intent and near-zero conversion.

- **Comparison-augmented paths**  
  High cognitive load and hesitation with limited payoff.

- **Soft commitment paths**  
  Tentative intent that often leads to prolonged interaction without conversion.

- **Hard commitment paths**  
  Decisive behavior characterized by efficient progression to purchase.

This framework highlights that *commitment strength* is more informative than *commitment timing* or activity volume.

## Decision Framework (Visual Summary)

| Segment | What it looks like | Conversion | Avg events | Avg hesitation |
|---|---|---:|---:|---:|
| **Browsing-only** (no commitment) | View-heavy exploration → exit | **2.9%** | 11.6 | 0.108 |
| **Comparison-augmented** (no commitment) | Views + compare loops → exit | **2.4%** | 10.4 | **0.238** |
| **Soft commitment** (add_to_cart) | Add-to-cart present, often tentative | **2.1%** | 10.8 | 0.142 |
| **Hard commitment** (checkout / purchase) | Checkout/purchase boundary, decisive | **37.2%** | **9.8** | 0.125 |

**Takeaway:**  
*Commitment strength is the dominant signal of conversion intent.  
Soft commitment actions (add-to-cart) behave similarly to non-commitment paths, while hard commitment forms a clear behavioral boundary with dramatically higher conversion efficiency.*

---

## Implications

From a product analytics perspective, these results suggest:

- Early add-to-cart events should not be over-interpreted as strong intent signals.
- Friction-reduction efforts may be better targeted at comparison-heavy paths.
- Decision modeling should prioritize structural behavior patterns over aggregate metrics.

The framework is designed to be extensible and can serve as a foundation for downstream modeling or experimentation.

---

## Repository Structure

```
behavior-state-modeling
├── data/          # Generated sample data
├── notebooks/     # EDA and analysis notebooks
├── docs/          # Project logs and documentation
├── src/           # Data generation and utilities
└── README.md
```

---

## Notes

This project emphasizes interpretability and analytical reasoning rather than predictive optimization.  
All conclusions are supported by reproducible analysis in the accompanying notebooks.
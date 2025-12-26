## 2025-12-26
- Defined v0 data specification for semi-synthetic e-commerce clickstream.
- Chosen focus: decision paths, while also enabling churn-risk and engagement-quality analysis.
- Next: implement generator v0_1 and export a small sample dataset committed to the repo.

## 2025-12-26 — Initial EDA: Session Structure & Commitment Timing

### What was done
- Conducted initial exploratory data analysis (EDA) on session-level behavior using the v0_1 semi-synthetic e-commerce dataset.
- Analyzed session length distribution and compared path length between converted and non-converted sessions.
- Derived and validated a new feature, `first_cart_ratio`, representing the normalized position of the first add-to-cart event within a session.
- Performed conditional analysis restricted to sessions that include at least one add-to-cart action.
- Compared commitment timing (`first_cart_ratio`) between converted and non-converted sessions using both descriptive statistics and boxplot visualization.

### Key findings
- **Session length alone does not meaningfully distinguish conversion outcomes.**
  Converted and non-converted sessions share nearly identical medians and interquartile ranges in number of events, indicating that higher activity volume does not imply higher purchase intent.
- **Only a subset of sessions (~40%) ever reach an explicit commitment action (add-to-cart).**
  This highlights a structural separation between exploratory-only sessions and sessions that enter a commitment phase.
- **Among sessions with add-to-cart behavior, commitment timing shows a modest but consistent signal.**
  Converted sessions tend to initiate add-to-cart earlier in their decision paths, with the entire distribution (median and IQR) shifted slightly toward earlier positions, despite substantial overlap.

### Interpretation
These results suggest that decision outcomes are better explained by **path structure and the timing of key commitment actions**, rather than by overall interaction volume. Early commitment appears to be associated with higher conversion likelihood, though the effect size is moderate and non-deterministic.

### Next steps
- Move beyond scalar metrics (length, timing) to analyze **decision path structures**.
- Identify and group common session path patterns (e.g., direct purchase, comparison-heavy, wandering paths).
- Compare these path patterns in terms of conversion rate, hesitation behavior, and efficiency.

## 2025-12-26 — Decision Path Structure: Rule-based Path Types

### What was done
- Filtered sessions to decision-relevant subsets (minimum length and non-trivial paths).
- Inspected frequent path signatures to identify recurring structural patterns.
- Defined three interpretable, rule-based decision path types:
  - `browsing_only`
  - `comparison_augmented`
  - `commitment_touch`
- Assigned each decision-relevant session to a path type based solely on path structure.

### Key findings
- **Path structure strongly differentiates conversion outcomes.**
  Sessions with commitment-touch paths exhibit a substantially higher conversion rate (~24%) than browsing-only or comparison-augmented paths (~2–3%).
- **Comparison-augmented paths show the highest hesitation levels but the lowest conversion.**
  This suggests that extensive comparison behavior is associated with decision friction rather than improved outcomes.
- **Browsing-only paths remain low-conversion despite relatively long interaction sequences.**
  This further reinforces that interaction volume alone does not indicate intent.

### Interpretation
Decision outcomes are better explained by *qualitative path structure* than by path length or activity volume. Explicit commitment actions represent a critical structural boundary in user decision processes, while comparison-heavy paths may reflect stalled or indecisive behavior.

### Next steps
- Quantify differences between path types with focused visualizations.
- Examine how early commitment timing interacts with path type.
- Explore whether path types can be inferred without explicit action labels.

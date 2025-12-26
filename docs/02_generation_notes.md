# Generation Notes

## v0_1 (planned)
- Adds event-level `state_true` with 5 states
- Adds 4 user archetypes (browser/researcher/decisive/bargain_hunter)
- Introduces basic transition matrix + event emission probabilities
- Exports:
  - data/sample/v0_1/events_sample.csv
  - data/sample/v0_1/sessions_sample.csv
- Seeded generation for reproducibility

### Key sanity checks (v0_1)
- conversion rate by archetype
- average path length by archetype
- compare_rate differences across states/archetypes
- distribution of gap_time_s and dwell_time_s

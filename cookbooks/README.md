# cookbooks/

End-to-end workflows that compose agents and plugins. Each cookbook is intended to be readable as a worked example, not packaged as a product.

- **Morning dossier** — daily per-account briefing assembled across the six schema slots.
- **Pre-announcement watcher** — flags publicly observable pre-announcement signals (earnings cadence, hiring, exec movement, regulatory filings). Subject to the web-monitoring compliance disclaimer in the root README.
- **Signal velocity monitor** — tracks rate-of-change on `trigger_events` and `outcome_telemetry` per account.
- **Renewal radar** — assembles `outcome_telemetry` and `funnel_telemetry` into renewal-risk surfacing.
- **Win/loss interview integrator** — folds post-mortem interview notes into `conversation_evidence`.

All five are stubs at Day 1. The morning dossier reaches a runnable end-to-end form in Day 3.

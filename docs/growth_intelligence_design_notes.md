<!-- SPDX-License-Identifier: Apache-2.0 -->
# Growth Intelligence Design Notes

This layer is intentionally not a Gong clone. It shifts the repository from "what happened in calls?" to "where should the company create, capture, and defend demand?"

## Why These Modules

`market_share_tracker.py` uses a configurable rule-of-60 posture: a segment is not treated as owned until market share, demand share, account coverage, and high-intent capture are strong enough to defend. The 60 percent threshold is an operating heuristic for category concentration, not a universal rule. The design borrows the discipline of SaaS efficiency metrics without pretending that search interest equals revenue.

`campaign_roi_tracker.py` keeps campaign measurement tied to revenue, gross-margin payback, attribution confidence, and pipeline quality. This avoids the common trap where a campaign looks strong by attributed value but weak by account fit, sales acceptance, or payback.

`search_intent_mapper.py` treats search as a demand radar. It scores queries by intent, position gap, click-through gap, difficulty, business fit, and downstream conversion quality so growth teams can choose between content, paid capture, competitor intercept, or no action.

## Source-Backed Inputs

- Google Search Console exposes impressions, clicks, CTR, queries, pages, countries, and search appearance, which map directly to `search_intent_mapper.py` inputs.
- GA4 attribution paths report customer touchpoints, revenue, days to key events, and path length, which map to the attribution and conversion-quality fields in `campaign_roi_tracker.py`.
- HubSpot documents campaign ROI as revenue or attributed value minus campaign spend divided by spend, which is the ROI basis implemented here.
- Google Ads exposes conversion value per cost for ROAS-style reporting; this repo keeps ROAS separate from ROI so gross-margin payback is not hidden.
- McKinsey's SaaS Rule of 40 discussion highlights ARR growth, net retention, payback period, and free cash flow percentage as value-creation signals. Those are adjacent to, but separate from, the rule-of-60 market posture used here.
- Google Trends is useful as one demand signal, but Google's own documentation warns that Trends data is not a perfect mirror of search activity or polling data. The tracker therefore requires source diversity before treating a segment as board-ready.

## Model Arbitration

Growth workflows use the shared token router:

- `campaign_roi_tracker` normally uses the cheapest route because the core math is deterministic; it escalates when budget decisions or attribution conflicts are high stakes.
- `market_share_tracker` defaults to Sonnet for synthesis, and escalates when a board-visible segment is near control or demand sources conflict.
- `search_intent_mapper` uses Sonnet for query-cluster reasoning and long-context Sonnet when a large keyword universe exceeds the normal context band.

## Public References

- Google Search Console performance reports: https://support.google.com/webmasters/answer/10268906
- GA4 attribution paths: https://support.google.com/analytics/answer/10595568
- HubSpot campaign ROI: https://knowledge.hubspot.com/campaigns/analyze-your-campaign-roi
- Google Ads conversion values and ROAS: https://support.google.com/google-ads/answer/13064207
- McKinsey Rule of 40 metrics: https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/saas-and-the-rule-of-40-keys-to-the-critical-value-creation-metric
- Google Trends interpretation caveats: https://support.google.com/trends/answer/4365533
- Google Trends API alpha: https://developers.google.com/search/apis/trends

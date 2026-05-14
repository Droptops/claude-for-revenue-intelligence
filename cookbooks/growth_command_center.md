<!-- SPDX-License-Identifier: Apache-2.0 -->
# Growth Command Center

Goal: make revenue intelligence useful before a deal exists. This cookbook combines market share posture, campaign ROI, and search intent so a business can decide where to create demand, where to capture demand, and where to stop spending.

## Inputs

- Segment revenue, market revenue, or externally supplied market-share estimate.
- Brand and competitor search volumes or share-of-search exports.
- Target-account coverage and high-intent account capture.
- Campaign spend, attributed revenue, closed-won revenue, gross margin, and campaign IDs.
- Search Console or keyword-tool rows: query, impressions, clicks, position, CPC, difficulty, business fit, conversion rate.

## Workflow

1. Run `plugins/growth/market_share_tracker.py`.
   - Find segments where demand share outruns revenue share.
   - Flag rule-of-60 gaps, low account coverage, and high-intent capture leaks.
   - Escalate board-visible segments through `market_share_tracker` model arbitration.

2. Run `plugins/growth/campaign_roi_tracker.py`.
   - Calculate ROI, ROAS, gross-margin payback, attribution confidence, and pipeline quality.
   - Separate "scale" from "fix attribution" from "cut or rework."
   - Treat high ROAS with low account fit as a risk, not a win.

3. Run `plugins/growth/search_intent_mapper.py`.
   - Classify queries as buying intent, competitor intercept, problem demand, category demand, or education demand.
   - Prioritize content and paid capture where the business fit is high and the SERP gap is real.
   - Avoid chasing high-volume, low-fit query clusters.

4. Produce a growth operating memo.
   - Segment to win or defend.
   - Campaigns to scale, repair, or stop.
   - Search clusters to build, refresh, or ignore.
   - Model route and token budget for each section.

## Example Commands

```bash
python plugins/growth/market_share_tracker.py
python plugins/growth/campaign_roi_tracker.py
python plugins/growth/search_intent_mapper.py
```

## Review Checklist

- Is the growth recommendation grounded in revenue quality, not only impressions or MQLs?
- Does the segment have enough source diversity to be board-ready?
- Are paid and organic search decisions tied to actual business fit?
- Are budget changes separated from attribution cleanup?
- Does the selected model tier match the token load and decision risk?

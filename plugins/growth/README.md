<!-- SPDX-License-Identifier: Apache-2.0 -->
# growth/

Growth plugins move the repository outside a conversation-intelligence lane. They connect category demand, campaign spend, and search intent to pipeline and retention outcomes without requiring a packaged vendor platform.

Built demos:

- `market_share_tracker.py` - rule-of-60 segment posture, share-of-search proxy, high-intent account capture, and market-share defense flags.
- `campaign_roi_tracker.py` - ROI, ROAS, CAC payback, attribution confidence, and pipeline-quality triage.
- `search_intent_mapper.py` - query-level search demand, intent class, organic capture gaps, and content/campaign priority.

The first version is deterministic and connector-neutral. Operators can load data from Google Search Console, Google Trends exports, GA4 attribution paths, ad platforms, CRM campaigns, or finance-owned spend files.

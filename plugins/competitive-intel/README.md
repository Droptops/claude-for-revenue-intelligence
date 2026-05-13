<!-- SPDX-License-Identifier: Apache-2.0 -->
# competitive-intel/

Competitive-intel plugins turn public, permitted signals into reviewer-ready sales and growth artifacts.

Built demos:

- `battlecard_builder.py` - maps searched keywords, competitor terms, own proof points, and feature evidence into a factual battlecard.
- `cdn_feature_monitor.py` - compares operator-provided public asset snapshots to detect possible competitor feature or packaging changes.

Compliance posture:

- Do not bypass authentication, paywalls, rate limits, robots.txt, or Terms of Service.
- Do not crawl a competitor's CDN recursively. Use an approved URL manifest, sitemap-permitted paths, partner-provided exports, or manually reviewed public assets.
- Treat filenames and public JavaScript strings as weak signals. Human review is required before making a claim in sales material.

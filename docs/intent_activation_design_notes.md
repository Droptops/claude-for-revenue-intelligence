<!-- SPDX-License-Identifier: Apache-2.0 -->
# Intent Activation And Competitive Response Design Notes

This layer turns high-intent account signals into action without making the repo feel like another call-recording product.

## What It Adds

`plugins/growth/intent_sequence_builder.py` accepts connector-neutral 6sense/ZoomInfo-style account intent: intent score, searched topics, competitor terms, contact routes, opt-out state, and source confidence. It drafts a four-step email sequence using account-level themes. It intentionally does not say "you searched" or imply individual surveillance.

`plugins/competitive-intel/battlecard_builder.py` maps searched keywords and competitor terms into a battlecard: matched own capabilities, competitor-only signals, talk tracks, discovery questions, objections, and landmines. Claims stay evidence-linked.

`plugins/competitive-intel/cdn_feature_monitor.py` compares operator-provided public asset snapshots. It can detect possible feature-language additions or removals, but it does not crawl, fetch, bypass authentication, or make final claims. CDN and public JavaScript changes are weak signals until verified against product docs, packaging pages, or customer evidence.

## Connector-Neutral Inputs

- 6sense-style account intent topics, stages, and account fit.
- ZoomInfo-style buyer intent, contact enrichment, and routing fields.
- First-party site activity, Search Console query exports, G2/review-site category signals, and CRM campaign membership.
- Operator-reviewed competitor public asset snapshots and feature terms.

## Safety And Compliance

- Use account-level intent language. Do not claim that a named person searched a term.
- Suppress opted-out contacts and contacts without an allowed route.
- Do not scrape or monitor assets where robots.txt, Terms of Service, or source permission are not confirmed.
- Do not recursively crawl competitor CDNs. Use approved URL manifests, sitemap-permitted paths, partner-provided exports, or manually reviewed public snapshots.
- Treat public asset changes as a review queue, not proof of feature parity.

## Model Arbitration

- `intent_sequence_builder` defaults to Sonnet because it combines persona routing, keyword themes, and safe copy. It escalates for executive sequences or conflicting source confidence.
- `competitive_battlecard_builder` uses Sonnet for normal battlecards and escalates for strategic competitors or evidence conflict.
- `cdn_feature_monitor` stays on the cheapest route because diffing is deterministic; it escalates when permission, pricing, packaging, or launch signals require narrative judgment.

## Public References

- 6sense keyword management docs: https://support.6sense.com/docs/manage-keywords-1
- 6sense sales-intelligence keyword docs: https://support.6sense.com/using-keywords-for-sales-intelligence
- ZoomInfo Intent launch overview: https://zoominfotechnologiesinc.gcs-web.com/news-releases/news-release-details/zoominfo-launches-intent-solution-help-b2b-companies-identify
- FTC CAN-SPAM compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- RFC 9309 Robots Exclusion Protocol: https://www.rfc-editor.org/rfc/rfc9309
- Google robots.txt documentation: https://developers.google.com/search/docs/crawling-indexing/robots/intro

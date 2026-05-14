<!-- SPDX-License-Identifier: Apache-2.0 -->
# Intent Activation And Competitive Response

Goal: convert high-intent account signals into a compliant outbound sequence, a factual competitive battlecard, and a review queue for public competitor feature changes.

## Inputs

- Intent account: account ID, company name, source system, intent score, searched keywords/topics, source confidence, and active competitors.
- Contacts: permitted contact routes, title, persona, seniority, opt-out state, verification state, and recent engagement.
- Competitor profile: competitor terms, observed feature signals, own capabilities, proof points, and customer objections.
- Public asset snapshots: approved URL manifest, body snippets or hashes, source permission, robots confirmation, and ToS confirmation.

## Workflow

1. Run `plugins/growth/intent_sequence_builder.py`.
   - Cluster searched keywords into account-level themes.
   - Suppress contacts without a permitted route.
   - Draft a four-step sequence without saying a person searched a term.
   - Route high-stakes or low-confidence sequences through model arbitration.

2. Run `plugins/competitive-intel/battlecard_builder.py`.
   - Map the active research themes to own capabilities and competitor signals.
   - Generate talk tracks, discovery questions, objection responses, and landmines.
   - Keep every claim tied to supplied evidence.

3. Run `plugins/competitive-intel/cdn_feature_monitor.py`.
   - Compare previous and current public asset snapshots.
   - Detect feature-language additions, removals, or possible parity gaps.
   - Block use when permission, robots, or ToS status is missing.

4. Reviewer writes the final play.
   - Sequence to approved contacts.
   - Battlecard for the account team.
   - Asset-change review item for product marketing.

## Example Commands

```bash
python plugins/growth/intent_sequence_builder.py
python plugins/competitive-intel/battlecard_builder.py
python plugins/competitive-intel/cdn_feature_monitor.py
```

## Review Checklist

- Does the email avoid individual surveillance language?
- Are opted-out contacts suppressed?
- Are competitor claims evidence-backed and reviewed?
- Was every monitored asset permitted by robots.txt, ToS, and source policy?
- Are CDN changes treated as weak signals until verified?

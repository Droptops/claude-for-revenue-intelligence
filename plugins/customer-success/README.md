<!-- SPDX-License-Identifier: Apache-2.0 -->
# plugins/customer-success

Customer-success views over the six schema slots. The first built module is
`renewal_radar.py`, a deterministic churn-risk and expansion-fit scorer that
uses `outcome_telemetry`, `funnel_telemetry`, support trend labels, and usage
trend labels.

Every output is a draft for reviewer judgment. The plugin does not send
emails, update CRM, or make renewal decisions without explicit operator review.

Run the demo:

```bash
python plugins/customer-success/renewal_radar.py
```

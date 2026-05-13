<!-- SPDX-License-Identifier: Apache-2.0 -->
# cookbooks/

End-to-end workflows that compose agents and plugins. Each cookbook is intended to be readable as a worked example, not packaged as a product.

Status values: `built` (cookbook file present with steps and sample output), `stub` (file present, scaffolding only), `planned` (no file yet).

| Cookbook | File | Status |
|---|---|---|
| morning_dossier | `morning_dossier.md` | built |
| pre_announcement_watcher | `pre_announcement_watcher.md` | planned (cookbook planned; see `agents/trigger_event_monitor/pre_announcement_watcher.py` for the agent module) |
| signal_velocity_monitor | `signal_velocity_monitor.md` | planned |
| renewal_radar | `renewal_radar.md` | planned |
| win_loss_interview_integrator | `win_loss_interview_integrator.md` | planned |

Subject to the web-monitoring compliance disclaimer in the root README: any cookbook that observes external sites (pre-announcement watcher, signal velocity monitor) must be used in compliance with each target site's `robots.txt` and Terms of Service.

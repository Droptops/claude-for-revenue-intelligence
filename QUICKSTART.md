# Quickstart

## 1. Prerequisites

- Python 3.10 or later.
- An Anthropic API key (`ANTHROPIC_API_KEY`).
- Optional credentials for any source systems you intend to wire up: Salesforce, Gong, Outreach, Slack, Google Drive.

## 2. Install

```bash
pip install -r requirements.txt
```

`requirements.txt` does not yet exist — Day 1 is repo scaffold only. The install command above is the intended interface; it will fail at Day 1 and become live as the first runnable agent lands.

## 3. Cold-Start Interview

Coming Day 2. A small interactive routine that asks practice-shaping questions and writes a per-installation `CLAUDE.md` profile (anti-qualification thresholds, source-system identifiers, persona-graph definitions). The profile is local to each install and is not committed back to this repository.

Until Day 2, the root `CLAUDE.md` is a placeholder describing the cold-start flow at a glance.

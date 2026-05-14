<!-- SPDX-License-Identifier: Apache-2.0 -->
# Morning Dossier Demo

This demo runs the local scorers over committed synthetic data and prints a
morning-dossier-shaped briefing.

Run from the repository root:

```bash
python demo/morning_dossier_demo.py
```

The demo uses only stdlib Python and local files. It makes no network calls,
does not write to a CRM, and does not require external credentials. All account,
opportunity, and persona values are placeholders. URLs use `placeholder.invalid`.

The output is a draft for reviewer judgment and is intended to show how the
scorers can be composed into an operator-facing morning workflow.

The PLG fork has a separate tiny demo that proves a non-enterprise schema slot
set can run without changing the base harness:

```bash
python examples/forks/plg-self-serve/demo.py
```

<!-- SPDX-License-Identifier: Apache-2.0 -->
# finserv-enterprise

Thin overlay for a regulated financial-services enterprise motion.

What changed vs. the base harness:

- Keeps the reference `enterprise-account-based` six-slot model.
- Adds a `regulatory_filings` slot for filings, enforcement updates, and review
  gates that influence buying committees.
- Adds a stub regulatory filing monitor to the roster.
- Keeps the same anti-qualification thresholds as the reference skill until an
  operator validates different values for this motion.

This fork is a stub. It does not implement full agents.

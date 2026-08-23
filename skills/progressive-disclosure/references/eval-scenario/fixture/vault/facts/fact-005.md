# billing-api: log retention policy

General guidance for billing-api regarding log retention policy: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 56 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

Historical context: an earlier version of this setting caused a minor incident before it was tuned.
Cross-referenced against the vendor's own recommended defaults, which this deliberately overrides.

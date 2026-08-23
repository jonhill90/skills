# billing-api: TLS cert rotation cadence

General guidance for billing-api regarding TLS cert rotation cadence: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 53 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

Cross-referenced against the vendor's own recommended defaults, which this deliberately overrides.
Written down after a postmortem so the reasoning would not have to be re-derived from a chat log.

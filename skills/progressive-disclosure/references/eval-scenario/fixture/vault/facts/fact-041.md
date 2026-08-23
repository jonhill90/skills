# search-indexer: TLS cert rotation cadence

General guidance for search-indexer regarding TLS cert rotation cadence: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 113 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

No customer-facing impact has ever been traced to this setting directly.
Cross-referenced against the vendor's own recommended defaults, which this deliberately overrides.

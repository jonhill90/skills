# session-gateway: TLS cert rotation cadence

General guidance for session-gateway regarding TLS cert rotation cadence: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 11 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
Cross-referenced against the vendor's own recommended defaults, which this deliberately overrides.

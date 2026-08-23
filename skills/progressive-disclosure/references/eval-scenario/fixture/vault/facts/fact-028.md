# ingest-worker: circuit-breaker thresholds

General guidance for ingest-worker regarding circuit-breaker thresholds: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 74 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
This note was last reviewed during a routine ops sweep and no action was needed at the time.

# ingest-worker: cache invalidation rule

General guidance for ingest-worker regarding cache invalidation rule: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 32 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
No customer-facing impact has ever been traced to this setting directly.

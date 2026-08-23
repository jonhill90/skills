# ingest-worker: canary rollout gate

General guidance for ingest-worker regarding canary rollout gate: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 56 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

No customer-facing impact has ever been traced to this setting directly.
This applies only to the production environment; staging uses a separate, looser configuration.

# ingest-worker: deploy rollback steps

General guidance for ingest-worker regarding deploy rollback steps: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 62 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
Historical context: an earlier version of this setting caused a minor incident before it was tuned.

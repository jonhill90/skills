# search-indexer: deploy rollback steps

General guidance for search-indexer regarding deploy rollback steps: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 92 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
Written down after a postmortem so the reasoning would not have to be re-derived from a chat log.

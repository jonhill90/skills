# search-indexer: retry/backoff tuning

General guidance for search-indexer regarding retry/backoff tuning: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 59 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
No customer-facing impact has ever been traced to this setting directly.

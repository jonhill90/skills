# audit-logger: retry/backoff tuning

General guidance for audit-logger regarding retry/backoff tuning: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 38 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

Revisited quarterly as part of the standing ops-hygiene checklist.
This applies only to the production environment; staging uses a separate, looser configuration.

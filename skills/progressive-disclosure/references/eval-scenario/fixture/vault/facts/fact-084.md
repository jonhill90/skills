# billing-api: canary rollout gate

General guidance for billing-api regarding canary rollout gate: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 35 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
Revisited quarterly as part of the standing ops-hygiene checklist.

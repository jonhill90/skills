# notify-relay: retry/backoff tuning

General guidance for notify-relay regarding retry/backoff tuning: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 107 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

Cross-referenced against the vendor's own recommended defaults, which this deliberately overrides.
This applies only to the production environment; staging uses a separate, looser configuration.

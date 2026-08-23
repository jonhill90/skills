# billing-api: rate-limit thresholds

General guidance for billing-api regarding rate-limit thresholds: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 41 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

The team agreed this value should not be changed without a second reviewer signing off.
This applies only to the production environment; staging uses a separate, looser configuration.

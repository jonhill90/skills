# media-transcoder: canary rollout gate

General guidance for media-transcoder regarding canary rollout gate: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 8 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

This applies only to the production environment; staging uses a separate, looser configuration.
Historical context: an earlier version of this setting caused a minor incident before it was tuned.

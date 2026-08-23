# notify-relay: cache invalidation rule

General guidance for notify-relay regarding cache invalidation rule: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 53 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

Written down after a postmortem so the reasoning would not have to be re-derived from a chat log.
Historical context: an earlier version of this setting caused a minor incident before it was tuned.

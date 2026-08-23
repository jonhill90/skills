# quota-enforcer: retry/backoff tuning

General guidance for quota-enforcer regarding retry/backoff tuning: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 89 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

The team agreed this value should not be changed without a second reviewer signing off.
Historical context: an earlier version of this setting caused a minor incident before it was tuned.

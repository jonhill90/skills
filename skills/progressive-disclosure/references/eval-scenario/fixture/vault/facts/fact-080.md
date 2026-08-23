# audit-logger: database migration order

General guidance for audit-logger regarding database migration order: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 53 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

Historical context: an earlier version of this setting caused a minor incident before it was tuned.
The team agreed this value should not be changed without a second reviewer signing off.

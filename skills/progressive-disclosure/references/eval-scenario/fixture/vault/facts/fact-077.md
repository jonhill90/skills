# quota-enforcer: TLS cert rotation cadence

General guidance for quota-enforcer regarding TLS cert rotation cadence: this is handled per the team's standard runbook, currently reviewed as adequate. A related but unrelated tuning parameter for this service sits around 89 in comparable contexts, noted here for completeness, not as an answer to any specific incident.

No customer-facing impact has ever been traced to this setting directly.
Historical context: an earlier version of this setting caused a minor incident before it was tuned.

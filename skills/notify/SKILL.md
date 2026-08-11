---
name: notify
description: Send a short, structured message to a human on a configured outbound channel (iMessage today) from the terminal, so a stalled or escalated agent loop can reach someone who's away from the machine. Owns sending only, not escalation policy — the caller decides what's worth interrupting a human for. Dry-run by default; sending requires an explicit flag and a real send failure exits non-zero. User-invoked only — call this deliberately from a caller that has already decided to notify (e.g. a supervisor's escalate state), never automatically because a task felt important.
---

# Notify

An autonomous loop that stalls while its operator is away stays stalled
until someone happens to look. This skill is the outbound half of that
gap: one script that sends a short message on a configured channel and
tells the truth about whether it worked.

## Reach for this when

- A caller has already decided a human needs to know something *now* —
  typically because it owns a health/escalation state machine (a
  supervisor's `escalate` state, a CI failure gate) — and needs to
  actually deliver that decision outside the terminal.

## Do not reach for this when

- You are deciding *whether* something is worth interrupting a human
  for. That judgement belongs to the caller, not this skill. A `notify`
  that also decided when to fire would make its caller's escalation
  logic impossible to reason about separately.
- The task just "feels important." This is a deliberate, user-invoked
  tool, not a discipline the agent reaches for on its own.

## What this owns, and what it does not

Owns: sending a short message on whichever channel is configured, dry-run
by default, real send behind an explicit flag, dedup/rate-limit so a loop
messaging on every tick doesn't become worse than silence, and a failure
path that is loud rather than swallowed.

Does not own: deciding when to notify, what the message should say beyond
"short and state-bearing," or wiring this into any particular watchdog or
loop. That integration is the caller's job.

## Channel priority

Per [jonhill90/skills#146](https://github.com/jonhill90/skills/issues/146):

1. **iMessage — built.** No third-party service, no credential on a Mac;
   Messages.app is already signed in. This is the only channel this
   skill sends on today.
2. Telegram, 3. Discord, 4. Teams — designed, not built. See
   [`references/channels.md`](references/channels.md) for the shape each
   would take if a future change needs one. Build only if iMessage is
   genuinely blocked for a given setup — one working channel closes the
   operational gap; five is not the goal.
5. Slack — deferred indefinitely, unused since 2019. Do not build it.

## Configuration

Everything channel- and credential-related comes from the environment.
Nothing is hardcoded and nothing is committed.

| Variable | Required | Default | Meaning |
|---|---|---|---|
| `NOTIFY_CHANNEL` | no | `imessage` | which channel to send on |
| `NOTIFY_IMESSAGE_TARGET` | yes, for iMessage | — | the phone number or Apple ID email to send to (your own, for a self-notification) |
| `NOTIFY_STATE_DIR` | no | `~/.local/state/notify` | where the dedup/rate-limit state and local log live |
| `NOTIFY_DEDUP_WINDOW_SECONDS` | no | `300` | suppress an identical message sent again within this window |
| `NOTIFY_MIN_INTERVAL_SECONDS` | no | `60` | suppress *any* send within this long of the last one |

iMessage needs no credential — that's part of why it's first per the
issue. There is no config file in this repository to edit; set the
environment where the caller runs.

## Usage

```bash
# Dry run (default) — prints exactly what would be sent, sends nothing, exits 0.
python3 scripts/notify.py --message "watchdog: escalate — 3 restarts/hr, stopped."

# Real send — requires the flag explicitly.
NOTIFY_IMESSAGE_TARGET="you@example.com" \
  python3 scripts/notify.py --message "watchdog: escalate — check tmux." --send
```

- `--message` (required) — kept under 200 characters by the script; a
  message that doesn't fit on a lock screen defeats the point. State
  what stopped, what it needs, and where to look — not a transcript
  dump.
- `--send` — actually deliver. Every other invocation, including every
  test, omits this and gets a dry run instead.
- `--force` — bypass dedup/rate-limit suppression for one send. Use
  sparingly; the suppression exists because a loop that messages on
  every tick is worse than silence.
- `--channel` — override `$NOTIFY_CHANNEL`. Anything other than
  `imessage` currently exits 2 with a message pointing at
  `references/channels.md`, rather than silently doing nothing.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | dry run printed, message sent, or message intentionally suppressed (deduped / rate-limited) |
| `1` | a send was attempted and failed — always logged to `$NOTIFY_STATE_DIR/notify.log` first |
| `2` | usage or configuration error (missing `--message`, oversized message, unknown or unbuilt channel, missing target) |

An unreachable channel must never look like "nothing to report" — that
is the fail-open shape this comes from
(jonhill90/skills#146). Exit 1 plus a local log line is the contract a
caller can check.

## Testing this skill

Sending a message is an outward-facing action — treat it like any other
send to a live system.

- **Always dry-run while iterating.** Every invocation above without
  `--send` prints what would happen and touches no state, no network,
  no `Messages.app`.
- **`--self-test`** exercises the dedup, rate-limit, config-validation,
  and logging logic against a scratch state directory with no real send
  involved:

  ```bash
  python3 scripts/notify.py --self-test
  ```

- **At most one live send, ever, per change.** If you need to confirm
  the real path works, send exactly one message to yourself, clearly
  marked as a test, and record its exact content in whatever report
  you're producing. Do not loop, retry, or fan this out to confirm it
  "really" worked — one send is the check.
- **If a self-send doesn't produce a notification, report that.** Do
  not start experimenting with dedicated threads, group chats, or other
  recipients to chase a notification — that's a scope creep this skill
  explicitly avoids (see Channel priority above; the issue anticipates
  self-messaging may not notify and treats that as information, not a
  bug to iterate around).

## Bundled scripts

| Script | Use |
|---|---|
| `notify.py` | dry-run/live sender for the configured channel; owns dedup, rate-limiting, and local failure logging |

## Notes

- This skill does not modify, read, or depend on any watchdog, roster,
  or supervisor state file. Wiring a caller's escalation logic to this
  script is a separate change (jonhill90/agent-dotfiles#50).
- Rate-limiting and dedup state live under `$NOTIFY_STATE_DIR`
  (`~/.local/state/notify` by default) — local to the machine, never
  committed, never read by this repository's validator.

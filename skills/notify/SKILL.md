---
name: notify
description: Send a short, structured message to a human on a configured outbound channel (Telegram first, iMessage as a Mac-only fallback) from the terminal, so a stalled or escalated agent loop can reach someone who's away from the machine. Owns sending only, not escalation policy — the caller decides what's worth interrupting a human for. Dry-run by default; sending requires an explicit flag and a real send failure exits non-zero. User-invoked only — call this deliberately from a caller that has already decided to notify (e.g. a supervisor's escalate state), never automatically because a task felt important.
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

Per [jonhill90/skills#146](https://github.com/jonhill90/skills/issues/146),
Jon later re-ordered this (2026-08-11) once Telegram proved to be the only
channel that actually reached his phone: Telegram works from any machine
and does not depend on macOS automation permissions, so it goes first and
iMessage becomes the fallback rather than the primary.

1. **Telegram — built, tried first.** Bot API over HTTPS; works from any
   machine, not just a Mac.
2. **iMessage — built, Mac-only fallback.** No credential on a Mac;
   Messages.app is already signed in. Tried only if Telegram isn't
   configured or its send fails.
3. Discord, 4. Teams — designed, not built. See
   [`references/channels.md`](references/channels.md) for the shape each
   would take if a future change needs one. Build only if both Telegram and
   iMessage are genuinely blocked for a given setup — one working channel
   closes the operational gap; five is not the goal.
5. Slack — deferred indefinitely, unused since 2019. Do not build it.

## Configuration

Everything channel- and credential-related comes from the environment.
Nothing is hardcoded and nothing is committed.

| Variable | Required | Default | Meaning |
|---|---|---|---|
| `NOTIFY_CHANNEL` | no | `auto` | `auto` tries telegram then imessage, in that order, stopping at the first that accepts the message; `telegram` or `imessage` forces exactly one channel with no fallback |
| `AGENT_NOTIFY_TELEGRAM_TOKEN` | yes, for Telegram | — | bot token from `@BotFather` |
| `AGENT_NOTIFY_TELEGRAM_CHAT_ID` | yes, for Telegram | — | the chat to send to (must have started a chat with the bot at least once) |
| `AGENT_NOTIFY_IMESSAGE_TO` | yes, for iMessage | — | **canonical.** The phone number or Apple ID email to send to (your own, for a self-notification). Matches the `AGENT_NOTIFY_*` prefix Telegram already uses and is the name `agent-dotfiles/scripts/supervisor/notify.sh` reads. |
| `NOTIFY_IMESSAGE_TARGET` | no | — | **deprecated alias** for `AGENT_NOTIFY_IMESSAGE_TO`, kept working so an existing `notify.env` or shell profile doesn't break. If both are set, `AGENT_NOTIFY_IMESSAGE_TO` wins. New config should use the canonical name (jonhill90/skills#152). |
| `NOTIFY_STATE_DIR` | no | `~/.local/state/notify` | where the dedup/rate-limit state and local log live |
| `NOTIFY_DEDUP_WINDOW_SECONDS` | no | `300` | suppress an identical message sent again within this window |
| `NOTIFY_MIN_INTERVAL_SECONDS` | no | `60` | suppress *any* send within this long of the last one |

Credentials must come from the environment — an untracked, 0600 env file
loaded by the caller is the pattern this skill assumes, the same one
`agent-dotfiles/scripts/supervisor/notify.sh` uses. Never put a token
inline in a command, a script, or anything committed to this repository.
There is no config file in this repository to edit; set the environment
where the caller runs.

## Usage

```bash
# Dry run (default) — prints exactly what would be sent, sends nothing, exits 0.
python3 scripts/notify.py --message "watchdog: escalate — 3 restarts/hr, stopped."

# Real send, auto channel selection (Telegram, then iMessage fallback).
AGENT_NOTIFY_TELEGRAM_TOKEN="..." AGENT_NOTIFY_TELEGRAM_CHAT_ID="..." \
AGENT_NOTIFY_IMESSAGE_TO="you@example.com" \
  python3 scripts/notify.py --message "watchdog: escalate — check tmux." --send

# Force a single channel — no fallback to the other if it fails.
AGENT_NOTIFY_IMESSAGE_TO="you@example.com" \
  python3 scripts/notify.py --message "..." --channel imessage --send
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
- `--channel` — override `$NOTIFY_CHANNEL`. `auto` (default) tries
  telegram then imessage with no further fallback once one is named
  explicitly. `discord`, `teams`, and `slack` exit 2 with a message
  pointing at `references/channels.md`, rather than silently doing
  nothing.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | dry run printed, message sent, or message intentionally suppressed (deduped / rate-limited) |
| `1` | a send was attempted and failed on every candidate channel (just `--channel imessage` itself, when forced explicitly) — always logged to `$NOTIFY_STATE_DIR/notify.log` first |
| `2` | usage or configuration error (missing `--message`, oversized message, unknown or unbuilt channel, no channel configured at all) |

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

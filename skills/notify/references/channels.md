# Planned channels — designed, not built

Per [jonhill90/skills#146](https://github.com/jonhill90/skills/issues/146),
Telegram and iMessage are the two built channels — Telegram tried first,
iMessage as a Mac-only fallback — and `scripts/notify.py` is the single
canonical sender for both. Discord and Teams below are recorded so a
future change that adds one of them starts from an agreed shape instead of
a blank page — they are not partial implementations and
`scripts/notify.py --channel <name>` for either exits 2 on purpose.

Build one of these only if both Telegram and iMessage are genuinely
blocked for a given setup. One working channel is the requirement; this
list exists for portability, not because five channels are the goal.

## Telegram (priority 1, built)

- Transport: Telegram Bot API, `POST
  https://api.telegram.org/bot<token>/sendMessage` with `chat_id` and
  `text`.
- Credential: a bot token from `@BotFather`, plus the target `chat_id`
  (the recipient must have started a chat with the bot at least once).
  Both from environment (`AGENT_NOTIFY_TELEGRAM_TOKEN`,
  `AGENT_NOTIFY_TELEGRAM_CHAT_ID` — the same names
  `agent-dotfiles/scripts/supervisor/notify.sh` already used, kept
  identical rather than renamed so an existing env file works unchanged),
  never committed.
- Failure shape: non-2xx HTTP response, or a network error reaching
  `api.telegram.org` — both map to `SendError`, logged and then either
  falls through to iMessage (`--channel auto`, the default) or exits 1
  (an explicit `--channel telegram`).
- Why first: works from any machine with outbound HTTPS, not tied to one
  Mac's automation permissions — the reason Jon re-ordered priority ahead
  of iMessage on 2026-08-11 after Telegram proved to be the only channel
  that actually reached his phone.

## iMessage (priority 2, built, Mac-only fallback)

- Transport: `Messages.app` via AppleScript/`osascript`.
- Credential: none — iMessage on a Mac is already signed in. Set
  `AGENT_NOTIFY_IMESSAGE_TO` to the recipient (phone number or Apple ID
  email) — canonical since jonhill90/skills#152, matching
  `agent-dotfiles/scripts/supervisor/notify.sh`.
  `NOTIFY_IMESSAGE_TARGET` still works as a deprecated alias.
- Failure shape: `osascript` exiting non-zero, or timing out (often an
  unacknowledged Automation permission dialog) — both map to `SendError`.
- Why second: costs nothing extra to keep since it was already built, but
  depends on being on a specific signed-in Mac, which Telegram does not.

## Discord (priority 3)

- Transport: an incoming webhook URL,
  `POST <webhook_url>` with a JSON body `{"content": "..."}`.
- Credential: the webhook URL itself is the secret
  (`NOTIFY_DISCORD_WEBHOOK_URL`) — treat it like a token, never commit
  it, never log it in full (log path/host only if a failure needs
  logging).
- Failure shape: non-2xx from Discord, or the webhook having been
  deleted/regenerated server-side (404) — the latter is worth a
  specific local log line since it means the channel is silently dead
  until someone re-creates the webhook.

## Teams (priority 4)

- Jon will handle this one; recorded here only so the shape is
  agreed if it needs a stand-in sooner.
- Transport: an Incoming Webhook connector URL, `POST <webhook_url>`
  with an Adaptive Card or legacy `MessageCard` JSON body.
- Credential: webhook URL from environment
  (`NOTIFY_TEAMS_WEBHOOK_URL`), same handling as the Discord webhook.

## Slack — deferred indefinitely

Unused since 2019 per the issue. Do not build this without a fresh
decision to revisit it; nothing here should be read as an implicit
green light.

## Shared contract for any future channel

Whatever channel gets built next should keep the same shape
`scripts/notify.py` already has for Telegram and iMessage, so the
caller-facing interface (`--message`, `--send`, `--force`, exit codes,
dedup/rate-limit, local logging) does not change per channel:

1. A `channel_config_error()` branch that returns a string when the
   channel's required environment variable(s) are missing — checked even
   during a dry run, and for `auto` mode before deciding which channels
   are candidates.
2. A `send_<channel>()` function that raises `SendError` with the
   underlying failure detail (HTTP status, stderr, etc.) rather than
   swallowing it.
3. Add the channel to `CHANNEL_ORDER` at the position matching its
   priority if `auto` mode should try it automatically; leave it out of
   `CHANNEL_ORDER` (but in `SUPPORTED_CHANNELS`) if it should only ever be
   reached with an explicit `--channel`.
4. No new suppression logic — dedup and rate-limiting are channel-agnostic;
   `auto` mode keys on message content alone since the caller doesn't care
   which channel ultimately delivered a repeat, and an explicit
   `--channel` keys on `(channel, target, message)` as before.

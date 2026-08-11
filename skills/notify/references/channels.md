# Planned channels — designed, not built

Per [jonhill90/skills#146](https://github.com/jonhill90/skills/issues/146),
only iMessage sends today. These are recorded so a future change that adds
one of them starts from an agreed shape instead of a blank page — they are
not partial implementations and `scripts/notify.py --channel <name>` for
any of these exits 2 on purpose.

Build one of these only if iMessage is genuinely blocked for a given
setup (e.g. no Mac available). One working channel is the requirement;
this list exists for portability, not because five channels are the goal.

## Telegram (priority 2)

- Transport: Telegram Bot API, `POST
  https://api.telegram.org/bot<token>/sendMessage` with `chat_id` and
  `text`.
- Credential: a bot token from `@BotFather`, plus the target `chat_id`
  (the recipient must have started a chat with the bot at least once).
  Both from environment (`NOTIFY_TELEGRAM_TOKEN`,
  `NOTIFY_TELEGRAM_CHAT_ID`), never committed.
- Failure shape: non-2xx HTTP response, or a network error reaching
  `api.telegram.org` — both should map to the same `SendError` exit-1
  path this skill already uses for iMessage.
- Why second: bot API is trivial to script and works from any machine
  with outbound HTTPS, not just a Mac.

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
`scripts/notify.py` already has for iMessage, so the caller-facing
interface (`--message`, `--send`, `--force`, exit codes, dedup/rate-limit,
local logging) does not change per channel:

1. A `resolve_target()`-style function that raises `ConfigError` when the
   channel's required environment variable(s) are missing — checked even
   during a dry run.
2. A `send_<channel>()` function that raises `SendError` with the
   underlying failure detail (HTTP status, stderr, etc.) rather than
   swallowing it.
3. No new suppression logic — dedup and rate-limiting are channel-agnostic
   and already keyed on `(channel, target, message)`.

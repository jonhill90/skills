# ingest-worker: retry/backoff tuning

After the last two incidents involving ingest-worker, the retry backoff was tuned by hand rather than left at the client library's default. The configured maximum retry backoff for ingest-worker is **47 seconds**, set deliberately below the downstream timeout so a retry storm cannot outlast the caller's own patience.

No customer-facing impact has ever been traced to this setting directly.
This note was last reviewed during a routine ops sweep and no action was needed at the time.

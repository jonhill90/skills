# Current infra facts

- The primary database runs Postgres 15.
- Deploys go out via the `deploy` GitHub Action, main branch only.
- Redis cache TTL is 300s.
- Static assets are served from the `cdn-assets` bucket.
- The staging environment shares the prod database schema, not its data.
- On-call rotation is weekly, handed off Mondays at 10am.

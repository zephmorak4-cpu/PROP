# Free Render Operating Mode

Render Free web services spin down after idle time. LI-X handles this by using
GitHub Actions as an external clock.

## Model

- Render hosts the HTTP API.
- Render's in-process scheduler should be disabled.
- GitHub Actions calls admin endpoints on a schedule.
- Supabase stores all persistent state.

## Workflow

`.github/workflows/lix-external-clock.yml` runs every 10 minutes and:

1. Wakes the Render service through `/health`.
2. Refreshes pair rankings every 30 minutes.
3. Runs `/admin/scan-now`.
4. Runs `/admin/trade-health/evaluate`.

Required GitHub Actions secrets:

```text
LIX_BASE_URL
LIX_ADMIN_API_KEY
```

Current production values:

```text
LIX_BASE_URL=https://lix-forex-intelligence.onrender.com
```

Do not store `LIX_ADMIN_API_KEY` directly in the workflow file.

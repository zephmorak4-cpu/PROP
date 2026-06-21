# Render Deployment

LI-X is ready to run as a Render Docker web service.

## Deployment Options

Preferred:

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from the GitHub repository.
3. Render will read `render.yaml` and create the Docker web service.

Alternative:

1. Create a new Render Web Service manually.
2. Select Docker as the runtime.
3. Use this repository as the source.
4. Set health check path to `/health`.

## Required Environment Variables

Set these in Render's environment settings:

```env
ENVIRONMENT=production
LOG_LEVEL=INFO
SCHEDULER_ENABLED=true

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_ADMIN_IDS=

SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
FINANCIAL_MODELING_PREP_API_KEY=
OPENAI_API_KEY=

ADMIN_API_KEY=
```

## Required Pre-Deploy Step

Apply `db/migrations/001_lix_core.sql` in Supabase project:

`exlkvqtafjpfftuhewqq`

Without the migration, the service can boot, but signal persistence and trade
lifecycle writes will fail.

## Smoke Test

After deploy:

```bash
curl https://YOUR_RENDER_SERVICE.onrender.com/health
```

Telegram test:

```bash
curl -X POST https://YOUR_RENDER_SERVICE.onrender.com/admin/test-telegram \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY"
```

# LI-X Institutional Forex Intelligence

LI-X is a Telegram-based forex research desk. It scans market data, ranks pairs,
generates manual trade ideas, monitors active trade state, and sends management
recommendations. It does not place broker orders.

## Current State

This repository is a clean LI-X scaffold because the legacy Telegram trading
system was not present in the workspace at build start. Legacy migration hooks
are represented as explicit architecture boundaries so old decision engines
cannot be mixed into LI-X later.

## Required Runtime Environment

Copy `.env.example` to `.env` locally or configure the same variables in Render.
Do not commit real secrets.

Supabase stores both persistent data and runtime state. Financial Modeling Prep
is optional at startup; if it is missing, LI-X will boot with degraded news
capability and report that in health checks.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn lix.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

Admin endpoints require the `X-Admin-Key` header matching `ADMIN_API_KEY`.

## Deploy On Render

Use `render.yaml` as the Blueprint. The service runs from the Dockerfile and
binds to Render's injected `PORT`.

Before enabling live scans:

1. Apply `db/migrations/001_lix_core.sql` in Supabase project `exlkvqtafjpfftuhewqq`.
2. Add all secret environment variables in Render.
3. Call `/admin/test-telegram` with the `X-Admin-Key` header.
4. Call `/admin/scan-now` once before relying on the scheduler.

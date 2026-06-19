# LI-X Migration Report

## Workspace Audit

Path audited: `C:\Users\HP\Documents\PROP`

The workspace did not contain the previous Telegram forex signal system. It
contained an empty Git repository when development started. Because of that,
there were no legacy strategy engines, signal generators, schedulers, Telegram
workers, or database models available to inspect or remove.

## Decision

Development started as a clean LI-X implementation. The project is structured so
all trade decisions pass through one class:

`lix.intelligence.engine.LixIntelligenceEngine`

Legacy code should not be added beside it. If the previous system is later
copied into this repository, old trading logic must be disabled before any
scheduler or Telegram sender is enabled.

## Preserved Infrastructure Target

The system is prepared to reuse existing infrastructure through environment
variables:

- Telegram bot token, chat ID, and admin IDs
- Supabase URL and keys
- Alpha Vantage
- Finnhub
- Financial Modeling Prep for economic calendar data when available
- OpenAI for report/explanation assistance only

No secrets are committed.

## Files Created

- `src/lix/main.py`: FastAPI entrypoint and health endpoints
- `src/lix/config.py`: environment-driven runtime configuration
- `src/lix/intelligence/engine.py`: single LI-X decision engine
- `src/lix/providers/market_data_provider.py`: provider abstraction
- `src/lix/providers/alpha_vantage.py`: Alpha Vantage adapter
- `src/lix/strategies/*`: modular strategy engines
- `src/lix/telegram/client.py`: Telegram delivery service
- `src/lix/db/repository.py`: Supabase persistence wrapper
- `src/lix/cache/redis_cache.py`: Redis cache wrapper
- `src/lix/jobs/scheduler.py`: LI-X-only scheduler
- `db/migrations/001_lix_core.sql`: Supabase schema

## Credential Status

Provided by user, but not stored in repo:

- Alpha Vantage API key
- Finnhub API key
- OpenAI API key
- Supabase URL
- Supabase anon key
- Supabase service role key
- Telegram bot token
- Telegram chat/admin ID candidate

Still needed or incomplete:

- `FINANCIAL_MODELING_PREP_API_KEY`: provided by user, configure as an environment variable

## Current Limitations

- Strategy engines other than Asian Liquidity Sweep are placeholders.
- Supabase is now used for runtime state; Redis is not required.
- No production Telegram send test has been run.
- Supabase migration has not been applied.

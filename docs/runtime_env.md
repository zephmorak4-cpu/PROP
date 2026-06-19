# Runtime Environment

Configure these variables in Railway or a local `.env` file.

Required for live operation:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_ADMIN_IDS=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
ALPHA_VANTAGE_API_KEY=
ADMIN_API_KEY=
```

Recommended for full LI-X capability:

```env
FINNHUB_API_KEY=
FINANCIAL_MODELING_PREP_API_KEY=
OPENAI_API_KEY=
```

Runtime state is stored in Supabase using `lix_runtime_state`; Redis is not required.

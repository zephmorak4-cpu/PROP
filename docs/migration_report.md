# LI-X v2 Migration Report

## Objective

LI-X v2 is a controlled migration of the Telegram forex signal bot into a
single-strategy decision-support system. It does not place trades.

The only active signal engine after this migration is:

```text
Asian Liquidity Sweep
```

## Phase 1 Audit

### Existing Trading Logic

| Component | Decision | Notes |
| --- | --- | --- |
| `src/lix/strategies/asian_liquidity_sweep.py` | Refactor | Rebuilt as the only active signal strategy. |
| `src/lix/strategies/base.py` | Keep | Provider-neutral strategy interface. |
| `src/lix/strategies/key_level_rejection.py` | Remove | Legacy multi-strategy path. |
| `src/lix/strategies/liquidity_grab.py` | Remove | Legacy multi-strategy path. |
| `src/lix/strategies/london_expansion.py` | Remove | Legacy multi-strategy path. |
| `src/lix/strategies/monday_gap.py` | Remove | Legacy multi-strategy path. |
| `src/lix/strategies/news_continuation.py` | Remove | Legacy multi-strategy path. |
| `src/lix/strategies/volatility_expansion.py` | Remove | Legacy multi-strategy path. |
| `src/lix/intelligence/engine.py` | Refactor | Now instantiates only Asian Liquidity Sweep. |
| `src/lix/intelligence/confidence.py` | Refactor | Removed legacy strategy-specific confidence exceptions. |
| `src/lix/risk/manager.py` | Refactor | Added basic RR validation. |
| `src/lix/services/market_scanner.py` | Keep | Still handles duplicate suppression, persistence, and Telegram dispatch. |
| `src/lix/services/trade_monitor.py` | Keep | Preserved trade lifecycle monitoring. |
| `src/lix/jobs/scheduler.py` | Refactor | Scan and trade monitoring run every minute in-process. |
| `src/lix/backtesting/engine.py` | Add | Backtesting scaffold for Asian Liquidity Sweep research. |
| `src/lix/monitoring/loss_review.py` | Add | Loss-review scaffold for post-trade analysis. |

### Existing APIs

All integrations are preserved:

- Telegram Bot API
- Supabase
- Twelve Data
- Financial Modeling Prep
- Alpha Vantage
- Finnhub
- OpenAI
- Render / Railway deployment files
- GitHub Actions external clock

No new credentials are required for this migration.

### Existing Database

Historical tables are preserved:

- `lix_signals`
- `lix_trade_updates`
- `lix_active_trades`
- `lix_pair_rankings`
- `lix_market_regimes`
- `lix_strategy_performance`
- `lix_risk_statistics`
- `lix_daily_reports`
- `lix_weekly_reports`
- `lix_runtime_state`

Added non-destructive migration:

- `db/migrations/002_lix_v2_asian_sweep.sql`

New tables:

- `lix_performance_metrics`
- `lix_loss_reviews`
- `lix_market_sessions`
- `lix_pair_statistics`

## Phase 2 Removed Legacy Trading Engine

Removed files:

- `src/lix/strategies/key_level_rejection.py`
- `src/lix/strategies/liquidity_grab.py`
- `src/lix/strategies/london_expansion.py`
- `src/lix/strategies/monday_gap.py`
- `src/lix/strategies/news_continuation.py`
- `src/lix/strategies/volatility_expansion.py`

The strategy directory now contains only:

- `base.py`
- `asian_liquidity_sweep.py`

## Phase 3 New Asian Sweep Engine

The strategy now requires:

- Asian session high/low from configured UTC session hours
- London-only entries
- Clear liquidity sweep beyond an ATR-based buffer
- Rejection candle or displacement candle
- Market structure shift after the sweep
- ATR minimum volatility filter
- Structural stop beyond the sweep
- Minimum reward-to-risk on TP1
- Confidence threshold default of 85

## Scheduler

In-process scheduler:

- Market scan: every 1 minute
- Trade monitoring: every 1 minute
- Pair ranking/news cache refresh cadence: 5 minutes
- Daily report: configured end-of-day cron

Render free mode still uses the external GitHub Actions clock because the Render
instance can sleep.

## Tests

Validation includes:

- Asian low sweep BUY detection
- Asian high sweep SELL detection
- London session rejection
- Single active engine validation
- Backtesting module behavior
- Loss-review module behavior
- Scanner duplicate and cooldown behavior
- Trade monitor lifecycle behavior
- Provider parsing
- Telegram rejection behavior

## Remaining Risks

- Live signal volume will drop because the confidence gate is now 85 and the
  setup requires full sweep, rejection, structure shift, and RR confirmation.
- Spread filtering is passive until a market-data provider returns spread.
- Loss review and backtesting scaffolds exist, but full historical report export
  still needs a later implementation pass.

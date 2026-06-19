create table if not exists public.lix_signals (
  id uuid primary key default gen_random_uuid(),
  pair text not null,
  direction text not null check (direction in ('BUY', 'SELL')),
  strategy text not null,
  confidence integer not null check (confidence >= 0 and confidence <= 100),
  entry numeric not null,
  stop_loss numeric not null,
  take_profits jsonb not null default '[]'::jsonb,
  risk_percent numeric not null,
  explanation text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.lix_trade_updates (
  id uuid primary key default gen_random_uuid(),
  pair text not null,
  action text not null,
  confidence integer not null check (confidence >= 0 and confidence <= 100),
  reason text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.lix_active_trades (
  id uuid primary key default gen_random_uuid(),
  pair text not null,
  direction text not null check (direction in ('BUY', 'SELL')),
  strategy text not null,
  entry numeric not null,
  stop_loss numeric not null,
  take_profits jsonb not null default '[]'::jsonb,
  confidence integer not null check (confidence >= 0 and confidence <= 100),
  risk_percent numeric not null,
  status text not null default 'active' check (status in ('active', 'closed')),
  reached_targets jsonb not null default '[]'::jsonb,
  break_even_sent boolean not null default false,
  emergency_exit_sent boolean not null default false,
  opened_at timestamptz not null default now()
);

create table if not exists public.lix_pair_rankings (
  id uuid primary key default gen_random_uuid(),
  pair text not null,
  score integer not null check (score >= 0 and score <= 100),
  reasons jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.lix_market_regimes (
  id uuid primary key default gen_random_uuid(),
  pair text not null,
  regime text not null,
  timeframe text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.lix_strategy_performance (
  id uuid primary key default gen_random_uuid(),
  strategy text not null,
  pair text not null,
  session text,
  market_regime text,
  wins integer not null default 0,
  losses integer not null default 0,
  average_rr numeric not null default 0,
  drawdown_contribution numeric not null default 0,
  updated_at timestamptz not null default now(),
  unique(strategy, pair, session, market_regime)
);

create table if not exists public.lix_risk_statistics (
  id uuid primary key default gen_random_uuid(),
  trading_day date not null,
  daily_drawdown numeric not null default 0,
  consecutive_losses integer not null default 0,
  max_exposure_recommendation numeric not null default 0,
  created_at timestamptz not null default now(),
  unique(trading_day)
);

create table if not exists public.lix_daily_reports (
  id uuid primary key default gen_random_uuid(),
  report_date date not null unique,
  total_signals integer not null default 0,
  wins integer not null default 0,
  losses integer not null default 0,
  average_rr numeric not null default 0,
  best_strategy text,
  worst_strategy text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.lix_weekly_reports (
  id uuid primary key default gen_random_uuid(),
  week_start date not null unique,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.lix_runtime_state (
  key text primary key,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create index if not exists lix_signals_pair_created_idx
  on public.lix_signals(pair, created_at desc);

create index if not exists lix_active_trades_status_idx
  on public.lix_active_trades(status, opened_at desc);

create index if not exists lix_pair_rankings_created_idx
  on public.lix_pair_rankings(created_at desc);

create index if not exists lix_strategy_performance_lookup_idx
  on public.lix_strategy_performance(strategy, pair);

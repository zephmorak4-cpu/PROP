create table if not exists public.lix_performance_metrics (
  id uuid primary key default gen_random_uuid(),
  pair text not null,
  strategy text not null default 'Asian Liquidity Sweep',
  session text not null default 'london',
  total_trades integer not null default 0,
  wins integer not null default 0,
  losses integer not null default 0,
  win_rate numeric not null default 0,
  average_rr numeric not null default 0,
  average_duration_minutes numeric not null default 0,
  average_stop_size numeric not null default 0,
  average_take_profit_size numeric not null default 0,
  updated_at timestamptz not null default now(),
  unique(pair, strategy, session)
);

create table if not exists public.lix_loss_reviews (
  id uuid primary key default gen_random_uuid(),
  active_trade_id uuid,
  signal_id uuid,
  pair text not null,
  strategy text not null default 'Asian Liquidity Sweep',
  stopped_hunted boolean,
  news_nearby boolean,
  volatility_too_low boolean,
  london_session_weak boolean,
  later_reached_target boolean,
  confidence_justified boolean,
  review_notes text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.lix_market_sessions (
  id uuid primary key default gen_random_uuid(),
  pair text not null,
  session_date date not null,
  asian_high numeric not null,
  asian_low numeric not null,
  london_high numeric,
  london_low numeric,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(pair, session_date)
);

create table if not exists public.lix_pair_statistics (
  id uuid primary key default gen_random_uuid(),
  pair text not null unique,
  best_session text,
  worst_session text,
  average_stop_size numeric not null default 0,
  average_take_profit_size numeric not null default 0,
  average_rr numeric not null default 0,
  updated_at timestamptz not null default now()
);

create index if not exists lix_loss_reviews_pair_created_idx
  on public.lix_loss_reviews(pair, created_at desc);

create index if not exists lix_market_sessions_pair_date_idx
  on public.lix_market_sessions(pair, session_date desc);

-- Chamber sessions extension r1
-- Purpose: persist session tokens for account-backed Chamber auth flows.

create table if not exists chamber_sessions (
  session_token uuid primary key,
  user_id uuid not null references chamber_users(user_id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null
);

create index if not exists idx_chamber_sessions_user_id
  on chamber_sessions (user_id);

create index if not exists idx_chamber_sessions_expires_at
  on chamber_sessions (expires_at);

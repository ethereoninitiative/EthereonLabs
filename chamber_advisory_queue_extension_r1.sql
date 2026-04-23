-- Chamber advisory queue extension r1
-- Purpose: persist advisory acceptance and supervised action queue state.

create table if not exists chamber_advisories (
  advisory_id uuid primary key,
  room_slug text not null,
  created_at timestamptz not null default now(),
  created_by_user_id uuid not null references chamber_users(user_id) on delete cascade,
  created_by_label text not null,
  recommendation_source text not null,
  guidance_strategy text not null,
  confidence_label text not null,
  reasoning_brief text not null,
  recommended_action text not null,
  action_type text not null,
  target_mode text,
  decision text not null default 'pending',
  decision_at timestamptz,
  decision_by_user_id uuid references chamber_users(user_id) on delete set null,
  decision_reason text,
  queue_item_id uuid unique
);

create table if not exists chamber_action_queue (
  queue_item_id uuid primary key,
  room_slug text not null,
  advisory_id uuid not null unique references chamber_advisories(advisory_id) on delete cascade,
  created_at timestamptz not null default now(),
  created_by_user_id uuid not null references chamber_users(user_id) on delete cascade,
  created_by_label text not null,
  requested_action text not null,
  action_type text not null,
  target_mode text,
  queue_status text not null default 'pending',
  claimed_at timestamptz,
  claimed_by_user_id uuid references chamber_users(user_id) on delete set null,
  claimed_by_label text,
  completed_at timestamptz,
  completed_by_user_id uuid references chamber_users(user_id) on delete set null,
  completed_by_label text,
  outcome_summary text
);

create index if not exists idx_chamber_advisories_room_created
  on chamber_advisories (room_slug, created_at);

create index if not exists idx_chamber_action_queue_room_created
  on chamber_action_queue (room_slug, created_at);

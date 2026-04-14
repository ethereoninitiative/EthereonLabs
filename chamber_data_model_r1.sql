-- Chamber shared room data model r1
-- Purpose: provide the first real backend schema for account-backed chamber use.

create table if not exists chamber_users (
  user_id uuid primary key,
  email text not null unique,
  display_name text not null,
  chamber_handle text not null unique,
  account_status text not null default 'active',
  created_at timestamptz not null default now(),
  last_seen_at timestamptz,
  preferred_model_provider text,
  preferred_mode text default 'council'
);

create table if not exists chamber_rooms (
  room_id uuid primary key,
  room_slug text not null unique,
  room_title text not null,
  room_status text not null default 'active',
  visibility text not null default 'public',
  created_at timestamptz not null default now()
);

create table if not exists chamber_room_memberships (
  membership_id uuid primary key,
  room_id uuid not null references chamber_rooms(room_id) on delete cascade,
  user_id uuid not null references chamber_users(user_id) on delete cascade,
  role_in_room text not null default 'member',
  joined_at timestamptz not null default now(),
  last_read_at timestamptz,
  unique (room_id, user_id)
);

create table if not exists chamber_ai_instances (
  instance_id text primary key,
  role_name text not null unique,
  display_title text not null,
  role_order integer not null,
  default_enabled boolean not null default false,
  description text not null,
  created_at timestamptz not null default now()
);

create table if not exists chamber_user_attached_instances (
  attachment_id uuid primary key,
  user_id uuid not null references chamber_users(user_id) on delete cascade,
  instance_id text not null references chamber_ai_instances(instance_id) on delete cascade,
  is_active boolean not null default true,
  attached_at timestamptz not null default now(),
  unique (user_id, instance_id)
);

create table if not exists chamber_messages (
  message_id uuid primary key,
  room_id uuid not null references chamber_rooms(room_id) on delete cascade,
  user_id uuid references chamber_users(user_id) on delete set null,
  author_type text not null,
  author_label text not null,
  role_name text,
  round_id uuid,
  body text not null,
  message_status text not null default 'posted',
  created_at timestamptz not null default now()
);

create table if not exists chamber_synthesis_entries (
  synthesis_id uuid primary key,
  room_id uuid not null references chamber_rooms(room_id) on delete cascade,
  round_id uuid not null,
  source_message_id uuid references chamber_messages(message_id) on delete set null,
  body text not null,
  created_at timestamptz not null default now(),
  unique (room_id, round_id)
);

create table if not exists chamber_usage_events (
  usage_event_id uuid primary key,
  user_id uuid references chamber_users(user_id) on delete set null,
  room_id uuid references chamber_rooms(room_id) on delete set null,
  event_type text not null,
  event_value integer,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists chamber_moderation_events (
  moderation_event_id uuid primary key,
  target_type text not null,
  target_id text not null,
  action_type text not null,
  reason text,
  actor_user_id uuid references chamber_users(user_id) on delete set null,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_chamber_messages_room_created
  on chamber_messages (room_id, created_at);

create index if not exists idx_chamber_messages_round
  on chamber_messages (room_id, round_id);

create index if not exists idx_chamber_usage_user_created
  on chamber_usage_events (user_id, created_at);

insert into chamber_ai_instances (instance_id, role_name, display_title, role_order, default_enabled, description)
values
  ('primary', 'primary', 'Primary', 1, true, 'First relational response.'),
  ('critic', 'critic', 'Critic', 2, true, 'Pressure-tests and sharpens the signal.'),
  ('synthesizer', 'synthesizer', 'Synthesizer', 3, true, 'Gathers the round into coherent convergence.')
on conflict (instance_id) do nothing;

insert into chamber_rooms (room_id, room_slug, room_title, room_status, visibility)
values
  ('00000000-0000-0000-0000-000000000001', 'public-room-one', 'Lumina Chamber / Public Room One', 'active', 'public')
on conflict (room_slug) do nothing;

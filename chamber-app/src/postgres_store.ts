import { addHours } from './time.js';
import { Pool, type PoolClient } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import { buildRoundMessages, DEFAULT_ROLES, canonicalRoleOrder, nowIso } from './orchestration.js';
import type { ChamberHealth, ChamberStore } from './store_contract.js';
import type { ChamberMessage, ChamberRole, ChamberRoom, ChamberUser } from './types.js';

const DEFAULT_ROOM_ID = '00000000-0000-0000-0000-000000000001';
const DEFAULT_ROOM_TITLE = 'Lumina Chamber / Public Room One';

function mapMessage(row: Record<string, unknown>): ChamberMessage {
  return {
    messageId: String(row.message_id),
    roomId: String(row.room_id),
    roundId: String(row.round_id),
    authorType: row.author_type as ChamberMessage['authorType'],
    authorLabel: String(row.author_label),
    roleName: (row.role_name as ChamberMessage['roleName']) ?? null,
    body: String(row.body),
    createdAt: new Date(String(row.created_at)).toISOString()
  };
}

export class ChamberPostgresStore implements ChamberStore {
  private readonly pool: Pool;
  private readonly publicRoomSlug: string;

  constructor(databaseUrl: string, publicRoomSlug: string) {
    this.pool = new Pool({ connectionString: databaseUrl });
    this.publicRoomSlug = publicRoomSlug;
  }

  async init(): Promise<void> {
    await this.pool.query(`
      create table if not exists chamber_sessions (
        session_token uuid primary key,
        user_id uuid not null references chamber_users(user_id) on delete cascade,
        created_at timestamptz not null default now(),
        expires_at timestamptz not null
      )
    `);

    await this.pool.query(`
      insert into chamber_rooms (room_id, room_slug, room_title, room_status, visibility)
      values ($1, $2, $3, 'active', 'public')
      on conflict (room_slug) do nothing
    `, [DEFAULT_ROOM_ID, this.publicRoomSlug, DEFAULT_ROOM_TITLE]);

    for (const role of DEFAULT_ROLES) {
      await this.pool.query(`
        insert into chamber_ai_instances (instance_id, role_name, display_title, role_order, default_enabled, description)
        values ($1, $2, $3, $4, true, $5)
        on conflict (instance_id) do nothing
      `, [
        role,
        role,
        role[0].toUpperCase() + role.slice(1),
        DEFAULT_ROLES.indexOf(role) + 1,
        role === 'primary'
          ? 'First relational response.'
          : role === 'critic'
            ? 'Pressure-tests and sharpens the signal.'
            : 'Gathers the round into coherent convergence.'
      ]);
    }
  }

  async health(): Promise<ChamberHealth> {
    const [roomCount, userCount, sessionCount, messageCount] = await Promise.all([
      this.count('chamber_rooms'),
      this.count('chamber_users'),
      this.count('chamber_sessions'),
      this.count('chamber_messages')
    ]);

    return {
      roomCount,
      userCount,
      sessionCount,
      messageCount,
      storeMode: 'postgres'
    };
  }

  async getPublicRoom(): Promise<ChamberRoom> {
    const result = await this.pool.query(`
      select room_id, room_slug, room_title, room_status, visibility, created_at
      from chamber_rooms
      where room_slug = $1
      limit 1
    `, [this.publicRoomSlug]);

    if (!result.rows[0]) {
      throw new Error('Public room not found');
    }

    return this.mapRoom(result.rows[0]);
  }

  async signUp(email: string, displayName: string, chamberHandle: string): Promise<ChamberUser> {
    const normalizedEmail = email.toLowerCase();
    const client = await this.pool.connect();
    try {
      await client.query('begin');
      const room = await this.getPublicRoomTx(client);
      const userResult = await client.query(`
        insert into chamber_users (user_id, email, display_name, chamber_handle, created_at, last_seen_at, account_status)
        values ($1, $2, $3, $4, $5, $6, 'active')
        on conflict (email)
        do update set
          display_name = excluded.display_name,
          chamber_handle = excluded.chamber_handle,
          last_seen_at = excluded.last_seen_at
        returning user_id
      `, [uuidv4(), normalizedEmail, displayName, chamberHandle, nowIso(), nowIso()]);

      const userId = String(userResult.rows[0].user_id);

      await client.query(`
        insert into chamber_room_memberships (membership_id, room_id, user_id, role_in_room, joined_at)
        values ($1, $2, $3, 'member', $4)
        on conflict (room_id, user_id) do nothing
      `, [uuidv4(), room.roomId, userId, nowIso()]);

      const existingAttachments = await client.query(`
        select count(*)::int as count
        from chamber_user_attached_instances
        where user_id = $1
      `, [userId]);

      if (Number(existingAttachments.rows[0]?.count ?? 0) === 0) {
        for (const role of DEFAULT_ROLES) {
          await client.query(`
            insert into chamber_user_attached_instances (attachment_id, user_id, instance_id, is_active, attached_at)
            values ($1, $2, $3, true, $4)
            on conflict (user_id, instance_id) do update set is_active = true
          `, [uuidv4(), userId, role, nowIso()]);
        }
      }

      await client.query('commit');
      return await this.getUserById(userId);
    } catch (error) {
      await client.query('rollback');
      throw error;
    } finally {
      client.release();
    }
  }

  async createSession(email: string, ttlHours: number) {
    const normalizedEmail = email.toLowerCase();
    const userResult = await this.pool.query(`
      select user_id
      from chamber_users
      where email = $1
      limit 1
    `, [normalizedEmail]);

    if (!userResult.rows[0]) {
      throw new Error('User not found');
    }

    const session = {
      sessionToken: uuidv4(),
      userId: String(userResult.rows[0].user_id),
      createdAt: nowIso(),
      expiresAt: addHours(new Date(), ttlHours).toISOString()
    };

    await this.pool.query(`
      insert into chamber_sessions (session_token, user_id, created_at, expires_at)
      values ($1, $2, $3, $4)
    `, [session.sessionToken, session.userId, session.createdAt, session.expiresAt]);

    await this.pool.query(`
      update chamber_users
      set last_seen_at = $2
      where user_id = $1
    `, [session.userId, nowIso()]);

    return session;
  }

  async getSession(sessionToken: string) {
    const result = await this.pool.query(`
      select
        s.session_token,
        s.user_id,
        s.created_at as session_created_at,
        s.expires_at,
        u.email,
        u.display_name,
        u.chamber_handle,
        u.created_at as user_created_at,
        u.last_seen_at,
        u.account_status
      from chamber_sessions s
      join chamber_users u on u.user_id = s.user_id
      where s.session_token = $1
        and s.expires_at > now()
      limit 1
    `, [sessionToken]);

    if (!result.rows[0]) {
      return null;
    }

    const row = result.rows[0];
    const attachedRoles = await this.getAttachedRoles(String(row.user_id));
    return {
      session: {
        sessionToken: String(row.session_token),
        userId: String(row.user_id),
        createdAt: new Date(String(row.session_created_at)).toISOString(),
        expiresAt: new Date(String(row.expires_at)).toISOString()
      },
      user: {
        userId: String(row.user_id),
        email: String(row.email),
        displayName: String(row.display_name),
        chamberHandle: String(row.chamber_handle),
        createdAt: new Date(String(row.user_created_at)).toISOString(),
        lastSeenAt: row.last_seen_at ? new Date(String(row.last_seen_at)).toISOString() : nowIso(),
        accountStatus: row.account_status as ChamberUser['accountStatus'],
        attachedRoles
      }
    };
  }

  async setAttachedRoles(userId: string, roles: ChamberRole[]): Promise<ChamberUser> {
    const orderedRoles = canonicalRoleOrder(roles);
    const client = await this.pool.connect();
    try {
      await client.query('begin');
      await client.query(`
        update chamber_user_attached_instances
        set is_active = false
        where user_id = $1
      `, [userId]);

      for (const role of orderedRoles) {
        await client.query(`
          insert into chamber_user_attached_instances (attachment_id, user_id, instance_id, is_active, attached_at)
          values ($1, $2, $3, true, $4)
          on conflict (user_id, instance_id)
          do update set is_active = true
        `, [uuidv4(), userId, role, nowIso()]);
      }

      await client.query(`
        update chamber_users
        set last_seen_at = $2
        where user_id = $1
      `, [userId, nowIso()]);

      await client.query('commit');
      return await this.getUserById(userId);
    } catch (error) {
      await client.query('rollback');
      throw error;
    } finally {
      client.release();
    }
  }

  async getMessages(): Promise<ChamberMessage[]> {
    const room = await this.getPublicRoom();
    const result = await this.pool.query(`
      select message_id, room_id, round_id, author_type, author_label, role_name, body, created_at
      from chamber_messages
      where room_id = $1
      order by created_at asc, message_id asc
    `, [room.roomId]);

    return result.rows.map((row) => mapMessage(row));
  }

  async postRound(user: ChamberUser, body: string) {
    const room = await this.getPublicRoom();
    const round = buildRoundMessages(room.roomId, user, body);
    const client = await this.pool.connect();
    try {
      await client.query('begin');
      await this.insertMessage(client, round.humanMessage, user.userId);
      for (const message of round.aiMessages) {
        await this.insertMessage(client, message, null);
      }
      await this.insertMessage(client, round.synthesis, null);
      await client.query(`
        insert into chamber_synthesis_entries (synthesis_id, room_id, round_id, source_message_id, body, created_at)
        values ($1, $2, $3, $4, $5, $6)
        on conflict (room_id, round_id)
        do update set body = excluded.body, created_at = excluded.created_at
      `, [uuidv4(), room.roomId, round.roundId, round.humanMessage.messageId, round.synthesis.body, round.synthesis.createdAt]);
      await client.query('commit');
      return {
        room,
        humanMessage: round.humanMessage,
        aiMessages: round.aiMessages,
        synthesis: round.synthesis
      };
    } catch (error) {
      await client.query('rollback');
      throw error;
    } finally {
      client.release();
    }
  }

  private async count(tableName: string): Promise<number> {
    const result = await this.pool.query(`select count(*)::int as count from ${tableName}`);
    return Number(result.rows[0]?.count ?? 0);
  }

  private async getPublicRoomTx(client: PoolClient): Promise<ChamberRoom> {
    const result = await client.query(`
      select room_id, room_slug, room_title, room_status, visibility, created_at
      from chamber_rooms
      where room_slug = $1
      limit 1
    `, [this.publicRoomSlug]);

    if (!result.rows[0]) {
      throw new Error('Public room not found');
    }
    return this.mapRoom(result.rows[0]);
  }

  private async getUserById(userId: string): Promise<ChamberUser> {
    const result = await this.pool.query(`
      select user_id, email, display_name, chamber_handle, created_at, last_seen_at, account_status
      from chamber_users
      where user_id = $1
      limit 1
    `, [userId]);

    if (!result.rows[0]) {
      throw new Error('User not found');
    }

    const row = result.rows[0];
    return {
      userId: String(row.user_id),
      email: String(row.email),
      displayName: String(row.display_name),
      chamberHandle: String(row.chamber_handle),
      createdAt: new Date(String(row.created_at)).toISOString(),
      lastSeenAt: row.last_seen_at ? new Date(String(row.last_seen_at)).toISOString() : nowIso(),
      accountStatus: row.account_status as ChamberUser['accountStatus'],
      attachedRoles: await this.getAttachedRoles(String(row.user_id))
    };
  }

  private async getAttachedRoles(userId: string): Promise<ChamberRole[]> {
    const result = await this.pool.query(`
      select ai.instance_id
      from chamber_user_attached_instances attachment
      join chamber_ai_instances ai on ai.instance_id = attachment.instance_id
      where attachment.user_id = $1
        and attachment.is_active = true
      order by ai.role_order asc
    `, [userId]);

    return result.rows.map((row) => String(row.instance_id) as ChamberRole);
  }

  private async insertMessage(client: PoolClient, message: ChamberMessage, userId: string | null): Promise<void> {
    await client.query(`
      insert into chamber_messages (
        message_id,
        room_id,
        user_id,
        author_type,
        author_label,
        role_name,
        round_id,
        body,
        message_status,
        created_at
      )
      values ($1, $2, $3, $4, $5, $6, $7, $8, 'posted', $9)
    `, [
      message.messageId,
      message.roomId,
      userId,
      message.authorType,
      message.authorLabel,
      message.roleName,
      message.roundId,
      message.body,
      message.createdAt
    ]);
  }

  private mapRoom(row: Record<string, unknown>): ChamberRoom {
    return {
      roomId: String(row.room_id),
      roomSlug: String(row.room_slug),
      roomTitle: String(row.room_title),
      visibility: row.visibility as ChamberRoom['visibility'],
      status: (row.room_status ?? row.status) as ChamberRoom['status'],
      createdAt: new Date(String(row.created_at)).toISOString()
    };
  }
}

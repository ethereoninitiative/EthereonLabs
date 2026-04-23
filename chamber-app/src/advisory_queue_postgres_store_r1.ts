import { Pool } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import type { ChamberActionQueueItem, ChamberAdvisory } from './advisory_queue_types.js';
import type {
  ChamberAdvisoryQueueStore,
  ClaimQueueItemInput,
  CompleteQueueItemInput,
  CreateAdvisoryInput,
  DecideAdvisoryInput
} from './advisory_queue_store_contract.js';

function nowIso(): string {
  return new Date().toISOString();
}

function mapAdvisory(row: Record<string, unknown>): ChamberAdvisory {
  return {
    advisoryId: String(row.advisory_id),
    roomSlug: String(row.room_slug),
    createdAt: new Date(String(row.created_at)).toISOString(),
    createdByUserId: String(row.created_by_user_id),
    createdByLabel: String(row.created_by_label),
    recommendationSource: row.recommendation_source as ChamberAdvisory['recommendationSource'],
    guidanceStrategy: String(row.guidance_strategy),
    confidenceLabel: row.confidence_label as ChamberAdvisory['confidenceLabel'],
    reasoningBrief: String(row.reasoning_brief),
    recommendedAction: String(row.recommended_action),
    actionType: row.action_type as ChamberAdvisory['actionType'],
    targetMode: row.target_mode ? String(row.target_mode) : null,
    decision: row.decision as ChamberAdvisory['decision'],
    decisionAt: row.decision_at ? new Date(String(row.decision_at)).toISOString() : null,
    decisionByUserId: row.decision_by_user_id ? String(row.decision_by_user_id) : null,
    decisionReason: row.decision_reason ? String(row.decision_reason) : null,
    queueItemId: row.queue_item_id ? String(row.queue_item_id) : null
  };
}

function mapQueueItem(row: Record<string, unknown>): ChamberActionQueueItem {
  return {
    queueItemId: String(row.queue_item_id),
    roomSlug: String(row.room_slug),
    advisoryId: String(row.advisory_id),
    createdAt: new Date(String(row.created_at)).toISOString(),
    createdByUserId: String(row.created_by_user_id),
    createdByLabel: String(row.created_by_label),
    requestedAction: String(row.requested_action),
    actionType: row.action_type as ChamberActionQueueItem['actionType'],
    targetMode: row.target_mode ? String(row.target_mode) : null,
    queueStatus: row.queue_status as ChamberActionQueueItem['queueStatus'],
    claimedAt: row.claimed_at ? new Date(String(row.claimed_at)).toISOString() : null,
    claimedByUserId: row.claimed_by_user_id ? String(row.claimed_by_user_id) : null,
    claimedByLabel: row.claimed_by_label ? String(row.claimed_by_label) : null,
    completedAt: row.completed_at ? new Date(String(row.completed_at)).toISOString() : null,
    completedByUserId: row.completed_by_user_id ? String(row.completed_by_user_id) : null,
    completedByLabel: row.completed_by_label ? String(row.completed_by_label) : null,
    outcomeSummary: row.outcome_summary ? String(row.outcome_summary) : null
  };
}

export class ChamberAdvisoryQueuePostgresStoreR1 implements ChamberAdvisoryQueueStore {
  private readonly pool: Pool;

  constructor(databaseUrl: string) {
    this.pool = new Pool({ connectionString: databaseUrl });
  }

  async init(): Promise<void> {
    await this.pool.query(`
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
      )
    `);

    await this.pool.query(`
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
      )
    `);

    await this.pool.query(`create index if not exists idx_chamber_advisories_room_created on chamber_advisories (room_slug, created_at)`);
    await this.pool.query(`create index if not exists idx_chamber_action_queue_room_created on chamber_action_queue (room_slug, created_at)`);
  }

  async listAdvisories(roomSlug: string): Promise<ChamberAdvisory[]> {
    const result = await this.pool.query(`
      select *
      from chamber_advisories
      where room_slug = $1
      order by created_at asc, advisory_id asc
    `, [roomSlug]);
    return result.rows.map((row) => mapAdvisory(row));
  }

  async listQueue(roomSlug: string): Promise<ChamberActionQueueItem[]> {
    const result = await this.pool.query(`
      select *
      from chamber_action_queue
      where room_slug = $1
      order by created_at asc, queue_item_id asc
    `, [roomSlug]);
    return result.rows.map((row) => mapQueueItem(row));
  }

  async createAdvisory(input: CreateAdvisoryInput): Promise<ChamberAdvisory> {
    const advisoryId = uuidv4();
    const result = await this.pool.query(`
      insert into chamber_advisories (
        advisory_id,
        room_slug,
        created_at,
        created_by_user_id,
        created_by_label,
        recommendation_source,
        guidance_strategy,
        confidence_label,
        reasoning_brief,
        recommended_action,
        action_type,
        target_mode,
        decision
      )
      values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'pending')
      returning *
    `, [
      advisoryId,
      input.roomSlug,
      nowIso(),
      input.createdByUserId,
      input.createdByLabel,
      input.recommendationSource,
      input.guidanceStrategy,
      input.confidenceLabel,
      input.reasoningBrief,
      input.recommendedAction,
      input.actionType,
      input.targetMode
    ]);
    return mapAdvisory(result.rows[0]);
  }

  async decideAdvisory(input: DecideAdvisoryInput): Promise<{ advisory: ChamberAdvisory; queueItem: ChamberActionQueueItem | null }> {
    const client = await this.pool.connect();
    try {
      await client.query('begin');
      const advisoryRow = await client.query(`select * from chamber_advisories where advisory_id = $1 limit 1`, [input.advisoryId]);
      if (!advisoryRow.rows[0]) {
        throw new Error('Advisory not found');
      }
      if (String(advisoryRow.rows[0].decision) !== 'pending') {
        throw new Error('Advisory has already been decided');
      }

      let queueItem: ChamberActionQueueItem | null = null;
      let queueItemId: string | null = null;

      if (input.decision === 'accepted') {
        queueItemId = uuidv4();
        const queueResult = await client.query(`
          insert into chamber_action_queue (
            queue_item_id,
            room_slug,
            advisory_id,
            created_at,
            created_by_user_id,
            created_by_label,
            requested_action,
            action_type,
            target_mode,
            queue_status
          )
          values ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'pending')
          returning *
        `, [
          queueItemId,
          String(advisoryRow.rows[0].room_slug),
          input.advisoryId,
          nowIso(),
          input.decisionByUserId,
          input.decisionByLabel,
          String(advisoryRow.rows[0].recommended_action),
          String(advisoryRow.rows[0].action_type),
          advisoryRow.rows[0].target_mode ? String(advisoryRow.rows[0].target_mode) : null
        ]);
        queueItem = mapQueueItem(queueResult.rows[0]);
      }

      const advisoryResult = await client.query(`
        update chamber_advisories
        set decision = $2,
            decision_at = $3,
            decision_by_user_id = $4,
            decision_reason = $5,
            queue_item_id = $6
        where advisory_id = $1
        returning *
      `, [
        input.advisoryId,
        input.decision,
        nowIso(),
        input.decisionByUserId,
        input.decisionReason,
        queueItemId
      ]);

      await client.query('commit');
      return { advisory: mapAdvisory(advisoryResult.rows[0]), queueItem };
    } catch (error) {
      await client.query('rollback');
      throw error;
    } finally {
      client.release();
    }
  }

  async claimQueueItem(input: ClaimQueueItemInput): Promise<ChamberActionQueueItem> {
    const result = await this.pool.query(`
      update chamber_action_queue
      set queue_status = 'claimed',
          claimed_at = $2,
          claimed_by_user_id = $3,
          claimed_by_label = $4
      where queue_item_id = $1
        and queue_status = 'pending'
      returning *
    `, [input.queueItemId, nowIso(), input.claimedByUserId, input.claimedByLabel]);

    if (!result.rows[0]) {
      throw new Error('Queue item is not pending or was not found');
    }
    return mapQueueItem(result.rows[0]);
  }

  async completeQueueItem(input: CompleteQueueItemInput): Promise<ChamberActionQueueItem> {
    const result = await this.pool.query(`
      update chamber_action_queue
      set queue_status = 'completed',
          completed_at = $2,
          completed_by_user_id = $3,
          completed_by_label = $4,
          outcome_summary = $5
      where queue_item_id = $1
        and queue_status = 'claimed'
      returning *
    `, [input.queueItemId, nowIso(), input.completedByUserId, input.completedByLabel, input.outcomeSummary]);

    if (!result.rows[0]) {
      throw new Error('Queue item must be claimed before completion');
    }
    return mapQueueItem(result.rows[0]);
  }
}

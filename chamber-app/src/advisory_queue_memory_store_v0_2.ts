import { v4 as uuidv4 } from 'uuid';
import type { ChamberActionQueueItem, ChamberAdvisory, AdvisoryDecision } from './advisory_queue_types.js';
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

export class ChamberAdvisoryQueueMemoryStoreV02 implements ChamberAdvisoryQueueStore {
  private readonly advisoriesById = new Map<string, ChamberAdvisory>();
  private readonly roomAdvisoryIds = new Map<string, string[]>();
  private readonly queueItemsById = new Map<string, ChamberActionQueueItem>();
  private readonly roomQueueIds = new Map<string, string[]>();

  async init(): Promise<void> {
    return;
  }

  async listAdvisories(roomSlug: string): Promise<ChamberAdvisory[]> {
    const ids = this.roomAdvisoryIds.get(roomSlug) ?? [];
    return ids
      .map((id) => this.advisoriesById.get(id))
      .filter((value): value is ChamberAdvisory => Boolean(value));
  }

  async listQueue(roomSlug: string): Promise<ChamberActionQueueItem[]> {
    const ids = this.roomQueueIds.get(roomSlug) ?? [];
    return ids
      .map((id) => this.queueItemsById.get(id))
      .filter((value): value is ChamberActionQueueItem => Boolean(value));
  }

  async createAdvisory(input: CreateAdvisoryInput): Promise<ChamberAdvisory> {
    const advisory: ChamberAdvisory = {
      advisoryId: uuidv4(),
      roomSlug: input.roomSlug,
      createdAt: nowIso(),
      createdByUserId: input.createdByUserId,
      createdByLabel: input.createdByLabel,
      recommendationSource: input.recommendationSource,
      guidanceStrategy: input.guidanceStrategy,
      confidenceLabel: input.confidenceLabel,
      reasoningBrief: input.reasoningBrief,
      recommendedAction: input.recommendedAction,
      actionType: input.actionType,
      targetMode: input.targetMode,
      decision: 'pending',
      decisionAt: null,
      decisionByUserId: null,
      decisionReason: null,
      queueItemId: null
    };

    this.advisoriesById.set(advisory.advisoryId, advisory);
    const ids = this.roomAdvisoryIds.get(input.roomSlug) ?? [];
    ids.push(advisory.advisoryId);
    this.roomAdvisoryIds.set(input.roomSlug, ids);
    return advisory;
  }

  async decideAdvisory(input: DecideAdvisoryInput): Promise<{ advisory: ChamberAdvisory; queueItem: ChamberActionQueueItem | null }> {
    const advisory = this.advisoriesById.get(input.advisoryId);
    if (!advisory) {
      throw new Error('Advisory not found');
    }
    if (advisory.decision !== 'pending') {
      throw new Error('Advisory has already been decided');
    }

    advisory.decision = input.decision as Exclude<AdvisoryDecision, 'pending'>;
    advisory.decisionAt = nowIso();
    advisory.decisionByUserId = input.decisionByUserId;
    advisory.decisionReason = input.decisionReason;

    if (input.decision === 'accepted') {
      const queueItem: ChamberActionQueueItem = {
        queueItemId: uuidv4(),
        roomSlug: advisory.roomSlug,
        advisoryId: advisory.advisoryId,
        createdAt: nowIso(),
        createdByUserId: input.decisionByUserId,
        createdByLabel: input.decisionByLabel,
        requestedAction: advisory.recommendedAction,
        actionType: advisory.actionType,
        targetMode: advisory.targetMode,
        queueStatus: 'pending',
        claimedAt: null,
        claimedByUserId: null,
        claimedByLabel: null,
        completedAt: null,
        completedByUserId: null,
        completedByLabel: null,
        outcomeSummary: null
      };

      advisory.queueItemId = queueItem.queueItemId;
      this.queueItemsById.set(queueItem.queueItemId, queueItem);
      const queueIds = this.roomQueueIds.get(advisory.roomSlug) ?? [];
      queueIds.push(queueItem.queueItemId);
      this.roomQueueIds.set(advisory.roomSlug, queueIds);
      return { advisory, queueItem };
    }

    return { advisory, queueItem: null };
  }

  async claimQueueItem(input: ClaimQueueItemInput): Promise<ChamberActionQueueItem> {
    const queueItem = this.queueItemsById.get(input.queueItemId);
    if (!queueItem) {
      throw new Error('Queue item not found');
    }
    if (queueItem.queueStatus !== 'pending') {
      throw new Error('Queue item is not pending');
    }

    queueItem.queueStatus = 'claimed';
    queueItem.claimedAt = nowIso();
    queueItem.claimedByUserId = input.claimedByUserId;
    queueItem.claimedByLabel = input.claimedByLabel;
    return queueItem;
  }

  async completeQueueItem(input: CompleteQueueItemInput): Promise<ChamberActionQueueItem> {
    const queueItem = this.queueItemsById.get(input.queueItemId);
    if (!queueItem) {
      throw new Error('Queue item not found');
    }
    if (queueItem.queueStatus !== 'claimed') {
      throw new Error('Queue item must be claimed before completion');
    }

    queueItem.queueStatus = 'completed';
    queueItem.completedAt = nowIso();
    queueItem.completedByUserId = input.completedByUserId;
    queueItem.completedByLabel = input.completedByLabel;
    queueItem.outcomeSummary = input.outcomeSummary;
    return queueItem;
  }
}

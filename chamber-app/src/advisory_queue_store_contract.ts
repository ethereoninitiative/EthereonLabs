import type { ChamberActionQueueItem, ChamberAdvisory, AdvisoryDecision } from './advisory_queue_types.js';

export interface CreateAdvisoryInput {
  roomSlug: string;
  createdByUserId: string;
  createdByLabel: string;
  recommendationSource: 'human' | 'system';
  guidanceStrategy: string;
  confidenceLabel: 'low' | 'medium' | 'high';
  reasoningBrief: string;
  recommendedAction: string;
  actionType: 'transition' | 'mutation' | 'promotion' | 'audit';
  targetMode: string | null;
}

export interface DecideAdvisoryInput {
  advisoryId: string;
  decision: Exclude<AdvisoryDecision, 'pending'>;
  decisionByUserId: string;
  decisionByLabel: string;
  decisionReason: string | null;
}

export interface ClaimQueueItemInput {
  queueItemId: string;
  claimedByUserId: string;
  claimedByLabel: string;
}

export interface CompleteQueueItemInput {
  queueItemId: string;
  completedByUserId: string;
  completedByLabel: string;
  outcomeSummary: string | null;
}

export interface ChamberAdvisoryQueueStore {
  init(): Promise<void>;
  listAdvisories(roomSlug: string): Promise<ChamberAdvisory[]>;
  listQueue(roomSlug: string): Promise<ChamberActionQueueItem[]>;
  createAdvisory(input: CreateAdvisoryInput): Promise<ChamberAdvisory>;
  decideAdvisory(input: DecideAdvisoryInput): Promise<{ advisory: ChamberAdvisory; queueItem: ChamberActionQueueItem | null }>;
  claimQueueItem(input: ClaimQueueItemInput): Promise<ChamberActionQueueItem>;
  completeQueueItem(input: CompleteQueueItemInput): Promise<ChamberActionQueueItem>;
}

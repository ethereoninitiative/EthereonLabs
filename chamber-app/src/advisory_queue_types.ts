export type AdvisoryDecision = 'pending' | 'accepted' | 'rejected';
export type ActionQueueStatus = 'pending' | 'claimed' | 'completed' | 'cancelled';

export interface ChamberAdvisory {
  advisoryId: string;
  roomSlug: string;
  createdAt: string;
  createdByUserId: string;
  createdByLabel: string;
  recommendationSource: 'human' | 'system';
  guidanceStrategy: string;
  confidenceLabel: 'low' | 'medium' | 'high';
  reasoningBrief: string;
  recommendedAction: string;
  actionType: 'transition' | 'mutation' | 'promotion' | 'audit';
  targetMode: string | null;
  decision: AdvisoryDecision;
  decisionAt: string | null;
  decisionByUserId: string | null;
  decisionReason: string | null;
  queueItemId: string | null;
}

export interface ChamberActionQueueItem {
  queueItemId: string;
  roomSlug: string;
  advisoryId: string;
  createdAt: string;
  createdByUserId: string;
  createdByLabel: string;
  requestedAction: string;
  actionType: 'transition' | 'mutation' | 'promotion' | 'audit';
  targetMode: string | null;
  queueStatus: ActionQueueStatus;
  claimedAt: string | null;
  claimedByUserId: string | null;
  claimedByLabel: string | null;
  completedAt: string | null;
  completedByUserId: string | null;
  completedByLabel: string | null;
  outcomeSummary: string | null;
}

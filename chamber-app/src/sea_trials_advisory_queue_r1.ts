import { ChamberAdvisoryQueueMemoryStore } from './advisory_queue_memory_store.js';

function main() {
  const store = new ChamberAdvisoryQueueMemoryStore();
  const roomSlug = 'public-room-one';

  const accepted = store.createAdvisory({
    roomSlug,
    createdByUserId: 'user-1',
    createdByLabel: 'architect',
    recommendationSource: 'system',
    guidanceStrategy: 'pending_next_action_history_aligned',
    confidenceLabel: 'high',
    reasoningBrief: 'Recent continuity signals align on the same next move.',
    recommendedAction: 'continue::lumina_orchestration_stack',
    actionType: 'audit',
    targetMode: 'Observation'
  });

  const rejected = store.createAdvisory({
    roomSlug,
    createdByUserId: 'user-2',
    createdByLabel: 'keeper',
    recommendationSource: 'human',
    guidanceStrategy: 'manual_override',
    confidenceLabel: 'medium',
    reasoningBrief: 'This recommendation should be refused for now.',
    recommendedAction: 'enter_drydock',
    actionType: 'transition',
    targetMode: 'DryDock'
  });

  const acceptedDecision = store.decideAdvisory({
    advisoryId: accepted.advisoryId,
    decision: 'accepted',
    decisionByUserId: 'user-1',
    decisionByLabel: 'architect',
    decisionReason: 'Recommendation matches the present heading.'
  });

  const rejectedDecision = store.decideAdvisory({
    advisoryId: rejected.advisoryId,
    decision: 'rejected',
    decisionByUserId: 'user-2',
    decisionByLabel: 'keeper',
    decisionReason: 'Hold this move outside the current lane.'
  });

  const claimed = store.claimQueueItem({
    queueItemId: acceptedDecision.queueItem!.queueItemId,
    claimedByUserId: 'user-3',
    claimedByLabel: 'operator'
  });

  const completed = store.completeQueueItem({
    queueItemId: claimed.queueItemId,
    completedByUserId: 'user-3',
    completedByLabel: 'operator',
    outcomeSummary: 'Advisory was reviewed and marked complete under supervision.'
  });

  const queue = store.listQueue(roomSlug);
  const advisories = store.listAdvisories(roomSlug);

  const checks = {
    accepted_advisory_creates_queue_item: acceptedDecision.queueItem !== null,
    rejected_advisory_does_not_create_queue_item: rejectedDecision.queueItem === null,
    queue_item_can_be_claimed: claimed.queueStatus === 'claimed',
    queue_item_can_be_completed_after_claim: completed.queueStatus === 'completed',
    room_retains_two_advisories: advisories.length === 2,
    room_retains_one_queue_item: queue.length === 1
  };

  return {
    suite: 'Chamber Advisory Queue Sea Trial r1',
    passed: Object.values(checks).every(Boolean),
    checks,
    advisories,
    queue
  };
}

console.log(JSON.stringify(main(), null, 2));

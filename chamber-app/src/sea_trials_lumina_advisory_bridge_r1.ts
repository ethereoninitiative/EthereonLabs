import { mapLuminaAdvisorySummaryToChamberPayload } from './lumina_advisory_bridge_r1.js';

function main() {
  const payload = mapLuminaAdvisorySummaryToChamberPayload({
    project_id: 'lumina-core',
    guidance_strategy: 'pending_next_action_history_aligned',
    recommended_next_action: 'stabilize_to_observation',
    confidence_label: 'very_high',
    reasoning_brief: 'Project return and checkpoint history reinforce the same recommendation.'
  });

  const checks = {
    recommendation_source_is_system: payload.recommendationSource === 'system',
    confidence_is_normalized_to_high: payload.confidenceLabel === 'high',
    target_mode_is_inferred: payload.targetMode === 'Observation',
    transition_action_is_inferred: payload.actionType === 'transition',
    project_id_is_preserved_in_reasoning: payload.reasoningBrief.startsWith('[lumina-core]')
  };

  return {
    suite: 'Lumina Advisory Bridge Sea Trial r1',
    passed: Object.values(checks).every(Boolean),
    checks,
    payload
  };
}

console.log(JSON.stringify(main(), null, 2));

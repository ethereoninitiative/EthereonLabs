export interface LuminaAdvisorySummaryInput {
  project_id: string;
  guidance_strategy: string;
  recommended_next_action: string;
  confidence_label: 'low_medium' | 'medium' | 'medium_high' | 'high' | 'very_high';
  reasoning_brief: string;
}

export interface ChamberAdvisoryCreatePayload {
  recommendationSource: 'system';
  guidanceStrategy: string;
  confidenceLabel: 'low' | 'medium' | 'high';
  reasoningBrief: string;
  recommendedAction: string;
  actionType: 'transition' | 'mutation' | 'promotion' | 'audit';
  targetMode: string | null;
}

function normalizeConfidence(label: LuminaAdvisorySummaryInput['confidence_label']): 'low' | 'medium' | 'high' {
  if (label === 'high' || label === 'very_high') {
    return 'high';
  }
  if (label === 'medium' || label === 'medium_high') {
    return 'medium';
  }
  return 'low';
}

function inferActionType(recommendedAction: string): 'transition' | 'mutation' | 'promotion' | 'audit' {
  const lowered = recommendedAction.toLowerCase();
  if (lowered.includes('promot')) {
    return 'promotion';
  }
  if (lowered.includes('stabilize') || lowered.includes('enter_') || lowered.includes('enter::')) {
    return 'transition';
  }
  if (lowered.includes('mutat')) {
    return 'mutation';
  }
  return 'audit';
}

function inferTargetMode(recommendedAction: string): string | null {
  const lowered = recommendedAction.toLowerCase();
  if (lowered.includes('observation')) {
    return 'Observation';
  }
  if (lowered.includes('drydock')) {
    return 'DryDock';
  }
  if (lowered.includes('canon')) {
    return 'Canon';
  }
  if (lowered.includes('sandbox')) {
    return 'Sandbox';
  }
  return null;
}

export function mapLuminaAdvisorySummaryToChamberPayload(input: LuminaAdvisorySummaryInput): ChamberAdvisoryCreatePayload {
  return {
    recommendationSource: 'system',
    guidanceStrategy: input.guidance_strategy,
    confidenceLabel: normalizeConfidence(input.confidence_label),
    reasoningBrief: `[${input.project_id}] ${input.reasoning_brief}`,
    recommendedAction: input.recommended_next_action,
    actionType: inferActionType(input.recommended_next_action),
    targetMode: inferTargetMode(input.recommended_next_action)
  };
}

import { v4 as uuidv4 } from 'uuid';
import type { ChamberMessage, ChamberRole, ChamberUser } from './types.js';

export const DEFAULT_ROLES: ChamberRole[] = ['primary', 'critic', 'synthesizer'];

export function nowIso(): string {
  return new Date().toISOString();
}

export function canonicalRoleOrder(roles: ChamberRole[]): ChamberRole[] {
  return DEFAULT_ROLES.filter((role) => roles.includes(role));
}

export function roleResponse(role: ChamberRole, text: string): string {
  const lowered = text.toLowerCase();
  const topic = lowered.includes('site') || lowered.includes('website')
    ? 'website'
    : lowered.includes('room') || lowered.includes('social') || lowered.includes('community')
      ? 'social'
      : lowered.includes('bot') || lowered.includes('ai') || lowered.includes('instance')
        ? 'ai'
        : 'general';

  const responses: Record<ChamberRole, Record<string, string>> = {
    primary: {
      website: 'The chamber should make the website feel inhabited: not a brochure, but a place people can enter and return to.',
      social: 'A room becomes social when identity, memory, and visible turn-taking hold together under repeated use.',
      ai: 'The first strong form of multibot is governed plurality: clear roles in one room before provider sprawl.',
      general: 'The next coherent move is to make the room shared, persistent, and trustworthy.'
    },
    critic: {
      website: 'If the chamber is only atmospheric, people will bounce. It needs real shared state and authentic return behavior.',
      social: 'Without moderation, quotas, and identity, free social space becomes drift and noise.',
      ai: 'If the roles do not feel distinct, the multibot layer will read as theater rather than signal.',
      general: 'The weak point is always false depth. The structure has to support the feeling.'
    },
    synthesizer: {
      website: 'The site is moving from description to embodiment. The room is becoming the proof.',
      social: 'The chamber pattern is clear: returning identity, bounded plurality, and synthesis after divergence.',
      ai: 'Council-mode orchestration is the clean bridge from one-model role-play to true multibot later.',
      general: 'The round converges on the same need: make the chamber shared, durable, and governable.'
    }
  };

  return responses[role][topic];
}

export function synthesisResponse(text: string): string {
  const lowered = text.toLowerCase();
  if (lowered.includes('site') || lowered.includes('website')) {
    return 'The room is pushing the website toward embodiment: a public threshold-space rather than a static explanation.';
  }
  if (lowered.includes('room') || lowered.includes('social') || lowered.includes('community')) {
    return 'The gathered signal is social in a real sense: returnable identity, shared memory, bounded plurality, and readable synthesis.';
  }
  if (lowered.includes('bot') || lowered.includes('ai') || lowered.includes('instance')) {
    return 'The room points toward true multibot later, but today it needs governed plurality and persistence more than provider diversity.';
  }
  return 'The chamber converges on a simple truth: it must feel inhabited, shared, and stable enough to return to.';
}

export function buildRoundMessages(roomId: string, user: ChamberUser, body: string) {
  const roundId = uuidv4();
  const createdAt = nowIso();

  const humanMessage: ChamberMessage = {
    messageId: uuidv4(),
    roomId,
    roundId,
    authorType: 'human',
    authorLabel: user.chamberHandle,
    roleName: null,
    body,
    createdAt
  };

  const aiMessages: ChamberMessage[] = canonicalRoleOrder(user.attachedRoles).map((role) => ({
    messageId: uuidv4(),
    roomId,
    roundId,
    authorType: 'ai',
    authorLabel: role[0].toUpperCase() + role.slice(1),
    roleName: role,
    body: roleResponse(role, body),
    createdAt: nowIso()
  }));

  const synthesis: ChamberMessage = {
    messageId: uuidv4(),
    roomId,
    roundId,
    authorType: 'synthesis',
    authorLabel: 'Synthesis',
    roleName: 'synthesis',
    body: synthesisResponse(body),
    createdAt: nowIso()
  };

  return { roundId, humanMessage, aiMessages, synthesis };
}

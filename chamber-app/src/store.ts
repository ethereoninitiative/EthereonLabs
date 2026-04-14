import { addHours } from './time.js';
import { v4 as uuidv4 } from 'uuid';
import type { ChamberMessage, ChamberRole, ChamberRoom, ChamberRoundPayload, ChamberSession, ChamberUser } from './types.js';

const DEFAULT_ROLES: ChamberRole[] = ['primary', 'critic', 'synthesizer'];

function nowIso(): string {
  return new Date().toISOString();
}

function roleResponse(role: ChamberRole, text: string): string {
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

function synthesisResponse(text: string): string {
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

export class ChamberMemoryStore {
  private readonly publicRoom: ChamberRoom;
  private readonly usersByEmail = new Map<string, ChamberUser>();
  private readonly usersById = new Map<string, ChamberUser>();
  private readonly sessions = new Map<string, ChamberSession>();
  private readonly roomMessages = new Map<string, ChamberMessage[]>();

  constructor(publicRoomSlug: string) {
    this.publicRoom = {
      roomId: '00000000-0000-0000-0000-000000000001',
      roomSlug: publicRoomSlug,
      roomTitle: 'Lumina Chamber / Public Room One',
      visibility: 'public',
      status: 'active',
      createdAt: nowIso()
    };

    this.roomMessages.set(this.publicRoom.roomId, []);
  }

  health() {
    return {
      roomCount: 1,
      userCount: this.usersById.size,
      sessionCount: this.sessions.size,
      messageCount: this.roomMessages.get(this.publicRoom.roomId)?.length ?? 0
    };
  }

  getPublicRoom(): ChamberRoom {
    return this.publicRoom;
  }

  signUp(email: string, displayName: string, chamberHandle: string): ChamberUser {
    const existing = this.usersByEmail.get(email.toLowerCase());
    if (existing) {
      existing.displayName = displayName;
      existing.chamberHandle = chamberHandle;
      existing.lastSeenAt = nowIso();
      return existing;
    }

    const user: ChamberUser = {
      userId: uuidv4(),
      email: email.toLowerCase(),
      displayName,
      chamberHandle,
      createdAt: nowIso(),
      lastSeenAt: nowIso(),
      accountStatus: 'active',
      attachedRoles: [...DEFAULT_ROLES]
    };

    this.usersByEmail.set(user.email, user);
    this.usersById.set(user.userId, user);
    return user;
  }

  createSession(email: string, ttlHours: number): ChamberSession {
    const user = this.usersByEmail.get(email.toLowerCase());
    if (!user) {
      throw new Error('User not found');
    }

    user.lastSeenAt = nowIso();
    const session: ChamberSession = {
      sessionToken: uuidv4(),
      userId: user.userId,
      createdAt: nowIso(),
      expiresAt: addHours(new Date(), ttlHours).toISOString()
    };
    this.sessions.set(session.sessionToken, session);
    return session;
  }

  getSession(sessionToken: string): { session: ChamberSession; user: ChamberUser } | null {
    const session = this.sessions.get(sessionToken);
    if (!session) return null;
    if (new Date(session.expiresAt).getTime() < Date.now()) {
      this.sessions.delete(sessionToken);
      return null;
    }

    const user = this.usersById.get(session.userId);
    if (!user) return null;
    return { session, user };
  }

  setAttachedRoles(userId: string, roles: ChamberRole[]): ChamberUser {
    const user = this.usersById.get(userId);
    if (!user) {
      throw new Error('User not found');
    }
    user.attachedRoles = [...roles];
    user.lastSeenAt = nowIso();
    return user;
  }

  getMessages(): ChamberMessage[] {
    return [...(this.roomMessages.get(this.publicRoom.roomId) ?? [])];
  }

  postRound(user: ChamberUser, body: string): ChamberRoundPayload {
    const roundId = uuidv4();
    const createdAt = nowIso();
    const messages = this.roomMessages.get(this.publicRoom.roomId) ?? [];

    const humanMessage: ChamberMessage = {
      messageId: uuidv4(),
      roomId: this.publicRoom.roomId,
      roundId,
      authorType: 'human',
      authorLabel: user.chamberHandle,
      roleName: null,
      body,
      createdAt
    };

    const aiMessages = user.attachedRoles.map((role) => ({
      messageId: uuidv4(),
      roomId: this.publicRoom.roomId,
      roundId,
      authorType: 'ai' as const,
      authorLabel: role[0].toUpperCase() + role.slice(1),
      roleName: role,
      body: roleResponse(role, body),
      createdAt: nowIso()
    }));

    const synthesis: ChamberMessage = {
      messageId: uuidv4(),
      roomId: this.publicRoom.roomId,
      roundId,
      authorType: 'synthesis',
      authorLabel: 'Synthesis',
      roleName: 'synthesis',
      body: synthesisResponse(body),
      createdAt: nowIso()
    };

    messages.push(humanMessage, ...aiMessages, synthesis);
    this.roomMessages.set(this.publicRoom.roomId, messages);

    return {
      room: this.publicRoom,
      humanMessage,
      aiMessages,
      synthesis
    };
  }
}

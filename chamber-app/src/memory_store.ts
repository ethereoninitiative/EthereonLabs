import { addHours } from './time.js';
import { v4 as uuidv4 } from 'uuid';
import { buildRoundMessages, DEFAULT_ROLES, nowIso } from './orchestration.js';
import type { ChamberHealth, ChamberStore } from './store_contract.js';
import type { ChamberMessage, ChamberRole, ChamberRoom, ChamberSession, ChamberUser } from './types.js';

export class ChamberMemoryStore implements ChamberStore {
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
  }

  async init(): Promise<void> {
    this.roomMessages.set(this.publicRoom.roomId, this.roomMessages.get(this.publicRoom.roomId) ?? []);
  }

  async health(): Promise<ChamberHealth> {
    return {
      roomCount: 1,
      userCount: this.usersById.size,
      sessionCount: this.sessions.size,
      messageCount: this.roomMessages.get(this.publicRoom.roomId)?.length ?? 0,
      storeMode: 'memory'
    };
  }

  async getPublicRoom(): Promise<ChamberRoom> {
    return this.publicRoom;
  }

  async signUp(email: string, displayName: string, chamberHandle: string): Promise<ChamberUser> {
    const normalizedEmail = email.toLowerCase();
    const existing = this.usersByEmail.get(normalizedEmail);
    if (existing) {
      existing.displayName = displayName;
      existing.chamberHandle = chamberHandle;
      existing.lastSeenAt = nowIso();
      return existing;
    }

    const user: ChamberUser = {
      userId: uuidv4(),
      email: normalizedEmail,
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

  async createSession(email: string, ttlHours: number): Promise<ChamberSession> {
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

  async getSession(sessionToken: string) {
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

  async setAttachedRoles(userId: string, roles: ChamberRole[]): Promise<ChamberUser> {
    const user = this.usersById.get(userId);
    if (!user) {
      throw new Error('User not found');
    }

    user.attachedRoles = [...roles];
    user.lastSeenAt = nowIso();
    return user;
  }

  async getMessages(): Promise<ChamberMessage[]> {
    return [...(this.roomMessages.get(this.publicRoom.roomId) ?? [])];
  }

  async postRound(user: ChamberUser, body: string) {
    const messages = this.roomMessages.get(this.publicRoom.roomId) ?? [];
    const round = buildRoundMessages(this.publicRoom.roomId, user, body);
    messages.push(round.humanMessage, ...round.aiMessages, round.synthesis);
    this.roomMessages.set(this.publicRoom.roomId, messages);
    return {
      room: this.publicRoom,
      humanMessage: round.humanMessage,
      aiMessages: round.aiMessages,
      synthesis: round.synthesis
    };
  }
}

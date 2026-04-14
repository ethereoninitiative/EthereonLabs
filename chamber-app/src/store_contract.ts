import type { ChamberMessage, ChamberRole, ChamberRoom, ChamberRoundPayload, ChamberSession, ChamberUser } from './types.js';

export interface ChamberHealth {
  roomCount: number;
  userCount: number;
  sessionCount: number;
  messageCount: number;
  storeMode: 'memory' | 'postgres';
}

export interface ChamberActor {
  session: ChamberSession;
  user: ChamberUser;
}

export interface ChamberStore {
  init(): Promise<void>;
  health(): Promise<ChamberHealth>;
  getPublicRoom(): Promise<ChamberRoom>;
  signUp(email: string, displayName: string, chamberHandle: string): Promise<ChamberUser>;
  createSession(email: string, ttlHours: number): Promise<ChamberSession>;
  getSession(sessionToken: string): Promise<ChamberActor | null>;
  setAttachedRoles(userId: string, roles: ChamberRole[]): Promise<ChamberUser>;
  getMessages(): Promise<ChamberMessage[]>;
  postRound(user: ChamberUser, body: string): Promise<ChamberRoundPayload>;
}

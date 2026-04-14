export type ChamberRole = 'primary' | 'critic' | 'synthesizer';

export interface ChamberUser {
  userId: string;
  email: string;
  displayName: string;
  chamberHandle: string;
  createdAt: string;
  lastSeenAt: string;
  accountStatus: 'active' | 'muted' | 'suspended';
  attachedRoles: ChamberRole[];
}

export interface ChamberSession {
  sessionToken: string;
  userId: string;
  createdAt: string;
  expiresAt: string;
}

export interface ChamberRoom {
  roomId: string;
  roomSlug: string;
  roomTitle: string;
  visibility: 'public';
  status: 'active';
  createdAt: string;
}

export interface ChamberMessage {
  messageId: string;
  roomId: string;
  roundId: string;
  authorType: 'human' | 'ai' | 'synthesis';
  authorLabel: string;
  roleName: ChamberRole | 'synthesis' | null;
  body: string;
  createdAt: string;
}

export interface ChamberRoundPayload {
  room: ChamberRoom;
  humanMessage: ChamberMessage;
  aiMessages: ChamberMessage[];
  synthesis: ChamberMessage;
}

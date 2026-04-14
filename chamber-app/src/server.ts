import 'dotenv/config';
import cors from 'cors';
import express from 'express';
import { z } from 'zod';
import { ChamberMemoryStore } from './store.js';
import type { ChamberRole } from './types.js';

const port = Number(process.env.PORT || 8787);
const origin = process.env.CHAMBER_APP_ORIGIN || `http://localhost:${port}`;
const publicRoomSlug = process.env.CHAMBER_PUBLIC_ROOM_SLUG || 'public-room-one';
const sessionTtlHours = Number(process.env.SESSION_TTL_HOURS || 168);

const store = new ChamberMemoryStore(publicRoomSlug);
const app = express();

app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

const signUpSchema = z.object({
  email: z.string().email(),
  displayName: z.string().min(1).max(64),
  chamberHandle: z.string().min(1).max(24)
});

const loginSchema = z.object({
  email: z.string().email()
});

const roleArraySchema = z.object({
  roles: z.array(z.enum(['primary', 'critic', 'synthesizer'])).max(3)
});

const postSchema = z.object({
  sessionToken: z.string().uuid(),
  body: z.string().min(1).max(4000)
});

function roleOrder(roles: ChamberRole[]): ChamberRole[] {
  const canonical: ChamberRole[] = ['primary', 'critic', 'synthesizer'];
  return canonical.filter((role) => roles.includes(role));
}

function getActor(sessionToken: string) {
  const actor = store.getSession(sessionToken);
  if (!actor) {
    return null;
  }
  return actor;
}

app.get('/health', (_req, res) => {
  res.json({
    ok: true,
    service: 'chamber-app-scaffold',
    origin,
    publicRoomSlug,
    health: store.health()
  });
});

app.post('/api/auth/signup', (req, res) => {
  const parsed = signUpSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ ok: false, error: parsed.error.flatten() });
  }

  const user = store.signUp(parsed.data.email, parsed.data.displayName, parsed.data.chamberHandle);
  const session = store.createSession(user.email, sessionTtlHours);
  return res.status(201).json({ ok: true, user, session });
});

app.post('/api/auth/login', (req, res) => {
  const parsed = loginSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ ok: false, error: parsed.error.flatten() });
  }

  try {
    const session = store.createSession(parsed.data.email, sessionTtlHours);
    const actor = getActor(session.sessionToken);
    return res.json({ ok: true, user: actor?.user, session });
  } catch (error) {
    return res.status(404).json({ ok: false, error: error instanceof Error ? error.message : 'Login failed' });
  }
});

app.get('/api/auth/session/:sessionToken', (req, res) => {
  const actor = getActor(req.params.sessionToken);
  if (!actor) {
    return res.status(404).json({ ok: false, error: 'Session not found' });
  }

  return res.json({ ok: true, user: actor.user, session: actor.session });
});

app.patch('/api/auth/session/:sessionToken/roles', (req, res) => {
  const actor = getActor(req.params.sessionToken);
  if (!actor) {
    return res.status(404).json({ ok: false, error: 'Session not found' });
  }

  const parsed = roleArraySchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ ok: false, error: parsed.error.flatten() });
  }

  const user = store.setAttachedRoles(actor.user.userId, roleOrder(parsed.data.roles));
  return res.json({ ok: true, user });
});

app.get('/api/rooms/public-room-one', (_req, res) => {
  res.json({ ok: true, room: store.getPublicRoom() });
});

app.get('/api/rooms/public-room-one/messages', (_req, res) => {
  res.json({ ok: true, room: store.getPublicRoom(), messages: store.getMessages() });
});

app.post('/api/rooms/public-room-one/messages', (req, res) => {
  const parsed = postSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ ok: false, error: parsed.error.flatten() });
  }

  const actor = getActor(parsed.data.sessionToken);
  if (!actor) {
    return res.status(404).json({ ok: false, error: 'Session not found' });
  }

  const round = store.postRound(actor.user, parsed.data.body);
  return res.status(201).json({ ok: true, round });
});

app.listen(port, () => {
  console.log(`chamber-app-scaffold listening on ${port}`);
});

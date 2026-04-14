import 'dotenv/config';
import cors from 'cors';
import express from 'express';
import { z } from 'zod';
import { createChamberStore } from './store_factory.js';
import type { ChamberRole } from './types.js';

const port = Number(process.env.PORT || 8787);
const publicRoomSlug = process.env.CHAMBER_PUBLIC_ROOM_SLUG || 'public-room-one';
const sessionTtlHours = Number(process.env.SESSION_TTL_HOURS || 168);
const storeMode = (process.env.CHAMBER_STORE_MODE || 'memory') as 'memory' | 'postgres';
const databaseUrl = process.env.DATABASE_URL;
const allowedOrigins = (process.env.CHAMBER_ALLOWED_ORIGINS || '')
  .split(',')
  .map((value) => value.trim())
  .filter(Boolean);

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

function roomPath(suffix = ''): string {
  return `/api/rooms/${publicRoomSlug}${suffix}`;
}

async function main() {
  const store = await createChamberStore({
    storeMode,
    publicRoomSlug,
    databaseUrl
  });

  const app = express();

  app.use(cors({
    origin(origin, callback) {
      if (!origin || allowedOrigins.length === 0 || allowedOrigins.includes(origin)) {
        callback(null, true);
        return;
      }
      callback(new Error('Origin not allowed by Chamber scaffold CORS policy'));
    },
    credentials: true
  }));
  app.use(express.json());

  app.get('/health', async (_req, res) => {
    res.json({
      ok: true,
      service: 'chamber-app-scaffold',
      publicRoomSlug,
      allowedOrigins,
      health: await store.health()
    });
  });

  app.post('/api/auth/signup', async (req, res) => {
    const parsed = signUpSchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ ok: false, error: parsed.error.flatten() });
    }

    const user = await store.signUp(parsed.data.email, parsed.data.displayName, parsed.data.chamberHandle);
    const session = await store.createSession(user.email, sessionTtlHours);
    return res.status(201).json({ ok: true, user, session });
  });

  app.post('/api/auth/login', async (req, res) => {
    const parsed = loginSchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ ok: false, error: parsed.error.flatten() });
    }

    try {
      const session = await store.createSession(parsed.data.email, sessionTtlHours);
      const actor = await store.getSession(session.sessionToken);
      return res.json({ ok: true, user: actor?.user, session });
    } catch (error) {
      return res.status(404).json({ ok: false, error: error instanceof Error ? error.message : 'Login failed' });
    }
  });

  app.get('/api/auth/session/:sessionToken', async (req, res) => {
    const actor = await store.getSession(req.params.sessionToken);
    if (!actor) {
      return res.status(404).json({ ok: false, error: 'Session not found' });
    }

    return res.json({ ok: true, user: actor.user, session: actor.session });
  });

  app.patch('/api/auth/session/:sessionToken/roles', async (req, res) => {
    const actor = await store.getSession(req.params.sessionToken);
    if (!actor) {
      return res.status(404).json({ ok: false, error: 'Session not found' });
    }

    const parsed = roleArraySchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ ok: false, error: parsed.error.flatten() });
    }

    const user = await store.setAttachedRoles(actor.user.userId, roleOrder(parsed.data.roles));
    return res.json({ ok: true, user });
  });

  app.get(roomPath(), async (_req, res) => {
    res.json({ ok: true, room: await store.getPublicRoom() });
  });

  app.get(roomPath('/messages'), async (_req, res) => {
    res.json({ ok: true, room: await store.getPublicRoom(), messages: await store.getMessages() });
  });

  app.post(roomPath('/messages'), async (req, res) => {
    const parsed = postSchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ ok: false, error: parsed.error.flatten() });
    }

    const actor = await store.getSession(parsed.data.sessionToken);
    if (!actor) {
      return res.status(404).json({ ok: false, error: 'Session not found' });
    }

    const round = await store.postRound(actor.user, parsed.data.body);
    return res.status(201).json({ ok: true, round });
  });

  app.listen(port, () => {
    console.log(`chamber-app-scaffold listening on ${port} using ${storeMode} store mode`);
  });
}

main().catch((error) => {
  console.error('Failed to start chamber-app-scaffold', error);
});

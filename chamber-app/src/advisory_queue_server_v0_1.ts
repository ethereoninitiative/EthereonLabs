import 'dotenv/config';
import cors from 'cors';
import express from 'express';
import { z } from 'zod';
import { createChamberStore } from './store_factory.js';
import { ChamberAdvisoryQueueMemoryStore } from './advisory_queue_memory_store.js';

const port = Number(process.env.CHAMBER_ADVISORY_PORT || 8788);
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

const createAdvisorySchema = z.object({
  sessionToken: z.string().uuid(),
  recommendationSource: z.enum(['human', 'system']).default('human'),
  guidanceStrategy: z.string().min(1).max(120),
  confidenceLabel: z.enum(['low', 'medium', 'high']),
  reasoningBrief: z.string().min(1).max(500),
  recommendedAction: z.string().min(1).max(200),
  actionType: z.enum(['transition', 'mutation', 'promotion', 'audit']),
  targetMode: z.string().min(1).max(64).nullable().optional()
});

const decideAdvisorySchema = z.object({
  sessionToken: z.string().uuid(),
  decision: z.enum(['accepted', 'rejected']),
  decisionReason: z.string().min(1).max(500).nullable().optional()
});

const claimQueueSchema = z.object({
  sessionToken: z.string().uuid()
});

const completeQueueSchema = z.object({
  sessionToken: z.string().uuid(),
  outcomeSummary: z.string().min(1).max(1000).nullable().optional()
});

function requirePublicRoom(roomSlug: string) {
  if (roomSlug !== publicRoomSlug) {
    throw new Error('Only the configured public Chamber room is supported in this scaffold');
  }
}

async function main() {
  const store = await createChamberStore({
    storeMode,
    publicRoomSlug,
    databaseUrl
  });
  const advisoryStore = new ChamberAdvisoryQueueMemoryStore();

  const app = express();
  app.use(cors({
    origin(origin, callback) {
      if (!origin || allowedOrigins.length === 0 || allowedOrigins.includes(origin)) {
        callback(null, true);
        return;
      }
      callback(new Error('Origin not allowed by Chamber advisory scaffold CORS policy'));
    },
    credentials: true
  }));
  app.use(express.json());

  app.get('/health', async (_req, res) => {
    res.json({
      ok: true,
      service: 'chamber-advisory-queue-scaffold',
      publicRoomSlug,
      allowedOrigins,
      health: await store.health(),
      advisoryCount: advisoryStore.listAdvisories(publicRoomSlug).length,
      queueCount: advisoryStore.listQueue(publicRoomSlug).length
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

  app.get('/api/rooms/:roomSlug/advisories', async (req, res) => {
    try {
      requirePublicRoom(req.params.roomSlug);
      return res.json({
        ok: true,
        room: await store.getPublicRoom(),
        advisories: advisoryStore.listAdvisories(req.params.roomSlug)
      });
    } catch (error) {
      return res.status(404).json({ ok: false, error: error instanceof Error ? error.message : 'Room not found' });
    }
  });

  app.post('/api/rooms/:roomSlug/advisories', async (req, res) => {
    try {
      requirePublicRoom(req.params.roomSlug);
      const parsed = createAdvisorySchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ ok: false, error: parsed.error.flatten() });
      }

      const actor = await store.getSession(parsed.data.sessionToken);
      if (!actor) {
        return res.status(404).json({ ok: false, error: 'Session not found' });
      }

      const advisory = advisoryStore.createAdvisory({
        roomSlug: req.params.roomSlug,
        createdByUserId: actor.user.userId,
        createdByLabel: actor.user.chamberHandle,
        recommendationSource: parsed.data.recommendationSource,
        guidanceStrategy: parsed.data.guidanceStrategy,
        confidenceLabel: parsed.data.confidenceLabel,
        reasoningBrief: parsed.data.reasoningBrief,
        recommendedAction: parsed.data.recommendedAction,
        actionType: parsed.data.actionType,
        targetMode: parsed.data.targetMode ?? null
      });

      return res.status(201).json({ ok: true, advisory });
    } catch (error) {
      return res.status(404).json({ ok: false, error: error instanceof Error ? error.message : 'Unable to create advisory' });
    }
  });

  app.post('/api/rooms/:roomSlug/advisories/:advisoryId/decision', async (req, res) => {
    try {
      requirePublicRoom(req.params.roomSlug);
      const parsed = decideAdvisorySchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ ok: false, error: parsed.error.flatten() });
      }

      const actor = await store.getSession(parsed.data.sessionToken);
      if (!actor) {
        return res.status(404).json({ ok: false, error: 'Session not found' });
      }

      const result = advisoryStore.decideAdvisory({
        advisoryId: req.params.advisoryId,
        decision: parsed.data.decision,
        decisionByUserId: actor.user.userId,
        decisionByLabel: actor.user.chamberHandle,
        decisionReason: parsed.data.decisionReason ?? null
      });

      return res.json({ ok: true, advisory: result.advisory, queueItem: result.queueItem });
    } catch (error) {
      return res.status(400).json({ ok: false, error: error instanceof Error ? error.message : 'Unable to decide advisory' });
    }
  });

  app.get('/api/rooms/:roomSlug/action-queue', async (req, res) => {
    try {
      requirePublicRoom(req.params.roomSlug);
      return res.json({
        ok: true,
        room: await store.getPublicRoom(),
        queue: advisoryStore.listQueue(req.params.roomSlug)
      });
    } catch (error) {
      return res.status(404).json({ ok: false, error: error instanceof Error ? error.message : 'Room not found' });
    }
  });

  app.post('/api/rooms/:roomSlug/action-queue/:queueItemId/claim', async (req, res) => {
    try {
      requirePublicRoom(req.params.roomSlug);
      const parsed = claimQueueSchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ ok: false, error: parsed.error.flatten() });
      }

      const actor = await store.getSession(parsed.data.sessionToken);
      if (!actor) {
        return res.status(404).json({ ok: false, error: 'Session not found' });
      }

      const queueItem = advisoryStore.claimQueueItem({
        queueItemId: req.params.queueItemId,
        claimedByUserId: actor.user.userId,
        claimedByLabel: actor.user.chamberHandle
      });

      return res.json({ ok: true, queueItem });
    } catch (error) {
      return res.status(400).json({ ok: false, error: error instanceof Error ? error.message : 'Unable to claim queue item' });
    }
  });

  app.post('/api/rooms/:roomSlug/action-queue/:queueItemId/complete', async (req, res) => {
    try {
      requirePublicRoom(req.params.roomSlug);
      const parsed = completeQueueSchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ ok: false, error: parsed.error.flatten() });
      }

      const actor = await store.getSession(parsed.data.sessionToken);
      if (!actor) {
        return res.status(404).json({ ok: false, error: 'Session not found' });
      }

      const queueItem = advisoryStore.completeQueueItem({
        queueItemId: req.params.queueItemId,
        completedByUserId: actor.user.userId,
        completedByLabel: actor.user.chamberHandle,
        outcomeSummary: parsed.data.outcomeSummary ?? null
      });

      return res.json({ ok: true, queueItem });
    } catch (error) {
      return res.status(400).json({ ok: false, error: error instanceof Error ? error.message : 'Unable to complete queue item' });
    }
  });

  app.listen(port, () => {
    console.log(`chamber-advisory-queue-scaffold listening on ${port} using ${storeMode} chamber identity store`);
  });
}

main().catch((error) => {
  console.error('Failed to start chamber-advisory-queue-scaffold', error);
});

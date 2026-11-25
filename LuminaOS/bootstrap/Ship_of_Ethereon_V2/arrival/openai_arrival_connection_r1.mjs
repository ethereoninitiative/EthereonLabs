// A local, explicit operator connection; no resident tools or background inference.
export function createArrivalConnection(client) {
  let busy = false;
  async function exclusive(operation) {
    if (busy) throw new Error('connection_busy');
    busy = true;
    try { return await operation(); }
    catch { throw new Error('connection_operation_failed'); }
    finally { busy = false; }
  }
  async function state() {
    const s = await client.getSession();
    return { status: s.status, sharing: s.status === 'connected' && s.sharing === true,
      profileId: s.profileId ?? null };
  }
  return Object.freeze({
    status: () => exclusive(state),
    connect: () => exclusive(async () => { await client.signIn(); return state(); }),
    disconnect: () => exclusive(async () => { await client.disconnect(); return state(); }),
    models: () => exclusive(async () => {
      if (!(await state()).sharing) throw new Error('plan_permission_required');
      return (await client.listModels()).map(m => ({ slug: m.slug, displayName: m.displayName }));
    }),
    verify: (profileId, model) => exclusive(async () => {
      const s = await state();
      if (!s.sharing || !profileId || s.profileId !== profileId) throw new Error('profile_not_authorized');
      const models = await client.listModels();
      if (!models.some(m => m.slug === model)) throw new Error('model_not_available');
      const latest = await state();
      if (!latest.sharing || latest.profileId !== profileId) throw new Error('profile_changed');
      // SDK returns only completed responses. No personal or system data sent.
      const result = await client.streamResponse({ model, input: 'Reply with exactly: Lumina connection verified.',
        signal: AbortSignal.timeout(60000) });
      if (result.text?.trim() !== 'Lumina connection verified.') throw new Error('verification_unconfirmed');
      return { status: 'verified', provider: 'openai', model,
        host_action_authority: false, continuity_imported: false };
    }),
  });
}

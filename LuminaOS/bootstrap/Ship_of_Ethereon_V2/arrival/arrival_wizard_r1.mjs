// Provider-neutral onboarding state machine. No credentials, persistence or network.
export function createArrivalWizard(connection) {
  let busy = false;
  let session = { status: 'disconnected', sharing: false, profileId: null };
  let models = [], selected = null, verified = null;
  const snapshot = () => structuredClone({ busy, session, models, selected, verified });
  const reset = () => { models = []; selected = null; verified = null; };
  const adopt = s => {
    const next = { status: s.status, sharing: s.status === 'connected' && s.sharing === true,
      profileId: typeof s.profileId === 'string' ? s.profileId : null };
    if (!next.sharing || !next.profileId || next.profileId !== session.profileId) reset();
    session = next;
  };
  async function run(action) {
    if (busy) throw new Error('busy');
    busy = true;
    try { await action(); }
    catch { reset(); throw new Error('arrival_step_failed'); }
    finally { busy = false; }
    return snapshot();
  }
  return Object.freeze({
    snapshot,
    refresh: () => run(async () => adopt(await connection.status())),
    connect: () => run(async () => { reset(); adopt(await connection.connect()); }),
    disconnect: () => run(async () => { reset(); adopt(await connection.disconnect()); }),
    discover: () => run(async () => {
      reset(); adopt(await connection.status());
      if (!session.sharing || !session.profileId) throw new Error('not_authorized');
      const profile = session.profileId;
      const found = await connection.models();
      adopt(await connection.status());
      if (!session.sharing || session.profileId !== profile) throw new Error('account_changed');
      if (!Array.isArray(found) || found.some(m => typeof m.slug !== 'string' || !m.slug || typeof m.displayName !== 'string')) throw new Error('invalid_models');
      models = found.map(({slug, displayName}) => ({slug, displayName}));
    }),
    choose: model => {
      if (busy || !models.some(m => m.slug === model)) throw new Error('invalid_selection');
      selected = model; verified = null; return snapshot();
    },
    verify: confirmed => run(async () => {
      verified = null;
      if (confirmed !== true || !selected) throw new Error('explicit_consent_required');
      const profile = session.profileId, model = selected;
      adopt(await connection.status());
      if (!session.sharing || session.profileId !== profile || selected !== model) throw new Error('account_changed');
      const receipt = await connection.verify(profile, model);
      adopt(await connection.status());
      if (!session.sharing || session.profileId !== profile || selected !== model || receipt.status !== 'verified' || receipt.model !== model || receipt.host_action_authority !== false || receipt.continuity_imported !== false) throw new Error('unverified');
      verified = { profileId: profile, model, provider: receipt.provider, continuityImported: false, hostActionAuthority: false };
    }),
  });
}

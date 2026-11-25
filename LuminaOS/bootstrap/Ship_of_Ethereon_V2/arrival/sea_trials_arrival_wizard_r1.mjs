import assert from 'node:assert/strict';
import { createArrivalWizard } from './arrival_wizard_r1.mjs';
let state = {status:'disconnected', sharing:false, profileId:null};
let calls = 0, switchDuringVerify = false;
const connection = {
  status: async () => state,
  connect: async () => (state = {status:'connected', sharing:false, profileId:'A'}),
  disconnect: async () => (state = {status:'disconnected', sharing:false, profileId:null}),
  models: async () => [{slug:'m',displayName:'Model',credential:'secret'}],
  verify: async (profileId, model) => {
    calls++; assert.equal(profileId,'A'); assert.equal(model,'m');
    if (switchDuringVerify) state = {...state,profileId:'B'};
    return {status:'verified', provider:'openai', model, host_action_authority:false, continuity_imported:false};
  },
};
const w = createArrivalWizard(connection);
await assert.rejects(w.discover());
await w.connect();
await assert.rejects(w.discover());
state.sharing = true;
await w.discover();
assert.deepEqual(w.snapshot().models,[{slug:'m',displayName:'Model'}]);
assert.throws(() => w.choose('not-offered'));
w.choose('m');
await assert.rejects(w.verify(false));
assert.equal(calls,0);
await w.discover(); w.choose('m');
await w.verify(true);
assert.equal(w.snapshot().verified.model,'m');
assert.equal(w.snapshot().verified.hostActionAuthority,false);
state.profileId = 'B'; await w.refresh();
assert.equal(w.snapshot().verified,null); assert.equal(w.snapshot().selected,null);
state.profileId = 'A'; await w.discover(); w.choose('m');
switchDuringVerify = true; await assert.rejects(w.verify(true));
assert.equal(w.snapshot().verified,null);
await w.disconnect(); assert.equal(w.snapshot().session.status,'disconnected');
assert.equal(w.snapshot().verified,null); assert.equal(calls,2);
console.log('Arrival wizard fixture passed: consent, account binding, model selection, verification invalidation and disconnect.');

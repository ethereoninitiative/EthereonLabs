import assert from 'node:assert/strict';
import { createArrivalConnection } from './openai_arrival_connection_r1.mjs';
let session = { status: 'disconnected', sharing: false, profileId: 'fixture', token: 'secret' };
let calls = 0;
let answer = 'Lumina connection verified.';
const sdk = {
  getSession: async () => session,
  signIn: async () => { session = { ...session, status: 'connected' }; },
  disconnect: async () => { session = { ...session, status: 'disconnected', sharing: false }; },
  listModels: async () => [{ slug: 'fixture-model', displayName: 'Fixture', token: 'secret' }],
  streamResponse: async options => { calls++; assert.equal(options.input, 'Reply with exactly: Lumina connection verified.'); return { text: answer }; },
};
const adapter = createArrivalConnection(sdk);
assert.deepEqual(await adapter.status(), { status: 'disconnected', sharing: false, profileId: 'fixture' });
await assert.rejects(adapter.verify('fixture','fixture-model'));
assert.equal((await adapter.connect()).sharing, false);
await assert.rejects(adapter.models());
session.sharing = true;
assert.deepEqual(await adapter.models(), [{slug:'fixture-model',displayName:'Fixture'}]);
await assert.rejects(adapter.verify('wrong','fixture-model'));
await assert.rejects(adapter.verify('fixture','wrong'));
assert.equal(calls, 0);
assert.equal((await adapter.verify('fixture','fixture-model')).status,'verified');
answer = 'incomplete';
await assert.rejects(adapter.verify('fixture','fixture-model'));
assert.equal((await adapter.disconnect()).sharing,false);
await assert.rejects(adapter.verify('fixture','fixture-model'));
assert.equal(calls,2);
console.log('Arrival adapter fixture checks passed; live sign-in and inference not tested.');

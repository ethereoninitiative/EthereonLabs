import type { ChamberAdvisoryQueueStore } from './advisory_queue_store_contract.js';
import { ChamberAdvisoryQueueMemoryStoreV02 } from './advisory_queue_memory_store_v0_2.js';
import { ChamberAdvisoryQueuePostgresStoreR1 } from './advisory_queue_postgres_store_r1.js';

export interface AdvisoryQueueStoreFactoryOptions {
  storeMode: 'memory' | 'postgres';
  databaseUrl?: string;
}

export async function createAdvisoryQueueStoreR1(options: AdvisoryQueueStoreFactoryOptions): Promise<ChamberAdvisoryQueueStore> {
  const store = options.storeMode === 'postgres'
    ? createPostgresStore(options)
    : new ChamberAdvisoryQueueMemoryStoreV02();

  await store.init();
  return store;
}

function createPostgresStore(options: AdvisoryQueueStoreFactoryOptions): ChamberAdvisoryQueueStore {
  if (!options.databaseUrl) {
    throw new Error('DATABASE_URL is required when CHAMBER_STORE_MODE=postgres for advisory queue persistence');
  }

  return new ChamberAdvisoryQueuePostgresStoreR1(options.databaseUrl);
}

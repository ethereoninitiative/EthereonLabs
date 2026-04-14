import { ChamberMemoryStore } from './memory_store.js';
import { ChamberPostgresStore } from './postgres_store.js';
import type { ChamberStore } from './store_contract.js';

export interface ChamberStoreFactoryOptions {
  storeMode: 'memory' | 'postgres';
  publicRoomSlug: string;
  databaseUrl?: string;
}

export async function createChamberStore(options: ChamberStoreFactoryOptions): Promise<ChamberStore> {
  const store = options.storeMode === 'postgres'
    ? createPostgresStore(options)
    : new ChamberMemoryStore(options.publicRoomSlug);

  await store.init();
  return store;
}

function createPostgresStore(options: ChamberStoreFactoryOptions): ChamberStore {
  if (!options.databaseUrl) {
    throw new Error('DATABASE_URL is required when CHAMBER_STORE_MODE=postgres');
  }

  return new ChamberPostgresStore(options.databaseUrl, options.publicRoomSlug);
}

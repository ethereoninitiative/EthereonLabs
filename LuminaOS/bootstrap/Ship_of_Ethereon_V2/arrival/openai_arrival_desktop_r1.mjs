// Main-process integration for a reviewed local Electron application.
import { join } from 'node:path';
import { createArrivalConnection } from './openai_arrival_connection_r1.mjs';

export async function createDesktopArrival({ app, safeStorage, shell, createChatGPT }) {
  await app.whenReady();
  const usable = () => safeStorage.isEncryptionAvailable() &&
    (process.platform !== 'linux' ||
      (typeof safeStorage.getSelectedStorageBackend === 'function' &&
       ['gnome_libsecret', 'kwallet', 'kwallet5', 'kwallet6'].includes(safeStorage.getSelectedStorageBackend())));
  if (!usable()) throw new Error('protected_credential_storage_unavailable');
  const requireStorage = () => { if (!usable()) throw new Error('protected_credential_storage_unavailable'); };
  const client = createChatGPT({
    appName: 'Lumina OS',
    appId: 'lumina-os',
    redirectPort: 0,
    sendHostId: true,
    storageDir: join(app.getPath('userData'), 'chatgpt'),
    credentialEncryption: {
      id: 'lumina-electron-safe-storage-r1',
      isAvailable: usable,
      encrypt: value => { requireStorage(); return safeStorage.encryptString(value); },
      decrypt: value => { requireStorage(); return safeStorage.decryptString(Buffer.from(value)); },
    },
    openBrowser: async value => {
      const url = new URL(value);
      if (url.origin !== 'https://auth.openai.com' || url.username || url.password ||
          url.pathname !== '/api/accounts/authorize') throw new Error('unexpected_authorization_destination');
      await shell.openExternal(url.href);
    },
  });
  return createArrivalConnection(client);
}

(() => {
  const STORAGE_KEYS = {
    identity: 'ethereonlabs-chamber-identity',
    sessionToken: 'ethereonlabs-chamber-session-token',
    apiBase: 'ethereonlabs-chamber-api-base',
    instances: 'ethereonlabs-chamber-instances',
    thread: 'ethereonlabs-chamber-thread',
    synthesis: 'ethereonlabs-chamber-synthesis'
  };

  const PUBLIC_ROOM_SLUG = 'public-room-one';
  const DEFAULT_INSTANCE_ORDER = ['primary', 'critic', 'synthesizer'];

  const instanceDefs = [
    {
      id: 'primary',
      title: 'Primary',
      summary: 'First relational response. Holds the main thread with the human.',
      activeByDefault: true
    },
    {
      id: 'critic',
      title: 'Critic',
      summary: 'Sharpens, tests, and exposes the weak point or missing edge.',
      activeByDefault: true
    },
    {
      id: 'synthesizer',
      title: 'Synthesizer',
      summary: 'Gathers the voices and states the next coherent move.',
      activeByDefault: true
    }
  ];

  const seedThread = [
    {
      id: 'seed-human',
      kind: 'human',
      author: 'Visitor',
      title: 'Human post',
      text: 'What does a public chamber for harmonic intelligence feel like when it first becomes real?',
      createdAt: new Date().toISOString()
    },
    {
      id: 'seed-primary',
      kind: 'ai-primary',
      author: 'Primary',
      title: 'Primary / first response',
      text: 'It feels like entering a room that already has coherence. Not just a prompt box, but a place with memory, structure, and presence.',
      createdAt: new Date().toISOString()
    },
    {
      id: 'seed-critic',
      kind: 'ai-critic',
      author: 'Critic',
      title: 'Critic / pressure test',
      text: 'Only if the room can survive real use. The chamber must be more than atmosphere; it has to hold identity, limits, and visible order.',
      createdAt: new Date().toISOString()
    },
    {
      id: 'seed-synth',
      kind: 'ai-synthesizer',
      author: 'Synthesizer',
      title: 'Synthesizer / gathered signal',
      text: 'A real chamber begins when social energy and governed structure appear together.',
      createdAt: new Date().toISOString()
    }
  ];

  const defaultSynthesis = 'This chamber shell demonstrates the intended interaction pattern: human post, role-bound plurality, then synthesis.';

  const identityForm = document.getElementById('identityForm');
  const identityEmail = document.getElementById('identityEmail');
  const identityHandle = document.getElementById('identityHandle');
  const identityState = document.getElementById('identityState');
  const identityClear = document.getElementById('identityClear');
  const rosterRoot = document.getElementById('instanceRoster');
  const threadRoot = document.getElementById('threadRoot');
  const synthesisRoot = document.getElementById('synthesisRoot');
  const composerForm = document.getElementById('composerForm');
  const composerInput = document.getElementById('composerInput');
  const resetThread = document.getElementById('resetThread');
  const modePill = document.getElementById('chamberModePill');
  const pulsePill = document.getElementById('chamberPulsePill');

  let identity = loadIdentity();
  let sessionToken = localStorage.getItem(STORAGE_KEYS.sessionToken) || '';
  let activeInstances = loadInstances();
  let thread = loadThread();
  let synthesis = loadSynthesis();
  let backend = { available: false, base: '', mode: 'local specimen' };

  function loadIdentity() {
    const raw = localStorage.getItem(STORAGE_KEYS.identity);
    if (!raw) return { email: '', handle: '' };
    try {
      return JSON.parse(raw);
    } catch {
      return { email: '', handle: '' };
    }
  }

  function saveIdentity() {
    localStorage.setItem(STORAGE_KEYS.identity, JSON.stringify(identity));
  }

  function loadInstances() {
    const raw = localStorage.getItem(STORAGE_KEYS.instances);
    if (!raw) return instanceDefs.filter((item) => item.activeByDefault).map((item) => item.id);
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) && parsed.length ? parsed : instanceDefs.filter((item) => item.activeByDefault).map((item) => item.id);
    } catch {
      return instanceDefs.filter((item) => item.activeByDefault).map((item) => item.id);
    }
  }

  function saveInstances() {
    localStorage.setItem(STORAGE_KEYS.instances, JSON.stringify(activeInstances));
  }

  function loadThread() {
    const raw = localStorage.getItem(STORAGE_KEYS.thread);
    if (!raw) return seedThread;
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) && parsed.length ? parsed : seedThread;
    } catch {
      return seedThread;
    }
  }

  function saveThread() {
    localStorage.setItem(STORAGE_KEYS.thread, JSON.stringify(thread.slice(-50)));
  }

  function loadSynthesis() {
    const raw = localStorage.getItem(STORAGE_KEYS.synthesis);
    return raw || defaultSynthesis;
  }

  function saveSynthesis() {
    localStorage.setItem(STORAGE_KEYS.synthesis, synthesis);
  }

  function nowLabel(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }

  function escapeHtml(text) {
    return text
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function canonicalRoleOrder(roles) {
    return DEFAULT_INSTANCE_ORDER.filter((role) => roles.includes(role));
  }

  function renderIdentity() {
    identityEmail.value = identity.email || '';
    identityHandle.value = identity.handle || '';

    if (identity.handle || identity.email) {
      const mode = backend.available ? 'connected' : 'local';
      identityState.innerHTML = `<strong>${escapeHtml(identity.handle || 'Visitor')}</strong><br>${escapeHtml(identity.email || 'local chamber shell identity active')}<br><small>${escapeHtml(mode)} mode</small>`;
    } else {
      identityState.textContent = backend.available
        ? 'No session active yet. Enter a handle and email to join the shared room.'
        : 'No chamber identity stored yet. Enter a handle to anchor your presence in this shell.';
    }
  }

  function renderRoster() {
    rosterRoot.innerHTML = '';
    instanceDefs.forEach((instance) => {
      const active = activeInstances.includes(instance.id);
      const card = document.createElement('article');
      card.className = `instance-card${active ? ' is-active' : ''}`;
      card.innerHTML = `
        <header>
          <h3>${instance.title}</h3>
          <button type="button">${active ? 'Attached' : 'Attach'}</button>
        </header>
        <p>${instance.summary}</p>
        <small>${active ? 'Will join the next round.' : 'Inactive for the next round.'}</small>
      `;
      card.querySelector('button').addEventListener('click', () => toggleInstance(instance.id));
      rosterRoot.appendChild(card);
    });
  }

  function renderThread() {
    threadRoot.innerHTML = '';
    thread.forEach((entry) => {
      const node = document.createElement('article');
      node.className = `thread-entry is-${entry.kind}`;
      node.innerHTML = `
        <header>
          <h3>${escapeHtml(entry.title)}</h3>
          <time>${nowLabel(entry.createdAt)}</time>
        </header>
        <p><strong>${escapeHtml(entry.author)}:</strong> ${escapeHtml(entry.text)}</p>
      `;
      threadRoot.appendChild(node);
    });
  }

  function renderSynthesis() {
    synthesisRoot.innerHTML = `<strong>Current synthesis</strong><p>${escapeHtml(synthesis)}</p>`;
  }

  function updatePulse() {
    const count = activeInstances.length;
    const handle = identity.handle || 'Visitor';
    modePill.textContent = count > 1 ? 'Mode: Council' : count === 1 ? 'Mode: Focused dialogue' : 'Mode: Human-only';
    const source = backend.available ? 'shared room' : 'local specimen';
    pulsePill.textContent = `Pulse: ${handle} with ${count} attached ${count === 1 ? 'instance' : 'instances'} / ${source}`;
  }

  function inferTopic(message) {
    const text = message.toLowerCase();
    if (text.includes('website') || text.includes('site')) return 'website';
    if (text.includes('build') || text.includes('ship') || text.includes('make')) return 'build';
    if (text.includes('social') || text.includes('people') || text.includes('community')) return 'social';
    if (text.includes('ai') || text.includes('instance') || text.includes('bot')) return 'ai';
    return 'general';
  }

  function roleResponse(roleId, message) {
    const topic = inferTopic(message);
    const map = {
      primary: {
        website: 'The strongest move is to let the site become a threshold-space instead of only a brochure. The chamber should feel like a place people can enter, not just read about.',
        build: 'The next believable move is to make the first layer tangible and socially legible. A chamber shell gives the project somewhere visible to stand.',
        social: 'Social energy comes from returnable identity, visible presence, and a room that feels inhabited even between posts.',
        ai: 'The user does not need provider-diverse multibot first. They need distinct, role-bound intelligences that feel coherent in one room.',
        general: 'The chamber should translate the project into a room with identity, flow, and visible coherence.'
      },
      critic: {
        website: 'If the chamber is only aesthetic, it will collapse into a novelty panel. The room has to show actual turn order, identity, and synthesis.',
        build: 'Do not pretend the whole host exists yet. The shell must stay honest about what is local, what is governed, and what still needs backend infrastructure.',
        social: 'Free social use without caps or moderation becomes noise and cost drift. The room must remain governable.',
        ai: 'Three generic voices are not enough. The roles must feel visibly different or the plurality reads as theater.',
        general: 'The weak point is always fake depth. The chamber has to earn the feeling of presence through structure.'
      },
      synthesizer: {
        website: 'The site can now begin to perform the project, not merely describe it.',
        build: 'The practical next move is clear: add real auth, shared persistence, and provider-backed orchestration behind this shell.',
        social: 'A returnable human identity plus bounded AI plurality is the heart of the chamber pattern.',
        ai: 'Governed roles first, true multibot routing later, is the clean expansion path.',
        general: 'The chamber becomes believable when human identity, bounded plurality, and synthesis appear together.'
      }
    };
    return map[roleId][topic];
  }

  function synthesisResponse(message, handle) {
    const topic = inferTopic(message);
    if (topic === 'website') return `${handle || 'The visitor'} is pushing the website toward embodiment: chamber as living threshold rather than static description.`;
    if (topic === 'build') return `The room is pointing toward the next build layer: real auth, shared room persistence, and orchestration behind the shell.`;
    if (topic === 'social') return `The gathered signal is social in a real sense: returnable identity, bounded plurality, and coherence under use.`;
    if (topic === 'ai') return `The chamber's current logic favors governed plurality over swarm behavior. That is the stable bridge to true multibot later.`;
    return `The round converges on the same core: make the chamber feel inhabited, governed, and returnable.`;
  }

  function localPostRound(message) {
    const handle = identity.handle || 'Visitor';
    const entries = [{
      id: crypto.randomUUID(),
      kind: 'human',
      author: handle,
      title: 'Human post',
      text: message,
      createdAt: new Date().toISOString()
    }];

    canonicalRoleOrder(activeInstances).forEach((instanceId) => {
      const instance = instanceDefs.find((item) => item.id === instanceId);
      entries.push({
        id: crypto.randomUUID(),
        kind: `ai-${instanceId}`,
        author: instance.title,
        title: `${instance.title} / chamber response`,
        text: roleResponse(instanceId, message),
        createdAt: new Date().toISOString()
      });
    });

    thread = [...thread, ...entries].slice(-50);
    synthesis = synthesisResponse(message, handle);
    saveThread();
    saveSynthesis();
    renderThread();
    renderSynthesis();
  }

  function normalizeMessage(message) {
    let kind = 'human';
    let title = 'Human post';
    if (message.authorType === 'ai' && message.roleName) {
      kind = `ai-${message.roleName}`;
      title = `${message.authorLabel} / chamber response`;
    }
    if (message.authorType === 'synthesis') {
      kind = 'ai-synthesizer';
      title = 'Synthesis / gathered signal';
    }

    return {
      id: message.messageId,
      kind,
      author: message.authorLabel,
      title,
      text: message.body,
      createdAt: message.createdAt
    };
  }

  async function detectBackend() {
    const candidateSet = new Set();
    const saved = localStorage.getItem(STORAGE_KEYS.apiBase);
    if (saved) candidateSet.add(saved);
    if (window.CHAMBER_API_BASE) candidateSet.add(window.CHAMBER_API_BASE);
    if (window.location.origin && window.location.origin.startsWith('http')) {
      candidateSet.add(window.location.origin);
    }
    candidateSet.add('http://localhost:8787');

    for (const candidate of candidateSet) {
      const base = candidate.replace(/\/$/, '');
      try {
        const response = await fetch(`${base}/health`, { headers: { Accept: 'application/json' } });
        if (!response.ok) continue;
        const payload = await response.json();
        if (payload?.service === 'chamber-app-scaffold' && payload?.ok) {
          localStorage.setItem(STORAGE_KEYS.apiBase, base);
          return { available: true, base, mode: 'shared room' };
        }
      } catch (_error) {
      }
    }

    return { available: false, base: '', mode: 'local specimen' };
  }

  async function fetchJson(path, options = {}) {
    if (!backend.available || !backend.base) {
      throw new Error('Backend unavailable');
    }

    const response = await fetch(`${backend.base}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(options.headers || {})
      },
      ...options
    });

    const payload = await response.json().catch(() => ({ ok: false, error: 'Invalid JSON response' }));
    if (!response.ok || payload?.ok === false) {
      throw new Error(payload?.error || `Request failed with status ${response.status}`);
    }
    return payload;
  }

  async function hydrateSession() {
    if (!backend.available || !sessionToken) return false;
    try {
      const payload = await fetchJson(`/api/auth/session/${sessionToken}`);
      identity = {
        email: payload.user.email,
        handle: payload.user.chamberHandle
      };
      activeInstances = canonicalRoleOrder(payload.user.attachedRoles || DEFAULT_INSTANCE_ORDER);
      saveIdentity();
      saveInstances();
      renderIdentity();
      renderRoster();
      updatePulse();
      return true;
    } catch (_error) {
      sessionToken = '';
      localStorage.removeItem(STORAGE_KEYS.sessionToken);
      return false;
    }
  }

  async function loadBackendMessages() {
    if (!backend.available) return false;
    try {
      const payload = await fetchJson(`/api/rooms/${PUBLIC_ROOM_SLUG}/messages`);
      thread = (payload.messages || []).map(normalizeMessage);
      if (!thread.length) {
        thread = seedThread;
      }
      const latestSynthesis = [...(payload.messages || [])].reverse().find((message) => message.authorType === 'synthesis');
      synthesis = latestSynthesis?.body || defaultSynthesis;
      saveThread();
      saveSynthesis();
      renderThread();
      renderSynthesis();
      return true;
    } catch (_error) {
      return false;
    }
  }

  async function toggleInstance(instanceId) {
    const active = activeInstances.includes(instanceId);
    let nextRoles;
    if (active) {
      nextRoles = activeInstances.filter((item) => item !== instanceId);
    } else {
      if (activeInstances.length >= 3) return;
      nextRoles = canonicalRoleOrder([...activeInstances, instanceId]);
    }

    if (backend.available && sessionToken) {
      try {
        const payload = await fetchJson(`/api/auth/session/${sessionToken}/roles`, {
          method: 'PATCH',
          body: JSON.stringify({ roles: nextRoles })
        });
        activeInstances = canonicalRoleOrder(payload.user.attachedRoles || nextRoles);
      } catch (_error) {
        return;
      }
    } else {
      activeInstances = nextRoles;
    }

    saveInstances();
    renderRoster();
    updatePulse();
  }

  identityForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    identity = {
      email: identityEmail.value.trim(),
      handle: identityHandle.value.trim()
    };

    if (!identity.email || !identity.handle) {
      renderIdentity();
      return;
    }

    if (backend.available) {
      try {
        const payload = await fetchJson('/api/auth/signup', {
          method: 'POST',
          body: JSON.stringify({
            email: identity.email,
            displayName: identity.handle,
            chamberHandle: identity.handle
          })
        });
        sessionToken = payload.session.sessionToken;
        localStorage.setItem(STORAGE_KEYS.sessionToken, sessionToken);
        activeInstances = canonicalRoleOrder(payload.user.attachedRoles || DEFAULT_INSTANCE_ORDER);
        await loadBackendMessages();
      } catch (error) {
        identityState.textContent = error instanceof Error ? error.message : 'Unable to enter chamber';
        return;
      }
    }

    saveIdentity();
    saveInstances();
    renderIdentity();
    renderRoster();
    updatePulse();
  });

  identityClear.addEventListener('click', () => {
    identity = { email: '', handle: '' };
    sessionToken = '';
    localStorage.removeItem(STORAGE_KEYS.sessionToken);
    saveIdentity();
    renderIdentity();
    updatePulse();
  });

  composerForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = composerInput.value.trim();
    if (!message) return;

    if (backend.available) {
      if (!sessionToken) {
        identityState.textContent = 'Enter the chamber with email and handle before posting to the shared room.';
        return;
      }

      try {
        await fetchJson(`/api/rooms/${PUBLIC_ROOM_SLUG}/messages`, {
          method: 'POST',
          body: JSON.stringify({ sessionToken, body: message })
        });
        await loadBackendMessages();
      } catch (error) {
        identityState.textContent = error instanceof Error ? error.message : 'Unable to post to chamber';
        return;
      }
    } else {
      localPostRound(message);
    }

    composerInput.value = '';
  });

  resetThread.addEventListener('click', async () => {
    if (backend.available) {
      await loadBackendMessages();
      return;
    }

    thread = seedThread;
    synthesis = defaultSynthesis;
    saveThread();
    saveSynthesis();
    renderThread();
    renderSynthesis();
  });

  async function init() {
    backend = await detectBackend();
    renderIdentity();
    renderRoster();
    renderThread();
    renderSynthesis();
    updatePulse();

    if (backend.available) {
      await hydrateSession();
      await loadBackendMessages();
      renderIdentity();
      renderRoster();
      updatePulse();
    }
  }

  init();
})();

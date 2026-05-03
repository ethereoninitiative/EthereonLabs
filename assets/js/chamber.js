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
  const DEFAULT_INSTANCE_ORDER = ['primary', 'synthesizer', 'critic'];

  const instanceDefs = [
    {
      id: 'primary',
      title: 'Witness',
      summary: 'Reflects the thought plainly and names what seems to be underneath it.',
      activeByDefault: true
    },
    {
      id: 'synthesizer',
      title: 'Builder',
      summary: 'Turns the thought into one useful next step or practical direction.',
      activeByDefault: true
    },
    {
      id: 'critic',
      title: 'Skeptic',
      summary: 'Checks for vague claims, overreach, or a missing human payoff.',
      activeByDefault: true
    }
  ];

  const seedThread = [
    {
      id: 'seed-human',
      kind: 'human',
      author: 'Visitor',
      title: 'Example thought',
      text: 'I have an idea that feels interesting, but I am not sure what it should become next.',
      createdAt: new Date().toISOString()
    },
    {
      id: 'seed-primary',
      kind: 'ai-primary',
      author: 'Witness',
      title: 'Witness / plain reflection',
      text: 'You are asking for orientation. The idea has energy, but it needs a smaller first move.',
      createdAt: new Date().toISOString()
    },
    {
      id: 'seed-synth',
      kind: 'ai-synthesizer',
      author: 'Builder',
      title: 'Builder / next step',
      text: 'Write the idea in one sentence, then name the smallest version someone could actually try.',
      createdAt: new Date().toISOString()
    },
    {
      id: 'seed-critic',
      kind: 'ai-critic',
      author: 'Skeptic',
      title: 'Skeptic / check',
      text: 'Do not make the promise larger than the result. Let the first version be useful, even if it is modest.',
      createdAt: new Date().toISOString()
    }
  ];

  const defaultSynthesis = 'This prototype shows the basic loop: add a thought, view it through selected perspectives, and receive a short reflection.';

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
  let backend = { available: false, base: '', mode: 'local prototype' };

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
    const defaults = instanceDefs.filter((item) => item.activeByDefault).map((item) => item.id);
    if (!raw) return defaults;
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) && parsed.length ? canonicalRoleOrder(parsed) : defaults;
    } catch {
      return defaults;
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
    return String(text || '')
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
      const mode = backend.available && sessionToken ? 'shared backend' : 'local browser';
      identityState.innerHTML = `<strong>${escapeHtml(identity.handle || 'Visitor')}</strong><br>${escapeHtml(identity.email || 'email not needed for local prototype')}<br><small>${escapeHtml(mode)}</small>`;
    } else {
      identityState.textContent = backend.available
        ? 'Add a handle and email to use the shared room, or add only a handle for the local prototype.'
        : 'No handle saved yet. Add one to label your reflections in this browser.';
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
          <button type="button">${active ? 'Selected' : 'Select'}</button>
        </header>
        <p>${instance.summary}</p>
        <small>${active ? 'Will shape the next reflection.' : 'Off for the next reflection.'}</small>
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
    synthesisRoot.innerHTML = `<strong>Current reflection</strong><p>${escapeHtml(synthesis)}</p>`;
  }

  function updatePulse() {
    const count = activeInstances.length;
    const handle = identity.handle || 'Visitor';
    modePill.textContent = count > 1 ? 'Mode: Perspective reflection' : count === 1 ? 'Mode: Single lens' : 'Mode: Human note';
    const source = backend.available && sessionToken ? 'shared room' : 'local browser';
    pulsePill.textContent = `Pulse: ${handle} / ${count} ${count === 1 ? 'perspective' : 'perspectives'} / ${source}`;
  }

  function inferTopic(message) {
    const text = message.toLowerCase();
    if (text.includes('chamber') || text.includes('website') || text.includes('site') || text.includes('page') || text.includes('copy')) return 'website';
    if (text.includes('build') || text.includes('make') || text.includes('prototype') || text.includes('project')) return 'build';
    if (text.includes('people') || text.includes('audience') || text.includes('visitor') || text.includes('community')) return 'human';
    if (text.includes('ai') || text.includes('bot') || text.includes('agent') || text.includes('role')) return 'ai';
    if (text.includes('confus') || text.includes('stuck') || text.includes('lost') || text.includes('unclear')) return 'clarity';
    return 'general';
  }

  function roleResponse(roleId, message) {
    const topic = inferTopic(message);
    const map = {
      primary: {
        website: 'You seem to be asking whether the page gives a visitor a real reason to stay. The useful test is simple: can someone do something here and understand the result?',
        build: 'The thought has build energy. It wants a small version that can be tried before it becomes a larger system.',
        human: 'The human need underneath this is orientation. A visitor should know what to do, what happened, and why it mattered.',
        ai: 'You are circling the difference between a named role and a real working response. The role needs to be useful before it needs to be grand.',
        clarity: 'This sounds like a request for a cleaner first step. The next move should reduce noise, not add features.',
        general: 'The thought seems to be asking for shape. Something interesting is present, but it needs a smaller handle.'
      },
      synthesizer: {
        website: 'Try one concrete improvement: rewrite the page around the action a visitor can take right now, then place future plans below that.',
        build: 'Make the first version do one thing well. A small working loop will teach more than a large promise.',
        human: 'Give the visitor a short path: write something, choose lenses, read the reflection, then decide what to do next.',
        ai: 'Keep the current version honest: scripted lenses now, live AI-backed roles later.',
        clarity: 'Choose one sentence as the working goal, then cut every label that makes the page sound larger than that goal.',
        general: 'Turn the thought into a one-step experiment. The smallest useful version is the safest next build.'
      },
      critic: {
        website: 'Watch the gap between language and payoff. If the page sounds bigger than what it delivers, the visitor will feel the mismatch immediately.',
        build: 'Do not hide behind prototype language either. Even a prototype should give a clean, satisfying result.',
        human: 'Avoid insider terms. A visitor should not need the whole Ethereon vocabulary to understand the room.',
        ai: 'Do not imply live AI or multibot behavior until the backend actually supports it.',
        clarity: 'If the next step cannot be explained in plain language, it is probably still too large.',
        general: 'The risk is vague importance. Make the result plain, useful, and proportionate.'
      }
    };
    return map[roleId][topic];
  }

  function synthesisResponse(message, handle) {
    const topic = inferTopic(message);
    const name = handle || 'The visitor';
    if (topic === 'website') return `${name} is testing the page against its human payoff. The next improvement is to keep the copy small and make the working loop obvious.`;
    if (topic === 'build') return `${name} is pointing toward a practical next step: build the smallest useful version first, then let the larger system grow from evidence.`;
    if (topic === 'human') return `${name} is asking for a better visitor experience. The room should make the action, result, and purpose easy to understand.`;
    if (topic === 'ai') return `${name} is separating current function from future infrastructure: use simple perspectives now, and reserve live AI-backed roles for a later version.`;
    if (topic === 'clarity') return `${name} is asking for less noise. The next step is to name the goal plainly and remove language that overstates the result.`;
    return `${name} brought a thought that needs shape. The useful move is to make one small version clear enough to try.`;
  }

  function localPostRound(message) {
    const handle = identity.handle || 'Visitor';
    const entries = [{
      id: crypto.randomUUID(),
      kind: 'human',
      author: handle,
      title: 'Your thought',
      text: message,
      createdAt: new Date().toISOString()
    }];

    canonicalRoleOrder(activeInstances).forEach((instanceId) => {
      const instance = instanceDefs.find((item) => item.id === instanceId);
      entries.push({
        id: crypto.randomUUID(),
        kind: `ai-${instanceId}`,
        author: instance.title,
        title: `${instance.title} / perspective`,
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
      title = `${message.authorLabel} / perspective`;
    }
    if (message.authorType === 'synthesis') {
      kind = 'ai-synthesizer';
      title = 'Reflection / summary';
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

    return { available: false, base: '', mode: 'local prototype' };
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

    if (!identity.handle) {
      identityState.textContent = 'Add a handle to label your local reflections.';
      return;
    }

    if (backend.available) {
      if (!identity.email) {
        identityState.textContent = 'Email is only needed for the shared backend. Add one to join that mode, or continue locally if the backend is unavailable.';
        saveIdentity();
        renderIdentity();
        updatePulse();
        return;
      }

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
        identityState.textContent = error instanceof Error ? error.message : 'Unable to save chamber handle';
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
        identityState.textContent = 'Save a handle and email before posting to the shared room.';
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

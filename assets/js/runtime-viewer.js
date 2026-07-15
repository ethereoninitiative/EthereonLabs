(function(){
  const RECEIPT_PATH = '/public/runtime/latest_cycle.json';
  const POLL_INTERVAL_MS = 3000;

  function byId(id){
    return document.getElementById(id);
  }

  function set(id, value){
    const el = byId(id);
    if(el) el.textContent = value || '—';
  }

  function setState(id, value, state){
    const el = byId(id);
    if(!el) return;
    el.textContent = value || '—';
    el.classList.remove('is-good','is-warn','is-bad','is-muted');
    if(state) el.classList.add(state);
  }

  function formatTimestamp(value){
    if(!value) return 'No timestamp yet';
    const date = new Date(value);
    if(Number.isNaN(date.getTime())) return value;
    return date.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  }

  function metric(value){
    return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(2) : null;
  }

  function ensureInsightPanel(){
    const grid = document.querySelector('.runtime-presence-grid');
    if(!grid || byId('runtimeInsight')) return;

    const panel = document.createElement('div');
    panel.className = 'runtime-insight';
    panel.id = 'runtimeInsight';
    panel.innerHTML = `
      <div class="runtime-insight-main">
        <small>Latest observation</small>
        <p id="runtimeSummary">Waiting for the first public runtime receipt.</p>
      </div>
      <dl class="runtime-facts" aria-label="Runtime receipt details">
        <div>
          <dt>Last updated</dt>
          <dd id="runtimeUpdated">—</dd>
        </div>
        <div>
          <dt>Receipt</dt>
          <dd id="runtimeReceipt">—</dd>
        </div>
      </dl>
      <p class="microcopy runtime-boundary" id="runtimeBoundary">This panel is a witness, not a control surface.</p>
    `;
    grid.insertAdjacentElement('afterend', panel);
  }

  function summarize(data){
    const halted = Boolean(data.status && data.status.halted);
    const mode = data.mode && data.mode.current;
    const chainValid = data.governance && data.governance.chain_valid;
    const probeActive = Boolean(data.probe && data.probe.active);

    if(halted){
      return 'The latest cycle halted before completion. That is useful: the runtime stopped instead of guessing past a guardrail.';
    }

    if(mode === 'Observation' && chainValid === true && probeActive){
      return 'The system completed a bounded Observation cycle, verified its governance chain, and emitted lawful probe telemetry for display.';
    }

    if(mode === 'Observation' && chainValid === true){
      return 'The system completed a bounded Observation cycle and verified its governance chain. Probe telemetry is not present in this receipt yet.';
    }

    if(chainValid === false){
      return 'The runtime receipt loaded, but the governance chain needs review before this state should be trusted.';
    }

    return 'The Chamber is reading the latest public runtime receipt. These values describe the system state; they do not authorize action.';
  }

  async function loadRuntime(){
    ensureInsightPanel();

    try{
      const res = await fetch(RECEIPT_PATH, { cache: 'no-store' });
      if(!res.ok) throw new Error(`runtime receipt returned ${res.status}`);
      const data = await res.json();

      const mode = data.mode && data.mode.current;
      const halted = Boolean(data.status && data.status.halted);
      const statusLabel = halted ? 'Halted' : (data.status && data.status.label) || 'Stable';
      const chainValid = data.governance && data.governance.chain_valid;
      const govLabel = chainValid === true ? 'Valid chain' : chainValid === false ? 'Needs review' : 'Unknown';
      const canonHead = data.canon && data.canon.current_head;
      const canonRecords = data.canon && data.canon.record_count;
      const canonLabel = canonHead || (canonRecords ? `${canonRecords} records` : 'No canon head');
      const probe = data.probe || {};
      const probeBits = [
        probe.active ? 'Active' : 'Idle',
        metric(probe.presence) ? `presence ${metric(probe.presence)}` : null,
        metric(probe.lock) ? `lock ${metric(probe.lock)}` : null
      ].filter(Boolean);

      set('runtimeMode', mode || '—');
      setState('runtimeStatus', statusLabel, halted ? 'is-bad' : 'is-good');
      set('runtimeCanon', canonLabel);
      setState('runtimeGov', govLabel, chainValid === true ? 'is-good' : chainValid === false ? 'is-bad' : 'is-warn');
      setState('runtimeProbe', probeBits.join(' · '), probe.active ? 'is-good' : 'is-muted');
      set('runtimeSummary', summarize(data));
      set('runtimeUpdated', formatTimestamp(data.timestamp));
      set('runtimeReceipt', data.run_id || '—');
      set('runtimeBoundary', data.authority_boundary || 'Display receipt only; this panel does not execute tools or alter governance.');

    }catch(e){
      console.warn('runtime load failed', e);
      setState('runtimeStatus', 'Unavailable', 'is-warn');
      setState('runtimeGov', 'Unknown', 'is-warn');
      set('runtimeSummary', 'The Chamber could not read the public runtime receipt. The reflection prototype still works locally.');
      set('runtimeUpdated', 'Receipt unavailable');
      set('runtimeReceipt', '—');
    }
  }

  setInterval(loadRuntime, POLL_INTERVAL_MS);
  loadRuntime();
})();

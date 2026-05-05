(function(){
  async function loadRuntime(){
    try{
      const res = await fetch('/runtime/latest_cycle.json');
      const data = await res.json();

      const set = (id,val)=>{
        const el=document.getElementById(id);
        if(el) el.textContent=val ?? '—';
      };

      set('runtimeMode', data.mode?.current);
      set('runtimeStatus', data.status?.halted ? 'HALTED' : 'STABLE');
      set('runtimeCanon', data.canon?.current_head || 'none');
      set('runtimeGov', data.governance?.transition ? 'VALID' : 'BLOCKED');
      set('runtimeProbe', data.probe?.active ? 'ACTIVE' : 'IDLE');

    }catch(e){
      console.warn('runtime load failed',e);
    }
  }

  setInterval(loadRuntime,3000);
  loadRuntime();
})();
// Dependency-free: node noise_sweep_r2.mjs
function noiseSweep(){
 const L=512,phi=(1+Math.sqrt(5))/2,w=Array.from({length:L},(_,i)=>(i+1)**(-phi));const s=w.reduce((a,b)=>a+b,0);for(let i=0;i<L;i++)w[i]/=s;
 const rows=[];for(const [name,alpha] of [["zero",0],["very_slow",.0001],["slow",.01],["phi",phi-1],["sqrt2",Math.sqrt(2)-1],["quarter",.25]]){
 let A=0,B=0,C=0;for(let i=0;i<L;i++){let x=w[i]*Math.cos(2*Math.PI*alpha*(i+1)),y=w[i]*Math.sin(2*Math.PI*alpha*(i+1));A+=x*x;B+=x*y;C+=y*y}
 const tr=A+C,det=Math.max(0,A*C-B*B),high=(tr+Math.hypot(A-C,2*B))/2,low=det/high;
 const noise=[1e-6,1e-4,.001,.01].map(v=>({variance:v,capacity:high/(high+v)+low/(low+v)}));
 if(noise.some(x=>x.capacity>2||x.capacity<0))throw Error("capacity bound");rows.push({name,alpha,eigenvalues:[high,low],noise})
 }return {L,p:phi,rows};
}
console.log(JSON.stringify(noiseSweep(),null,2));

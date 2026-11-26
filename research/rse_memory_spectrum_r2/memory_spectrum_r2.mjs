// Dependency-free: node memory_spectrum_r2.mjs
function experiment(){
 const L=512,phi=(1+Math.sqrt(5))/2, sum=a=>a.reduce((x,y)=>x+y,0), norm=a=>{let s=sum(a);return a.map(x=>x/s)}, p=norm(Array.from({length:L},(_,i)=>(i+1)**(-phi))), exp=q=>norm(Array.from({length:L},(_,i)=>q**i)), energy=a=>sum(a.map(x=>x*x)), assert=(c,m)=>{if(!c)throw Error(m)};
 let lo=0,hi=1;for(let i=0;i<70;i++){const q=(lo+hi)/2;if(energy(exp(q))>energy(p))lo=q;else hi=q;}
 const q=(lo+hi)/2,e=exp(q),lags=[1,2,4,8,16,32,64,128,256,512], bands=[[1,8],[9,32],[33,128],[129,512]];
 const spiral=(w,a)=>w.map((v,i)=>[v*Math.cos(2*Math.PI*a*(i+1)),v*Math.sin(2*Math.PI*a*(i+1))]);
 function assay(name, h){
  const A=sum(h.map(x=>x[0]**2)),B=sum(h.map(x=>x[0]*x[1])),C=sum(h.map(x=>x[1]**2)),det=A*C-B*B,rank=det>1e-12*(A+C)**2?2:1;
  const score=h.map(([x,y])=>rank===2?(C*x*x-2*B*x*y+A*y*y)/det:(x*x+y*y)/(A+C));
  assert(score.every(x=>x>=-1e-12&&x<=1+1e-12),name+" score bounds");
  assert(Math.abs(sum(score)-rank)<1e-9,name+" capacity identity");
  return {name,rank,capacity:sum(score),lag_r2:Object.fromEntries(lags.map(i=>[i,score[i-1]])),band_capacity:Object.fromEntries(bands.map(([a,b])=>[a+"-"+b,sum(score.slice(a-1,b))])),covariance:[A,B,C],score};
 }
 const expSlow=exp(.97); const cases=[assay("power_real",p.map(x=>[x,0])),assay("exponential_real_matched_energy",e.map(x=>[x,0])),assay("power_phi",spiral(p,phi-1)),assay("power_sqrt2",spiral(p,Math.sqrt(2)-1)),assay("power_quarter",spiral(p,.25)),assay("power_nearzero",spiral(p,.01)),assay("exponential_phi",spiral(e,phi-1)),assay("two_exponential",e.map((v,i)=>[v,expSlow[i]]))];
 function empirical(h,caseInfo){
   const n=8192, samples=Array.from({length:n+L},()=>0);let state=90210;for(let i=0;i<samples.length;i++){state=(Math.imul(1664525,state)+1013904223)>>>0;samples[i]=(state>>>31)?1:-1;}
   const [A,B,C]=caseInfo.covariance,det=A*C-B*B;let s=0,err=0;const lag=4,[x,y]=h[lag-1],beta=caseInfo.rank===2?[(C*x-B*y)/det,(A*y-B*x)/det]:[x/(A+C),y/(A+C)];
   for(let t=L;t<n+L;t++){let a=0,b=0;for(let i=0;i<L;i++){a+=h[i][0]*samples[t-i-1];b+=h[i][1]*samples[t-i-1];}const target=samples[t-lag];err+=(target-a*beta[0]-b*beta[1])**2;s+=target*target;}
   const r2=1-err/s;assert(Math.abs(r2-caseInfo.lag_r2[lag])<.05,"Monte Carlo check");return r2;
 }
 const checks=[["power_real",p.map(x=>[x,0])],["power_phi",spiral(p,phi-1)],["two_exponential",e.map((v,i)=>[v,expSlow[i]])]].map(([name,h])=>({name,lag:4,empirical_r2:empirical(h,cases.find(x=>x.name===name))}));
 return {L,p:phi,matched_exponential_q:q,matched_energy:energy(p),exponential_energy:energy(e),slow_exponential_q:.97,checks,cases:cases.map(({score,...v})=>v)};
}
console.log(JSON.stringify(experiment(),null,2));

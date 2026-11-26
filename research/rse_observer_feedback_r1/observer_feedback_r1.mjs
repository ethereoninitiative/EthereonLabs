// RSE Observer Feedback R1. Dependency-free; node observer_feedback_r1.mjs
function experiment(){
 const phi=(1+Math.sqrt(5))/2,L=256,T=2048,p=phi,g=.65;
 const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],sub=(a,b)=>[a[0]-b[0],a[1]-b[1]],mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]],conj=a=>[a[0],-a[1]],scale=(a,s)=>[a[0]*s,a[1]*s],abs=a=>Math.hypot(...a),cis=x=>[Math.cos(x),Math.sin(x)],div=(a,b)=>scale(mul(a,conj(b)),1/(abs(b)**2));
 const check=(condition,msg)=>{if(!condition)throw Error(msg)};
 let w=Array.from({length:L},(_,i)=>(i+1)**(-p));const norm=w.reduce((a,b)=>a+b,0);w=w.map(x=>x/norm);
 const rows=[];
 for(const [label,alpha] of [["phi",phi-1],["sqrt2",Math.sqrt(2)-1],["one_seventh",1/7],["near_zero",.01]]){
  const theta=2*Math.PI*alpha,ks=w.map((x,i)=>scale(cis(theta*(i+1)),x)),kb=w.reduce((s,x,i)=>add(s,scale(cis(2*theta*(i+1)),x)),[0,0]);
  for(const eta of [0,.3]){
   check(g*(1+eta)<1,"contractive");
   const c=conj(kb),d=sub([1,0],scale(c,g)),den=sub(scale(d,1-g),scale(c,g*g*eta*eta)),a=div(d,den),b=conj(div([g*eta,0],den));
   const z=[];
   let maxError=0;
   for(let t=0;t<T;t++){
    let m=[0,0];for(let n=1;n<=Math.min(t,L);n++)m=add(m,mul(ks[n-1],z[t-n]));
    const u=cis(theta*t);z.push(add(u,scale(add(m,scale(conj(m),eta)),g)));
    if(t>=T-64){const expected=add(mul(a,u),mul(b,conj(u)));maxError=Math.max(maxError,abs(sub(z[t],expected)));}
   }
   check(maxError<1e-8,"analytic/time-domain disagreement "+label+" "+eta+" "+maxError);
   if(eta===0){check(abs(b)<1e-12,"unexpected mirror");check(Math.abs(abs(a)-1/(1-g))<1e-12,"gauge invariance");}
   else check(abs(b)>.1,"missing mirror");
   rows.push({rotation:label,alpha,eta,primary:abs(a),mirror:abs(b),mirror_ratio:abs(b)/abs(a),max_last64_error:maxError});
  }
 }
 return {model:"finite normalized power-law kernel; zero prehistory; complex unit tone",L,T,p,g,rows,checks:"all passed"};
}
console.log(JSON.stringify(experiment(), null, 2));

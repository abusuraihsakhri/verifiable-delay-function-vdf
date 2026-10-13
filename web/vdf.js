/* Browser-only educational Wesolowski VDF; NOT production cryptography. */
(function(root) {
  'use strict';
  const MAX_ITERATIONS=10000;
  const BASES=[2n,325n,9375n,28178n,450775n,9780504n,1795265022n];
  function integer(value,label) {
    const s=String(value).trim();
    if(!/^(0|[1-9][0-9]*)$/.test(s)) throw Error(label+' must be an unsigned decimal integer');
    return BigInt(s);
  }
  function gcd(a,b) { while(b!==0n) [a,b]=[b,a%b]; return a; }
  function validate(n,x,t) {
    if(n<9n || n%2n!==1n || n.toString(2).length>4096) throw Error('Modulus must be odd, at least 9, and at most 4096 bits');
    if(x<2n || x>n-2n || gcd(x,n)!==1n) throw Error('Base must be between 2 and N-2 and coprime to N');
    if(!Number.isSafeInteger(t) || t<1 || t>MAX_ITERATIONS) throw Error('Iterations must be an integer from 1 to 10000');
  }
  function powmod(base,exponent,n) {
    let answer=1n; base%=n;
    while(exponent>0n) {
      if(exponent&1n) answer=answer*base%n;
      base=base*base%n; exponent>>=1n;
    }
    return answer;
  }
  function prime64(p) {
    if(p<2n) return false;
    for(const small of [2n,3n,5n,7n,11n,13n,17n,19n,23n,29n,31n,37n]) {
      if(p%small===0n) return p===small;
    }
    let d=p-1n,s=0;
    while(d%2n===0n) { d/=2n; s++; }
    for(const a of BASES) {
      if(a%p===0n) continue;
      let z=powmod(a,d,p);
      if(z===1n || z===p-1n) continue;
      let witness=true;
      for(let i=1;i<s;i++) {
        z=z*z%p;
        if(z===p-1n) { witness=false; break; }
      }
      if(witness) return false;
    }
    return true;
  }
  async function challengePrime(n,x,t,y) {
    const transcript='wesolowski-demo-v1|'+n+'|'+x+'|'+t+'|'+y;
    const digest=new Uint8Array(await root.crypto.subtle.digest('SHA-256',new TextEncoder().encode(transcript)));
    let l=0n;
    for(const byte of digest.slice(0,8)) l=(l<<8n)|BigInt(byte);
    l|=(1n<<63n)|1n;
    while(!prime64(l)) { l+=2n; if(l>=(1n<<64n)) l=(1n<<63n)+1n; }
    return l;
  }
  async function prove(modulus,base,iterations,progress) {
    const n=integer(modulus,'Modulus'),x=integer(base,'Base'),t=Number(iterations);
    validate(n,x,t);
    let y=x;
    for(let i=0;i<t;i++) {
      y=y*y%n;
      if(progress && (i+1)%256===0) {
        progress('Evaluating',i+1,t);
        await new Promise(resolve=>setTimeout(resolve,0));
      }
    }
    const l=await challengePrime(n,x,t,y);
    let pi=1n,r=1n;
    // Divide the binary exponent 2^T by l, collecting quotient bits.
    for(let i=0;i<t;i++) {
      const doubled=r*2n,bit=doubled>=l;
      r=doubled%l;
      pi=pi*pi%n;
      if(bit) pi=pi*x%n;
      if(progress && (i+1)%256===0) {
        progress('Proving',i+1,t);
        await new Promise(resolve=>setTimeout(resolve,0));
      }
    }
    return {modulus:String(n),base:String(x),iterations:t,output:String(y),proof:String(pi),challenge:String(l),remainder:String(r)};
  }
  async function verify(data) {
    try {
      const n=integer(data.modulus,'Modulus'),x=integer(data.base,'Base'),t=Number(data.iterations);
      validate(n,x,t);
      const y=integer(data.output,'Output'),pi=integer(data.proof,'Proof');
      const l=integer(data.challenge,'Challenge'),r=integer(data.remainder,'Remainder');
      if(y>=n || pi<1n || pi>=n) return false;
      if(l!==await challengePrime(n,x,t,y)) return false;
      if(r!==powmod(2n,BigInt(t),l)) return false;
      return (powmod(pi,l,n)*powmod(x,r,n))%n===y;
    } catch (_) { return false; }
  }
  const api={prove,verify,challengePrime,powmod,prime64};
  if(typeof module!=='undefined' && module.exports) module.exports=api;
  if(typeof document==='undefined') return;
  document.addEventListener('DOMContentLoaded',function(){
    const $=id=>document.getElementById(id);
    const output=$('proof-json'),message=$('message'),generate=$('generate'),check=$('verify');
    generate.addEventListener('click',async function() {
      generate.disabled=true; check.disabled=true;
      message.textContent='Evaluating sequential modular squares...';
      try {
        const start=performance.now();
        const result=await prove($('modulus').value,$('base').value,$('iterations').value,
          (stage,done,total)=>{message.textContent=stage+': '+done+' / '+total+' squarings';});
        const valid=await verify(result);
        output.value=JSON.stringify(result,null,2);
        message.textContent=(valid?'Proof verified':'Proof verification failed')+' - '+result.iterations+' sequential squarings - '+(performance.now()-start).toFixed(1)+' ms total (device-specific)';
        check.disabled=false;
      } catch(err) { message.textContent='Error: '+err.message; }
      finally { generate.disabled=false; }
    });
    check.addEventListener('click',async function() {
      check.disabled=true;
      try {
        const valid=await verify(JSON.parse(output.value));
        message.textContent=valid?'Proof verified against the transcript':'Proof rejected: inconsistent or modified data';
      } catch (_) { message.textContent='Error: proof is not valid JSON'; }
      finally { check.disabled=false; }
    });
    $('copy').addEventListener('click',async function(){
      if(!output.value) return;
      try { await navigator.clipboard.writeText(output.value); message.textContent='Proof JSON copied'; }
      catch (_) { output.focus(); output.select(); message.textContent='Select and copy the highlighted JSON'; }
    });
  });
})(typeof globalThis!=='undefined'?globalThis:this);

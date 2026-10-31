// Screenshot mit Chrome (headless) – Werkstatt, nur auf daniel.
// node screenshot.mjs <url> <breite> <hoehe> <datei> [js]   Env: DSF, CLIP (Selektor), MESS (JS → stdout), TRANSPARENT=1
import { spawn } from 'node:child_process';
import fs from 'node:fs';
const [url, w, h, out, js] = process.argv.slice(2);
const port = 9333 + Math.floor(Math.random()*500);
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new','--disable-gpu','--hide-scrollbars',`--remote-debugging-port=${port}`,`--user-data-dir=/tmp/cdp-${port}`,'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws; for (let i=0;i<60;i++){ try{ const l = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); const p=l.find(x=>x.type==='page'); if(p){ws=p.webSocketDebuggerUrl;break;} }catch{} await sleep(200); }
const s = new WebSocket(ws); await new Promise(r=>s.onopen=r);
let id=0; const pend={}; s.onmessage=e=>{const m=JSON.parse(e.data); if(m.method==='Runtime.exceptionThrown'){const d=m.params.exceptionDetails; console.log('FEHLER', ((d.exception&&d.exception.description)||d.text).slice(0,300));} if(m.id&&pend[m.id]){pend[m.id](m.result);delete pend[m.id];}};
const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;s.send(JSON.stringify({id:i,method,params}));});
await send('Emulation.setDeviceMetricsOverride',{width:+w,height:+h,deviceScaleFactor:+(process.env.DSF||1),mobile:+w<600});
if (process.env.TRANSPARENT) await send('Emulation.setDefaultBackgroundColorOverride',{color:{r:0,g:0,b:0,a:0}});
await send('Runtime.enable'); await send('Page.enable'); await send('Page.navigate',{url}); await sleep(3000);
if (js) { await send('Runtime.evaluate',{expression:js,awaitPromise:true}); await sleep(700); }
if (process.env.MESS) { const e=await send('Runtime.evaluate',{expression:process.env.MESS,returnByValue:true}); console.log(e.result.value); }
let clip; if (process.env.CLIP){ const e=await send('Runtime.evaluate',{expression:`JSON.stringify(document.querySelector('${process.env.CLIP}').getBoundingClientRect())`,returnByValue:true}); const b=JSON.parse(e.result.value); clip={x:b.x,y:b.y,width:b.width,height:b.height,scale:1}; }
const r = await send('Page.captureScreenshot', clip?{format:'png',clip,captureBeyondViewport:true}:{format:'png'});
fs.writeFileSync(out, Buffer.from(r.data,'base64')); chrome.kill(); process.exit(0);

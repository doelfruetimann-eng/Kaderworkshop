/* Nimmt die Bildspur zum Lernvideo auf: Playwright faehrt den Wizard im
   Demo-Modus ab, blendet Untertitel und Schrittzaehler ein und schiesst
   alle FPS_MS ein Bild. Der Ton wird spaeter in mische.py daruntergelegt. */
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';

const WURZEL   = '/home/user/CAS-KI';
const SEITE    = 'file:///workspace/youtube/web/public/kadertagung/index.html?demo=1';
const CHROME   = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const AUS      = '/home/user/CAS-KI/scratchpad/video/frames';
const FPS_MS   = 100;                      /* 10 Bilder je Sekunde */
const BREITE   = 1280, HOEHE = 800;

const szenen = JSON.parse(fs.readFileSync(path.join(WURZEL,'docs/lernvideo-teilnahme-szenen.json'),'utf-8'));
fs.rmSync(AUS,{recursive:true,force:true}); fs.mkdirSync(AUS,{recursive:true});

const b = await chromium.launch({executablePath: CHROME});
const p = await b.newPage({viewport:{width:BREITE,height:HOEHE}, deviceScaleFactor:1.5});
const fehler = [];
p.on('pageerror', e => fehler.push('PAGEERROR: '+e.message));

await p.goto(SEITE,{waitUntil:'load'});
await p.waitForTimeout(700);

/* Untertitelband, Schrittzaehler und Hervorhebung — als eigene Ebene ueber der Seite,
   damit Schrift und Umlaute von der Seite selbst kommen und nicht von ffmpeg. */
await p.addStyleTag({content:`
  #vid-cap{position:fixed;left:0;right:0;bottom:0;z-index:99998;
    background:linear-gradient(to top,rgba(12,26,46,.96),rgba(12,26,46,.86));
    color:#fff;font:600 25px/1.4 "PT Sans",system-ui,sans-serif;
    padding:20px 44px 24px;text-align:center;letter-spacing:.1px}
  #vid-step{position:fixed;right:22px;top:18px;z-index:99998;
    background:#8A0B38;color:#fff;font:700 15px/1 "PT Sans",system-ui,sans-serif;
    padding:9px 15px;border-radius:999px;letter-spacing:.4px}
  .vid-hl{position:relative;z-index:99997;
    outline:3px solid #FFD136 !important;outline-offset:3px;border-radius:6px;
    box-shadow:0 0 0 9999px rgba(12,26,46,.34) !important;transition:none}
  html{scroll-behavior:auto !important}
`});
await p.evaluate(() => {
  const c=document.createElement('div'); c.id='vid-cap'; document.body.appendChild(c);
  const s=document.createElement('div'); s.id='vid-step'; document.body.appendChild(s);
});
const setzen = (cap, step) => p.evaluate(([c,s]) => {
  document.getElementById('vid-cap').textContent = c;
  const e = document.getElementById('vid-step');
  e.textContent = s; e.style.display = s ? '' : 'none';
}, [cap, step]);


let nr = 0;
const T0 = Date.now();               /* Beginn der gesamten Aufnahme */
const bilder = [];                   /* {datei, t}  t = ms seit T0 */
const szenenZeit = [];               /* {id, start, dauerSoll} */
const schuss = async () => {
  const datei = `f${String(nr++).padStart(5,'0')}.png`;
  bilder.push({datei, t: Date.now()-T0});
  await p.screenshot({path:`${AUS}/${datei}`});
};

/* Nimmt Bilder auf, bis MS verstrichen sind. */
async function laufen(ms){
  const bis = Date.now()+ms;
  while(Date.now() < bis){ await schuss(); await p.waitForTimeout(Math.max(0,FPS_MS-35)); }
}
async function hl(sel){
  await p.evaluate(s => { const e=document.querySelector(s); if(e) e.classList.add('vid-hl'); }, sel);
}
async function unhl(){
  await p.evaluate(() => document.querySelectorAll('.vid-hl').forEach(e=>e.classList.remove('vid-hl')));
}

for(const s of szenen){
  const t0 = Date.now();
  szenenZeit.push({id: s.id, start: (t0-T0)/1000, dauerSoll: s.dauer, ton_von: s.ton_von, ton_bis: s.ton_bis});
  const gesamtMs = s.dauer*1000;
  await setzen(s.cap, s.step);
  const teile = String(s.akt||'').split('|');
  for(let i=0;i<teile.length;i++){
    const a = teile[i];
    if(a.startsWith('pause:'))      { await laufen(Number(a.slice(6))); }
    else if(a.startsWith('warte:')) { await laufen(Number(a.slice(6))); }
    else if(a.startsWith('hl:'))    { await hl(a.slice(3)); }
    else if(a === 'unhl')           { await unhl(); }
    else if(a.startsWith('scroll:')){ const sel=a.slice(7);
        await p.evaluate(x=>{const e=document.querySelector(x); if(e) e.scrollIntoView({block:'center'});}, sel);
        await laufen(500); }
    else if(a.startsWith('klick:')) { const sel=a.slice(6);
        const el=p.locator(sel).first();
        if(await el.count()) { await el.click({timeout:4000}).catch(e=>fehler.push(`Klick ging nicht: ${sel} (${s.id})`)); }
        else fehler.push(`fehlt: ${sel} (${s.id})`);
        await laufen(250); }
    else if(a.startsWith('tippe:')) {
        /* tippe:SELEKTOR|TEXT — der Text steht im naechsten Teilstueck */
        const ziel=a.slice(6); const txt=teile[++i]||'';
        const el=p.locator(ziel).first();
        if(await el.count()){ await el.fill(txt); } else fehler.push(`fehlt: ${ziel} (${s.id})`);
        await laufen(300); }
    else if(a.startsWith('etappe:')) { const n=Number(a.slice(7));
        const el=p.locator('[data-etappe]').nth(n);
        if(await el.count()){ await el.click({timeout:4000}).catch(e=>fehler.push(`Etappe ${n} blockiert (${s.id})`)); }
        else fehler.push(`Etappe ${n} fehlt (${s.id})`);
        await laufen(300); }
    else if(a.startsWith('dialog:')) { const txt=a.slice(7);
        const el=p.locator('.ov button', {hasText:txt}).first();
        if(await el.count()){ await el.click({timeout:4000}).catch(()=>{}); }
        else fehler.push(`Dialogknopf «${txt}» fehlt (${s.id})`);
        await laufen(250); }
    else if(a === 'abwarten')       {
        /* 80 % der SPRECHZEIT — nicht der Szenendauer. Sonst rutscht der Klick
           in die Atempause am Szenenende und das Bild haengt hinterher. */
        const zielMs = (s.sprechdauer || s.dauer)*1000*0.80;
        const rest = zielMs - (Date.now()-t0);
        if(rest > 0) await laufen(rest); }
  }
  await unhl();
  const rest = gesamtMs - (Date.now()-t0);
  if(rest > 0) await laufen(rest);
  console.log(`${s.id.padEnd(16)} soll ${s.dauer.toFixed(2)}s  ist ${((Date.now()-t0)/1000).toFixed(2)}s  Bilder ${nr}`);
}
const gesamt = (Date.now()-T0)/1000;
await b.close();
fs.writeFileSync(`${AUS}/../aufnahme.json`, JSON.stringify({gesamt, bilder, szenen: szenenZeit}, null, 1));
console.log(`\n${nr} Bilder in ${AUS} · Gesamtlaenge ${gesamt.toFixed(2)}s`);
if(fehler.length){ console.log('\nPROBLEME:\n'+fehler.join('\n')); process.exit(1); }
console.log('keine Probleme');

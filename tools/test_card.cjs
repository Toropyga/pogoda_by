/* Browser tests with stock Node.js >=22 and a locally installed Chrome. */
const { spawn } = require('node:child_process');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const http = require('node:http');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function main() {
  const chromePath = process.env.CHROME_BIN || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const output = path.resolve(process.argv[2] || path.join(os.tmpdir(), 'pogoda-card-check'));
  await fs.mkdir(output, {recursive:true});
  const profile = await fs.mkdtemp(path.join(os.tmpdir(),'pogoda-card-chrome-'));
  const server = http.createServer(async (req,res) => {
    const filename = path.resolve(root, '.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
    if (!filename.startsWith(root+path.sep)) {res.writeHead(403).end();return;}
    try {const data=await fs.readFile(filename);res.setHeader('Content-Type',filename.endsWith('.js')?'text/javascript; charset=utf-8':'text/html; charset=utf-8');res.end(data)} catch {res.writeHead(404).end()}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const chrome=spawn(chromePath,['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-extensions','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore',windowsHide:true});
  let ws, exitError;
  chrome.on('error',e=>{exitError=e});
  try {
    let port;
    for(let i=0;i<100;i++){if(exitError)throw exitError;try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch{await delay(100)}}
    if(!port)throw new Error('Chrome did not expose a debugging port');
    const targets=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true})});
    let nextId=0;const pending=new Map(),errors=[];
    ws.addEventListener('message',event=>{const data=JSON.parse(event.data);if(data.id){const p=pending.get(data.id);pending.delete(data.id);data.error?p?.reject(new Error(JSON.stringify(data.error))):p?.resolve(data.result)}else if(data.method==='Runtime.exceptionThrown') errors.push(data.params.exceptionDetails.text)});
    const cdp=(method,params={})=>new Promise((resolve,reject)=>{const id=++nextId;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
    const evaluate=async expression=>{const r=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value};
    await cdp('Runtime.enable');
    await cdp('Emulation.setDeviceMetricsOverride',{width:900,height:1000,deviceScaleFactor:1,mobile:false});
    await cdp('Page.navigate',{url:`http://127.0.0.1:${server.address().port}/tools/card-preview.html`});
    for(let i=0;i<100;i++){if(await evaluate("Boolean(window.card?.shadowRoot.querySelector('.value') && window.card._graph)"))break;await delay(50)}
    const results=[];
    const check=async(name,expression)=>{assert.equal(await evaluate(expression),true,name);results.push(name)};
    await check('Renamed entities resolved by unique_id',"card.shadowRoot.querySelector('.value').textContent === '7,4'");
    await check('Real sensor units preserved',"card.shadowRoot.querySelector('.unit').textContent === '°C'");
    await check('Station selected and observed time shown',"card.shadowRoot.querySelector('h2').textContent==='Минск' && !!card.shadowRoot.querySelector('time')");
    await check('No synthetic optional readings',"card.shadowRoot.querySelectorAll('.metric').length===2");
    await check('History helper receives renamed temperature and 24 hours',"helperCalls[0].entities[0].entity==='sensor.renamed_temperature' && helperCalls[0].hours_to_show===24");
    await check('Recent observation status',"card.shadowRoot.querySelector('.status').textContent==='Свежие данные'");
    await check('Click opens correct entity',"(()=>{let found;card.addEventListener('hass-more-info',e=>found=e.detail.entityId,{once:true});card.shadowRoot.querySelector('.temp').click();return found==='sensor.renamed_temperature'})()");
    await check('Unrelated hass updates preserve history instance',"(()=>{const graph=card._graph;card.hass={...demoHass,states:{...demoHass.states,'light.demo':{state:'on',attributes:{}}}};return card._graph===graph})()");
    await cdp('Page.captureScreenshot',{format:'png'}).then(r=>fs.writeFile(path.join(output,'pogoda-card-light.png'),Buffer.from(r.data,'base64')));
    await evaluate("document.body.classList.add('dark')");
    await cdp('Page.captureScreenshot',{format:'png'}).then(r=>fs.writeFile(path.join(output,'pogoda-card-dark.png'),Buffer.from(r.data,'base64')));
    await cdp('Emulation.setDeviceMetricsOverride',{width:360,height:1000,deviceScaleFactor:1,mobile:false});
    await check('Mobile layout has no horizontal overflow',"document.documentElement.scrollWidth===360 && card.shadowRoot.querySelector('ha-card').scrollWidth<=card.clientWidth");
    await cdp('Page.captureScreenshot',{format:'png'}).then(r=>fs.writeFile(path.join(output,'pogoda-card-mobile.png'),Buffer.from(r.data,'base64')));
    await check('Old observations detected',"(()=>{demoHass.states['sensor.renamed_observation_time'].state=new Date(Date.now()-4*3600000).toISOString();card.hass={...demoHass};return card.shadowRoot.querySelector('.status').textContent==='Устаревшие данные'})()");
    await check('Missing observation never shown as fresh',"(()=>{demoHass.states['sensor.renamed_observation_time'].state='unknown';card.hass={...demoHass};return card.shadowRoot.querySelector('.status').textContent==='Время наблюдения неизвестно'&&!card.shadowRoot.querySelector('time')})()");
    await check('Unavailable readings remain missing, not zero',"(()=>{for(const f of ['temperature','pressure','condition','wind_speed'])demoHass.states['sensor.renamed_'+f].state='unavailable';card.hass={...demoHass};return card.shadowRoot.querySelector('.value').textContent==='—'&&card.shadowRoot.querySelector('.status').classList.contains('off')})()");
    await check('Zero and Fahrenheit render correctly',"(()=>{Object.assign(demoHass.states['sensor.renamed_temperature'],{state:'0',attributes:{unit_of_measurement:'°F'}});card.hass={...demoHass};return card.shadowRoot.querySelector('.value').textContent==='0'&&card.shadowRoot.querySelector('.unit').textContent==='°F'})()");
    await check('Markup from provider and configuration is escaped',"(()=>{demoHass.states['sensor.renamed_condition'].state='<img src=x onerror=alert(1)>';card.setConfig({...demoConfig,name:'<b>Title</b>'});return !card.shadowRoot.querySelector('img')&&!card.shadowRoot.querySelector('h2 b')&&card.shadowRoot.querySelector('h2').textContent==='<b>Title</b>'})()");
    await check('Graph disabled removes history',"(()=>{card.setConfig({...demoConfig,show_graph:false});return !card._graph&&!card.shadowRoot.querySelector('.history').children.length})()");
    await check('Optional metrics appear only when available',"(()=>{demoHass.states['sensor.hum']={state:'78',attributes:{unit_of_measurement:'%'}};card.setConfig({...demoConfig,show_graph:false,entities:{humidity:'sensor.hum'}});return card.shadowRoot.querySelectorAll('.metric').length===3})()");
    await check('Manual mapping works without registry',"(()=>{const el=document.createElement('pogoda-by-card');el.setConfig({entities:{temperature:'sensor.renamed_temperature'},show_graph:false});el.hass={...demoHass,callWS:undefined};return el.shadowRoot.querySelector('.value').textContent==='0'})()");
    await check('Invalid configuration rejected',"(()=>{try{card.setConfig({...demoConfig,hours_to_show:0});return false}catch{return true}})()");
    await check('Five interface languages available',"(()=>{return ['ru','be','pl','en','de'].every(language=>{card.setConfig({...demoConfig,show_graph:false,language});return !!card.shadowRoot.querySelector('.status').textContent})})()");
    await check('Editor lists station and preserves Lovelace options',"(async()=>{const el=card.constructor.getConfigElement();el.setConfig({...demoConfig,grid_options:{columns:12},visibility:[{condition:'user',users:['demo']}]});el.hass=demoHass;document.getElementById('editor').append(el);await new Promise(r=>setTimeout(r,10));let config;el.addEventListener('config-changed',e=>config=e.detail.config);const box=el.shadowRoot.querySelector('[data-key=show_graph]');box.checked=false;box.dispatchEvent(new Event('change',{bubbles:true}));return !!el.shadowRoot.querySelector('option[value=BY_26850]')&&config.show_graph===false&&config.grid_options.columns===12&&config.visibility[0].condition==='user'})()");
    await check('Late history helper cannot restore disabled graph',"(async()=>{let release;window.loadCardHelpers=()=>new Promise(r=>release=r);card.setConfig({...demoConfig,show_graph:true,hours_to_show:12});await new Promise(r=>setTimeout(r,0));card.setConfig({...demoConfig,show_graph:false});release({createCardElement(){throw new Error('stale helper must not create graph')}});await new Promise(r=>setTimeout(r,0));return !card._graph&&!card.shadowRoot.querySelector('.history').children.length})()");
    await check('History loading error is contained',"(async()=>{window.loadCardHelpers=async()=>{throw new Error('test failure')};card.setConfig({...demoConfig,show_graph:true,hours_to_show:48});await new Promise(r=>setTimeout(r,10));return !!card.shadowRoot.querySelector('.history .message')&&!!card.shadowRoot.querySelector('.value')})()");
    assert.deepEqual(errors,[],'No unhandled browser exceptions');
    console.log(JSON.stringify({passed:results.length,tests:results,unhandledErrors:errors,screenshots:output},null,2));
    await fs.writeFile(path.join(output,'validation.json'),JSON.stringify({passed:results.length,tests:results,unhandledErrors:errors},null,2));
  } finally {if(ws)ws.close();chrome.kill();server.close()}
}
main().catch(error=>{console.error(error);process.exitCode=1});

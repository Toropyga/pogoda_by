/* Logic checks against a minimal DOM host. No rendering engine or HA server. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname,'../custom_components/pogoda_by/frontend/pogoda-by-card.js'),'utf8');

class Node {
  constructor() {this.innerHTML='';this.children=[];this.style={};this.listeners={};}
  replaceChildren(...nodes) {this.innerHTML='';this.children=nodes;}
  addEventListener(type,listener) {this.listeners[type]=listener;}
}
class Root extends Node {
  constructor() {super();this.nodes=new Map();}
  querySelector(selector) {if(!this.nodes.has(selector))this.nodes.set(selector,new Node());return this.nodes.get(selector);}
}
function environment({rejectRegistry=false,helper}={}) {
  const definitions=new Map();
  class Element extends Node {
    attachShadow() {this.shadowRoot=new Root();return this.shadowRoot;}
    dispatchEvent(event) {this.lastEvent=event;return true;}
  }
  const context={HTMLElement:Element,console:{info(){}},setInterval,clearInterval,Intl,Date,Promise,
    CustomEvent:class {constructor(type,options){this.type=type;Object.assign(this,options);}},
    customElements:{get:key=>definitions.get(key),define:(key,value)=>definitions.set(key,value)},
    document:{createElement:key=>definitions.has(key)?new (definitions.get(key))():new Node()}
  };
  context.window={loadCardHelpers:helper||async function(){return {createCardElement(config){const el=new Node();el.config=config;return el;}}}};
  vm.runInNewContext(source,context);
  const fields={station:'Минск',temperature:'7.4',condition:'Переменная облачность',pressure:'1018',pressure_trend:'растёт',wind_speed:'0',wind_direction:'штиль',observation_time:new Date(Date.now()-30*60000).toISOString()};
  const states={},entries=[];
  for(const [key,state]of Object.entries(fields)) {
    const entity_id='sensor.custom_'+key;
    entries.push({entity_id,platform:'pogoda_by',unique_id:'BY_26850_'+key,disabled_by:null});
    states[entity_id]={entity_id,state,attributes:{unit_of_measurement:({temperature:'°C',pressure:'hPa',wind_speed:'m/s'})[key],...(key==='station'?{country:'BY',station_id:'26850',observation_url:'https://pogoda.by/observation/meteo-observation/26850'}:{station_id:'26850'})}};
  }
  let registryCalls=0;
  const hass={states,connection:{},locale:{language:'ru'},config:{time_zone:'Europe/Minsk'},
    callWS:async()=>{registryCalls++;if(rejectRegistry)throw new Error('unavailable');return entries},
    formatEntityState(state){const number=Number(state.state);return (Number.isFinite(number)?new Intl.NumberFormat('ru').format(number):state.state)+(state.attributes.unit_of_measurement?' '+state.attributes.unit_of_measurement:'')}
  };
  const make=(config={})=>{const card=new(definitions.get('pogoda-by-card'))();card.setConfig({type:'custom:pogoda-by-card',station:'BY_26850',...config});card.hass=hass;return card;};
  return {hass,entries,make,context,definitions,calls:()=>registryCalls};
}
const flush=()=>new Promise(resolve=>setImmediate(resolve));
const summary=card=>card.shadowRoot.querySelector('.summary').innerHTML;

test('station discovery resolves arbitrary renamed IDs',async()=>{
  const e=environment(),card=e.make();await flush();
  assert.match(summary(card),/<h2>Минск<\/h2>/);
  assert.match(summary(card),/class="value">7,4<\/span>/);
  assert.match(summary(card),/data-entity="sensor.custom_wind_speed"/);
  assert.equal(card._graph.config.entities[0].entity,'sensor.custom_temperature');
});
test('registry requests are shared between cards',async()=>{
  const e=environment();e.make();e.make();await flush();assert.equal(e.calls(),1);
});
test('unrelated integration with same station-like unique_id cannot leak in',async()=>{
  const e=environment();e.entries.unshift({entity_id:'sensor.other',platform:'other',unique_id:'BY_26850_temperature'});
  const card=e.make();await flush();assert.match(summary(card),/7,4/);assert.equal(card._graph.config.entities[0].entity,'sensor.custom_temperature');
});
test('two stations remain isolated',async()=>{
  const e=environment();
  e.entries.push({entity_id:'sensor.brest_temp',platform:'pogoda_by',unique_id:'BY_33008_temperature'});
  e.hass.states['sensor.brest_temp']={state:'12',attributes:{unit_of_measurement:'°C'}};
  const card=e.make({station:'BY_33008'});await flush();
  assert.match(summary(card),/class="value">12<\/span>/);assert.doesNotMatch(summary(card),/7,4|слабо растёт/);
});
test('old observation is marked stale even after a fresh hass update',async()=>{
  const e=environment();e.hass.states['sensor.custom_observation_time'].state=new Date(Date.now()-4*3600000).toISOString();
  const card=e.make();await flush();assert.match(summary(card),/Устаревшие данные/);
});
test('missing and future timestamps are not marked fresh',async()=>{
  for(const time of ['unknown','invalid',new Date(Date.now()+3600000).toISOString()]){
    const e=environment();e.hass.states['sensor.custom_observation_time'].state=time;
    const card=e.make();await flush();assert.match(summary(card),/Время наблюдения неизвестно/);assert.doesNotMatch(summary(card),/<time /);
  }
});
test('unavailable observations never become zero or fresh',async()=>{
  const e=environment();for(const [id,state]of Object.entries(e.hass.states))if(!id.endsWith('station'))state.state='unavailable';
  const card=e.make();await flush();assert.match(summary(card),/class="value">—<\/span>/);assert.match(summary(card),/status off/);assert.doesNotMatch(summary(card),/Свежие данные/);
});
test('real zero, negative temperatures and chosen units are preserved',async()=>{
  const e=environment(),card=e.make();await flush();
  for(const [state,value]of [['0','0'],['-12.5','-12,5']]){
    Object.assign(e.hass.states['sensor.custom_temperature'],{state,attributes:{unit_of_measurement:'°F'}});card.hass={...e.hass};
    assert.match(summary(card),new RegExp('class="value">'+value+'<'));assert.match(summary(card),/class="unit">°F</);
  }
});
test('optional sensors only appear with available readings',async()=>{
  const e=environment(),card=e.make();await flush();assert.doesNotMatch(summary(card),/Влажность/);
  e.hass.states['sensor.humidity']={state:'81',attributes:{unit_of_measurement:'%'}};
  card.setConfig({station:'BY_26850',entities:{humidity:'sensor.humidity'}});assert.match(summary(card),/Влажность/);assert.match(summary(card),/81 %/);
  e.hass.states['sensor.humidity'].state='unavailable';card.hass={...e.hass};assert.doesNotMatch(summary(card),/Влажность/);
});
test('all data and titles are HTML escaped',async()=>{
  const e=environment();e.hass.states['sensor.custom_condition'].state='<img src=x onerror=alert(1)>';
  const card=e.make({name:'<b>Title</b>'});await flush();
  assert.match(summary(card),/&lt;b&gt;Title&lt;\/b&gt;/);assert.match(summary(card),/&lt;img/);assert.doesNotMatch(summary(card),/<img|<h2><b>/);
});
test('explicit mapping works if registry access fails',async()=>{
  const e=environment({rejectRegistry:true});const card=e.make({station:undefined,name:'Manual',entities:{temperature:'sensor.custom_temperature'}});await flush();
  assert.match(summary(card),/class="value">7,4</);assert.match(summary(card),/<h2>Manual</);assert.equal(card._registryError,true);
});
test('disabled and missing entities are not displayed as measurements',async()=>{
  const e=environment();e.entries.find(x=>x.unique_id.endsWith('_temperature')).disabled_by='user';
  const card=e.make();await flush();assert.match(summary(card),/class="value">—</);assert.equal(card._graph,undefined);
});
test('graph is built once and receives configured duration',async()=>{
  const e=environment(),card=e.make({hours_to_show:48});await flush();const graph=card._graph;
  assert.equal(graph.config.hours_to_show,48);card.hass={...e.hass};assert.equal(card._graph,graph);
});
test('late graph initialization cannot restore a disabled graph',async()=>{
  let release;const e=environment({helper:()=>new Promise(r=>{release=r})}),card=e.make();await flush();
  card.setConfig({station:'BY_26850',show_graph:false});release({createCardElement(){throw new Error('Must not run')}});await flush();
  assert.equal(card._graph,undefined);assert.equal(card.shadowRoot.querySelector('.history').children.length,0);
});
test('history errors do not remove observations',async()=>{
  const e=environment({helper:async()=>{throw new Error('History failed')}}),card=e.make();await flush();
  assert.match(summary(card),/7,4/);assert.match(card.shadowRoot.querySelector('.history').innerHTML,/Не удалось загрузить историю/);
});
test('five UI languages render; unsupported HA locale falls back to English',async()=>{
  const e=environment(),card=e.make();await flush();
  for(const [language,label]of Object.entries({ru:'Свежие данные',be:'Свежыя даныя',pl:'Aktualne dane',en:'Recent observation',de:'Aktuelle Beobachtung'})){
    card.setConfig({station:'BY_26850',language,show_graph:false});assert.ok(summary(card).includes(label));
  }
  e.hass.locale.language='fr';card.setConfig({station:'BY_26850',show_graph:false});assert.match(summary(card),/Recent observation/);
});
test('visual editor emits changes and retains standard Lovelace settings',async()=>{
  const e=environment(),Editor=e.definitions.get('pogoda-by-card-editor'),editor=new Editor();
  editor.setConfig({station:'BY_26850',grid_options:{columns:12},visibility:[{condition:'user',users:['demo']}]});editor.hass=e.hass;await flush();
  assert.match(editor.shadowRoot.innerHTML,/<option value="BY_26850" selected>Минск/);
  editor.shadowRoot.querySelector('.form').listeners.change({target:{dataset:{key:'show_graph'},type:'checkbox',checked:false,reportValidity:()=>true}});
  const config=editor.lastEvent.detail.config;assert.equal(editor.lastEvent.type,'config-changed');assert.equal(config.show_graph,false);assert.equal(config.grid_options.columns,12);assert.equal(config.visibility[0].condition,'user');
});
test('bad ranges, booleans and entity mappings are rejected',()=>{
  const e=environment();for(const config of [{hours_to_show:0},{hours_to_show:1.5},{stale_after:0},{show_graph:'false'},{language:'invalid'},{entities:{temperature:'light.demo'}},{station:'<script>'}])assert.throws(()=>e.make(config));
});

test('full view remains the default with optional readings and history',async()=>{
  const e=environment();e.hass.states['sensor.humidity']={state:'81',attributes:{unit_of_measurement:'%'}};
  const card=e.make({entities:{humidity:'sensor.humidity'}});await flush();
  assert.equal(card._config.compact,false);assert.match(summary(card),/class="hero"/);
  assert.match(summary(card),/Влажность/);assert.ok(card._graph);
  assert.equal(card.getGridOptions().columns,12);assert.equal(card.getCardSize(),11);
});
test('compact view has its own layout and no history or optional readings',async()=>{
  const e=environment();e.hass.states['sensor.humidity']={state:'81',attributes:{unit_of_measurement:'%'}};
  const card=e.make({compact:true,show_graph:true,entities:{humidity:'sensor.humidity'}});await flush();
  const html=summary(card);assert.match(html,/class="compact-layout"/);
  assert.match(html,/Минск/);assert.match(html,/Переменная облачность/);assert.match(html,/>7,4</);
  assert.match(html,/data-entity="sensor.custom_temperature"/);assert.match(html,/data-entity="sensor.custom_wind_speed"/);
  assert.match(html,/data-entity="sensor.custom_pressure"/);assert.match(html,/<time /);
  assert.doesNotMatch(html,/class="hero"|Влажность|sensor.humidity/);
  assert.equal(card._graph,undefined);assert.equal(card.shadowRoot.querySelector('.history').children.length,0);
  assert.equal(card.getGridOptions().columns,6);assert.equal(card.getCardSize(),3);
});
test('switching views restores graph settings and uses current readings',async()=>{
  const e=environment(),card=e.make({hours_to_show:48});await flush();
  card.setConfig({station:'BY_26850',hours_to_show:48,compact:true});await flush();
  assert.equal(card._graph,undefined);
  e.hass.states['sensor.custom_temperature'].state='0';card.hass={...e.hass};
  assert.match(summary(card),/class="value">0</);
  card.setConfig({station:'BY_26850',hours_to_show:48,compact:false});await flush();
  assert.match(summary(card),/class="hero"/);assert.match(summary(card),/class="value">0</);
  assert.equal(card._graph.config.hours_to_show,48);
});
test('compact view respects hidden measurements and observation time',async()=>{
  const e=environment(),card=e.make({compact:true,show_details:false,show_observation:false});await flush();
  assert.doesNotMatch(summary(card),/class="compact-metrics"|class="compact-observed"|<time /);
  assert.match(summary(card),/Свежие данные/);assert.match(summary(card),/Pogoda.by ↗/);
});
test('compact view keeps stale, unknown and unavailable states explicit',async()=>{
  const e=environment(),card=e.make({compact:true});await flush();
  e.hass.states['sensor.custom_observation_time'].state=new Date(Date.now()-4*3600000).toISOString();card.hass={...e.hass};
  assert.match(summary(card),/Устаревшие данные/);
  e.hass.states['sensor.custom_observation_time'].state='unknown';card.hass={...e.hass};
  assert.match(summary(card),/Время наблюдения неизвестно/);assert.doesNotMatch(summary(card),/<time /);
  for(const field of ['temperature','condition','wind_speed','pressure'])e.hass.states['sensor.custom_'+field].state='unavailable';
  card.hass={...e.hass};assert.match(summary(card),/status off/);assert.match(summary(card),/class="value">—</);
  assert.doesNotMatch(summary(card),/Свежие данные/);
});
test('switching to compact cancels pending history creation',async()=>{
  let release;const e=environment({helper:()=>new Promise(r=>{release=r})}),card=e.make();await flush();
  card.setConfig({station:'BY_26850',compact:true});
  release({createCardElement(){throw new Error('Must not run in compact view')}});await flush();
  assert.equal(card._graph,undefined);assert.equal(card.shadowRoot.querySelector('.history').children.length,0);
  assert.match(summary(card),/compact-layout/);
});
test('view selector emits booleans and preserves full-view settings',async()=>{
  const e=environment(),Editor=e.definitions.get('pogoda-by-card-editor'),editor=new Editor();
  editor.setConfig({station:'BY_26850',show_graph:true,hours_to_show:48,grid_options:{columns:12}});editor.hass=e.hass;await flush();
  assert.match(editor.shadowRoot.innerHTML,/<select data-key="compact">/);assert.match(editor.shadowRoot.innerHTML,/Полный вид/);
  editor.shadowRoot.querySelector('.form').listeners.change({target:{dataset:{key:'compact'},type:'select-one',value:'true',reportValidity:()=>true}});
  let config=editor.lastEvent.detail.config;assert.equal(config.compact,true);assert.equal(config.show_graph,true);
  assert.equal(config.hours_to_show,48);assert.equal(config.grid_options.columns,12);
  assert.match(editor.shadowRoot.innerHTML,/data-key="show_graph"[^>]*disabled/);
  assert.match(editor.shadowRoot.innerHTML,/data-key="hours_to_show"[^>]*disabled/);
  editor.shadowRoot.querySelector('.form').listeners.change({target:{dataset:{key:'compact'},type:'select-one',value:'false',reportValidity:()=>true}});
  config=editor.lastEvent.detail.config;assert.equal(config.compact,false);assert.equal(config.show_graph,true);assert.equal(config.hours_to_show,48);
  assert.doesNotMatch(editor.shadowRoot.innerHTML,/data-key="show_graph"[^>]*disabled/);
});
test('compact view escapes titles, descriptions and metric tooltips',async()=>{
  const e=environment();e.hass.states['sensor.custom_condition'].state='" onmouseover="alert(1)<img>';
  e.hass.states['sensor.custom_wind_direction'].state='<script>alert(1)</script>';
  const card=e.make({compact:true,name:'<b>Title</b>'});await flush();
  const html=summary(card);assert.match(html,/&lt;b&gt;Title&lt;\/b&gt;/);assert.match(html,/&quot; onmouseover=&quot;/);
  assert.doesNotMatch(html,/<img|<script|<h2[^>]*><b>/);
});

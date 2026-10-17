/* WorldPulse — static GitHub Pages viewer. The scheduled workflow owns data updates. */
'use strict';
const COLORS={politics:'#eeb67e',environment:'#6edcb3',hazards:'#ef797d',society:'#ae94f3',health:'#d3a1ff',education:'#a8a3ff',rights:'#ef9bd0',community:'#bb95dd',economy:'#72baf1',science:'#e4d475',conflict:'#ff5878',social:'#eb8eeb'};
const LABELS={politics:'Politics',environment:'Environment',hazards:'Hazards',health:'Health',education:'Education',rights:'Rights & justice',community:'Community & culture',society:'Society (legacy)',economy:'Economy',science:'Science',conflict:'War & conflict'};
const $=id=>document.getElementById(id);
const state={news:[],posts:[],events:[],layer:'news',categories:new Set(Object.keys(LABELS)),cluster:true,precision:'all',rotate:true,translate:true,selected:null,translator:null,language:navigator.language||'en',feed:null,coverage:false,countries:[],countryStats:new Map(),coverageReady:false,visualMode:localStorage.getItem("worldpulse-globe-mode")==="real"?"real":"neon",twinkle:true};
let globe, currentPoints=[], lastTier=-1, translationCache=new Map();
const REAL_EARTH='https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg';

const POP_HUBS=[
 {name:'Tokyo',lat:35.68,lng:139.69,pop:37.4},{name:'Delhi',lat:28.61,lng:77.21,pop:32.1},{name:'Shanghai',lat:31.23,lng:121.47,pop:29.9},
 {name:'Dhaka',lat:23.81,lng:90.41,pop:23.9},{name:'Sao Paulo',lat:-23.55,lng:-46.63,pop:22.6},{name:'Mexico City',lat:19.43,lng:-99.13,pop:22.3},
 {name:'Cairo',lat:30.04,lng:31.24,pop:22.0},{name:'Beijing',lat:39.90,lng:116.40,pop:21.8},{name:'Mumbai',lat:19.08,lng:72.88,pop:21.3},
 {name:'Osaka',lat:34.69,lng:135.50,pop:19.0},{name:'Chongqing',lat:29.56,lng:106.55,pop:18.6},{name:'Karachi',lat:24.86,lng:67.01,pop:17.6},
 {name:'Istanbul',lat:41.01,lng:28.98,pop:16.0},{name:'Buenos Aires',lat:-34.60,lng:-58.38,pop:15.6},{name:'Kolkata',lat:22.57,lng:88.36,pop:15.3},
 {name:'Lagos',lat:6.52,lng:3.37,pop:15.2},{name:'Kinshasa',lat:-4.33,lng:15.31,pop:15.0},{name:'Manila',lat:14.60,lng:120.98,pop:14.9},
 {name:'Tianjin',lat:39.13,lng:117.20,pop:14.7},{name:'Rio de Janeiro',lat:-22.91,lng:-43.17,pop:13.6},{name:'Guangzhou',lat:23.13,lng:113.26,pop:13.6},
 {name:'Lahore',lat:31.55,lng:74.34,pop:13.5},{name:'Bangalore',lat:12.97,lng:77.59,pop:13.2},{name:'Paris',lat:48.86,lng:2.35,pop:11.2},
 {name:'Shenzhen',lat:22.54,lng:114.06,pop:12.6},{name:'Jakarta',lat:-6.21,lng:106.85,pop:11.4},{name:'Moscow',lat:55.76,lng:37.62,pop:12.5},
 {name:'Chennai',lat:13.08,lng:80.27,pop:11.1},{name:'Lima',lat:-12.05,lng:-77.04,pop:11.0},{name:'Bogota',lat:4.71,lng:-74.07,pop:11.0},
 {name:'Seoul',lat:37.57,lng:126.98,pop:9.9},{name:'London',lat:51.51,lng:-0.13,pop:9.6},{name:'Tehran',lat:35.69,lng:51.39,pop:9.5},
 {name:'Bangkok',lat:13.76,lng:100.50,pop:10.7},{name:'Hong Kong',lat:22.32,lng:114.17,pop:7.5},{name:'Wuhan',lat:30.59,lng:114.30,pop:10.0},
 {name:'Chengdu',lat:30.66,lng:104.06,pop:9.5},{name:'Ho Chi Minh City',lat:10.82,lng:106.63,pop:9.0},{name:'Hyderabad',lat:17.39,lng:78.49,pop:9.7},
 {name:'Ahmedabad',lat:23.03,lng:72.58,pop:8.7},{name:'Singapore',lat:1.35,lng:103.82,pop:5.9},{name:'Santiago',lat:-33.45,lng:-70.67,pop:6.8},
 {name:'Toronto',lat:43.65,lng:-79.38,pop:6.7},{name:'Johannesburg',lat:-26.20,lng:28.04,pop:6.2},{name:'Nairobi',lat:-1.29,lng:36.82,pop:5.3},
 {name:'Khartoum',lat:15.50,lng:32.56,pop:6.3},{name:'Casablanca',lat:33.57,lng:-7.59,pop:4.0},{name:'Algiers',lat:36.75,lng:3.06,pop:4.2},
 {name:'Baghdad',lat:33.31,lng:44.36,pop:7.6},{name:'Riyadh',lat:24.71,lng:46.67,pop:7.7},{name:'Jeddah',lat:21.49,lng:39.19,pop:4.7},
 {name:'Dubai',lat:25.20,lng:55.27,pop:3.6},{name:'Doha',lat:25.29,lng:51.53,pop:2.5},{name:'Kuwait City',lat:29.37,lng:47.98,pop:3.2},
 {name:'Tel Aviv',lat:32.09,lng:34.78,pop:4.2},{name:'Athens',lat:37.98,lng:23.73,pop:3.1},{name:'Rome',lat:41.90,lng:12.50,pop:4.2},
 {name:'Milan',lat:45.46,lng:9.19,pop:4.3},{name:'Madrid',lat:40.42,lng:-3.70,pop:6.7},{name:'Barcelona',lat:41.39,lng:2.17,pop:5.5},
 {name:'Berlin',lat:52.52,lng:13.40,pop:3.7},{name:'Hamburg',lat:53.55,lng:10.00,pop:1.8},{name:'Munich',lat:48.14,lng:11.58,pop:1.5},
 {name:'Warsaw',lat:52.23,lng:21.01,pop:1.9},{name:'Kyiv',lat:50.45,lng:30.52,pop:3.0},{name:'Bucharest',lat:44.43,lng:26.10,pop:2.1},
 {name:'Budapest',lat:47.50,lng:19.04,pop:1.8},{name:'Vienna',lat:48.21,lng:16.37,pop:1.9},{name:'Amsterdam',lat:52.37,lng:4.90,pop:2.5},
 {name:'Brussels',lat:50.85,lng:4.35,pop:2.1},{name:'Copenhagen',lat:55.68,lng:12.57,pop:1.4},{name:'Stockholm',lat:59.33,lng:18.07,pop:1.7},
 {name:'Oslo',lat:59.91,lng:10.75,pop:1.1},{name:'Helsinki',lat:60.17,lng:24.94,pop:1.3},{name:'Dublin',lat:53.35,lng:-6.26,pop:1.4},
 {name:'Lisbon',lat:38.72,lng:-9.14,pop:2.8},{name:'Prague',lat:50.08,lng:14.43,pop:1.3},{name:'Zurich',lat:47.38,lng:8.54,pop:1.4},
 {name:'New York',lat:40.71,lng:-74.01,pop:19.5},{name:'Boston',lat:42.36,lng:-71.06,pop:4.9},{name:'Washington DC',lat:38.90,lng:-77.04,pop:6.4},
 {name:'Philadelphia',lat:39.95,lng:-75.17,pop:5.7},{name:'Atlanta',lat:33.75,lng:-84.39,pop:6.1},{name:'Miami',lat:25.76,lng:-80.19,pop:6.2},
 {name:'Chicago',lat:41.88,lng:-87.63,pop:8.8},{name:'Detroit',lat:42.33,lng:-83.05,pop:4.3},{name:'Dallas',lat:32.78,lng:-96.80,pop:7.8},
 {name:'Houston',lat:29.76,lng:-95.37,pop:7.3},{name:'Phoenix',lat:33.45,lng:-112.07,pop:4.9},{name:'Denver',lat:39.74,lng:-104.99,pop:3.0},
 {name:'Seattle',lat:47.61,lng:-122.33,pop:4.0},{name:'San Francisco',lat:37.77,lng:-122.42,pop:4.6},{name:'Los Angeles',lat:34.05,lng:-118.24,pop:12.8},
 {name:'San Diego',lat:32.72,lng:-117.16,pop:3.3},{name:'Las Vegas',lat:36.17,lng:-115.14,pop:2.9},{name:'Minneapolis',lat:44.98,lng:-93.27,pop:3.7},
 {name:'St Louis',lat:38.63,lng:-90.20,pop:2.8},{name:'Mexico Monterrey',lat:25.69,lng:-100.32,pop:5.3},{name:'Guadalajara',lat:20.67,lng:-103.35,pop:5.3},
 {name:'Vancouver',lat:49.28,lng:-123.12,pop:2.7},{name:'Montreal',lat:45.50,lng:-73.57,pop:4.1},{name:'Ottawa',lat:45.42,lng:-75.69,pop:1.4},
 {name:'Calgary',lat:51.05,lng:-114.07,pop:1.6},{name:'Edmonton',lat:53.55,lng:-113.49,pop:1.5},{name:'Winnipeg',lat:49.90,lng:-97.14,pop:0.8},
 {name:'Havana',lat:23.11,lng:-82.37,pop:2.1},{name:'Santo Domingo',lat:18.49,lng:-69.99,pop:3.3},{name:'San Juan',lat:18.47,lng:-66.11,pop:2.3},
 {name:'Panama City',lat:8.98,lng:-79.52,pop:2.0},{name:'San Jose',lat:9.93,lng:-84.08,pop:2.4},{name:'Guatemala City',lat:14.63,lng:-90.55,pop:3.0},
 {name:'Quito',lat:-0.18,lng:-78.47,pop:2.8},{name:'Guayaquil',lat:-2.17,lng:-79.92,pop:3.0},{name:'Caracas',lat:10.48,lng:-66.90,pop:3.0},
 {name:'Medellin',lat:6.24,lng:-75.58,pop:4.1},{name:'La Paz',lat:-16.50,lng:-68.15,pop:2.0},{name:'Santa Cruz',lat:-17.78,lng:-63.18,pop:2.2},
 {name:'Asuncion',lat:-25.27,lng:-57.64,pop:2.2},{name:'Montevideo',lat:-34.90,lng:-56.16,pop:1.7},{name:'Cordoba',lat:-31.42,lng:-64.18,pop:1.6},
 {name:'Perth',lat:-31.95,lng:115.86,pop:2.2},{name:'Adelaide',lat:-34.93,lng:138.60,pop:1.4},{name:'Melbourne',lat:-37.81,lng:144.96,pop:5.2},
 {name:'Sydney',lat:-33.87,lng:151.21,pop:5.3},{name:'Brisbane',lat:-27.47,lng:153.03,pop:2.6},{name:'Auckland',lat:-36.85,lng:174.76,pop:1.7},
 {name:'Wellington',lat:-41.29,lng:174.78,pop:0.5},{name:'Christchurch',lat:-43.53,lng:172.63,pop:0.4},{name:'Port Moresby',lat:-9.44,lng:147.18,pop:0.4},
 {name:'Honolulu',lat:21.31,lng:-157.86,pop:1.0},{name:'Anchorage',lat:61.22,lng:-149.90,pop:0.4},{name:'Reykjavik',lat:64.15,lng:-21.94,pop:0.2},
 {name:'Addis Ababa',lat:8.98,lng:38.79,pop:5.6},{name:'Dar es Salaam',lat:-6.79,lng:39.21,pop:7.0},{name:'Kampala',lat:0.35,lng:32.58,pop:4.0},
 {name:'Kigali',lat:-1.95,lng:30.06,pop:1.2},{name:'Lusaka',lat:-15.39,lng:28.32,pop:3.0},{name:'Harare',lat:-17.82,lng:31.05,pop:2.1},
 {name:'Maputo',lat:-25.97,lng:32.58,pop:1.8},{name:'Luanda',lat:-8.84,lng:13.23,pop:9.0},{name:'Abidjan',lat:5.36,lng:-4.01,pop:6.3},
 {name:'Accra',lat:5.56,lng:-0.20,pop:5.5},{name:'Dakar',lat:14.69,lng:-17.45,pop:3.8},{name:'Bamako',lat:12.64,lng:-8.00,pop:2.8},
 {name:'Lome',lat:6.13,lng:1.22,pop:2.2},{name:'Cotonou',lat:6.37,lng:2.43,pop:2.4},{name:'Yaounde',lat:3.85,lng:11.50,pop:3.0},
 {name:'Douala',lat:4.05,lng:9.70,pop:3.7},{name:'Rabat',lat:34.02,lng:-6.84,pop:2.0},{name:'Tunis',lat:36.81,lng:10.18,pop:2.7},
 {name:'Antananarivo',lat:-18.91,lng:47.54,pop:3.4},{name:'Kathmandu',lat:27.72,lng:85.32,pop:3.0},{name:'Colombo',lat:6.93,lng:79.86,pop:5.6},
 {name:'Yangon',lat:16.86,lng:96.20,pop:5.4},{name:'Hanoi',lat:21.03,lng:105.85,pop:8.0},{name:'Phnom Penh',lat:11.56,lng:104.93,pop:2.3},
 {name:'Vientiane',lat:17.98,lng:102.63,pop:1.0},{name:'Kuala Lumpur',lat:3.14,lng:101.69,pop:8.8},{name:'Taipei',lat:25.03,lng:121.56,pop:7.0},
 {name:'Fukuoka',lat:33.59,lng:130.40,pop:2.6},{name:'Sapporo',lat:43.06,lng:141.35,pop:2.0},{name:'Novosibirsk',lat:55.03,lng:82.92,pop:1.7},
 {name:'Yekaterinburg',lat:56.84,lng:60.61,pop:1.6},{name:'Almaty',lat:43.24,lng:76.92,pop:2.1},{name:'Tashkent',lat:41.31,lng:69.28,pop:2.7}
].map(h=>({...h,weight:Math.sqrt(h.pop)}));
function wrapLngDelta(a,b){let d=Math.abs(a-b)%360;return d>180?360-d:d}
function ambientSettlementDensity(lat,lng){
 let score=0;
 const cosLat=Math.max(.28,Math.cos(lat*Math.PI/180));
 for(const h of POP_HUBS){
  const dLat=lat-h.lat;
  const dLng=wrapLngDelta(lng,h.lng)*cosLat;
  const d2=dLat*dLat+dLng*dLng;
  if(d2>2200)continue;
  score += (h.weight*0.9)*Math.exp(-d2/140) + (h.weight*0.35)*Math.exp(-d2/900);
 }
 return Math.min(1,score/7.8);
}

let neonTextureUrl=null,twinkleFrame=0;
let measuredPopulationImage=null, measuredPopulationStatus='not-loaded';

let permanentBorders=[]; // Cartographic geometry, completely independent of news data
let bordersLoading=false; // MUST initialize before bind() calls initCoverageControls()
function clean(s){return String(s??'').slice(0,500)}
function dist(a,b){let rad=Math.PI/180,dLat=(b.lat-a.lat)*rad,dLng=(b.lng-a.lng)*rad;let x=Math.sin(dLat/2)**2+Math.cos(a.lat*rad)*Math.cos(b.lat*rad)*Math.sin(dLng/2)**2;return 6371*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x))}
function age(ts){if(!ts)return 'not yet updated';let m=Math.floor((Date.now()-new Date(ts).getTime())/60000);if(!Number.isFinite(m))return 'unknown';if(m<0)return 'just updated';if(m<60)return `${m} minutes ago`;return `${Math.floor(m/60)} hours ago`}
function initGlobe(){
 if(typeof Globe==='undefined'){$('emptyNotice').hidden=false;$('emptyNotice').textContent='The 3D globe could not load. Check your internet connection or browser WebGL support.';return;}
 globe=Globe()($('globe'))
  .globeImageUrl(state.visualMode==='neon'?makeNeonTexture():REAL_EARTH)
  .bumpImageUrl(null)
  .backgroundColor('rgba(0,0,0,0)')
  .showAtmosphere(true).atmosphereColor(state.visualMode==='neon'?'#00e7ee':'#4baec0').atmosphereAltitude(state.visualMode==='neon'?.095:.14)
  .pointsMerge(false).pointLat('lat').pointLng('lng')
  .pointColor(p=>signalColor(p))
  .pointAltitude(p=>signalAltitude(p))
  .pointRadius(p=>signalRadius(p))
  .pointLabel(p=>`${clean(p.name)} · ${p.count.toLocaleString()} ${state.layer==='news'?'sampled articles':state.layer==='events'?'recorded events':'posts'}${p.accuracy==='country'?' · COUNTRY-LEVEL SUBJECT (approximate)':p.accuracy==='region'?' · regional reference':''}${p.velocity==='rising'?' · ↑ Rising':''}`)
  .ringsData([])
  .polygonsData([]).polygonCapColor(p=>coverageColor(p.properties.wpCount||0))
  .polygonSideColor(()=>'rgba(22,68,85,0.05)').polygonStrokeColor(()=>'rgba(167,204,219,0.26)')
  .polygonAltitude(()=>.004)
  .polygonLabel(p=>`${clean(p.properties.name)}: ${p.properties.wpCount||0} sampled mapped articles (approximate)`)
  .onPolygonClick(p=>selectCoverageCountry(p))
  .onPointClick(p=>openPoint(p.signalSource||p))
  .onGlobeClick(({lat,lng})=>pickPlace({lat,lng}))
  .onZoom(()=>refreshZoom());
 globe.pointOfView({lat:17,lng:16,altitude:2.15},0);
 globe.controls().autoRotate=true;globe.controls().autoRotateSpeed=.27;
 globe.controls().enableDamping=true;globe.controls().minDistance=115;globe.controls().maxDistance=850;
 const resize=()=>{if(!globe)return;globe.width($('scene').clientWidth);globe.height($('scene').clientHeight)};
 new ResizeObserver(resize).observe($('scene'));resize();
}
function tier(){if(!globe)return 0;let alt=globe.pointOfView().altitude;return alt>1.4?0:alt>.72?1:alt>.30?2:3}
function aggregate(items){if(!state.cluster||tier()===3)return items.map(p=>({...p,members:[p]}));
 let size=[19,9,4.5,1.5][tier()];let groups=new Map();
 for(let p of items){let x=Math.floor((p.lng+180)/size),y=Math.floor((p.lat+90)/size);let key=`${p.category}_${x}_${y}`;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p)}
 return [...groups.values()].map(members=>{
  if(members.length===1)return {...members[0],members};
  const count=members.reduce((n,p)=>n+p.count,0);
  let lat=members.reduce((n,p)=>n+p.lat*p.count,0)/Math.max(count,1);
  let ss=members.reduce((n,p)=>n+Math.sin(p.lng*Math.PI/180)*p.count,0),cc=members.reduce((n,p)=>n+Math.cos(p.lng*Math.PI/180)*p.count,0);
  let lng=Math.atan2(ss,cc)*180/Math.PI;
  const winner=[...members].sort((a,b)=>b.count-a.count)[0];
  return {lat,lng,count,category:winner.category,name:`${members.length} nearby signals`,velocity:members.some(p=>p.velocity==='rising')?'rising':'steady',members};
 });
}
function refreshZoom(){let t=tier();if(t!==lastTier){lastTier=t;renderPoints()}}
function renderPoints(){if(!globe)return;let data=state.layer==='news'?state.news.filter(p=>state.categories.has(p.category)):state.layer==='events'?(state.categories.has('hazards')?state.events:[]):state.posts;
 if(state.layer==='news'&&state.precision!=='all')data=data.filter(p=>p.accuracy===state.precision);
 // Country-level subjects remain small selectable anchors; never imply an event footprint.
 // All perpetual pulse rings are disabled: they were country-only and caused clutter.
 const mapped=state.layer==='news'?data.map(p=>p.accuracy==='country'?{...p,broadAnchor:true}:p):data;
 currentPoints=aggregate(mapped);globe.pointsData(signalDisplayPoints(currentPoints));refreshSignalGlow();refreshMarkerHalos();renderCoverage();
 $('locations').textContent=data.length.toLocaleString();$('total').textContent=data.reduce((n,p)=>n+p.count,0).toLocaleString();
}
function pickPlace(pos){let source=state.layer==='news'?state.news.filter(p=>state.categories.has(p.category)):state.layer==='events'?(state.categories.has('hazards')?state.events:[]):state.posts;
 if(state.layer==='news'&&state.precision!=='all')source=source.filter(p=>p.accuracy===state.precision);
 if(!source.length){openEmpty(pos);return}
 const nearest=[...source].sort((a,b)=>dist(pos,a)-dist(pos,b))[0];
 const km=dist(pos,nearest);
 if(km>450){openEmpty(pos);return}
 openPoint({...nearest,name:`Near ${nearest.name}`,distance:Math.round(km),members:[nearest]});
}
function openEmpty(pos){state.selected={lat:pos.lat,lng:pos.lng,count:0,members:[],name:`${pos.lat.toFixed(2)}°, ${pos.lng.toFixed(2)}°`};paintDrawer()}
function openPoint(p){state.selected=p;paintDrawer();if(globe){globe.controls().autoRotate=false;globe.pointOfView({lat:p.lat,lng:p.lng,altitude:Math.max(.48,globe.pointOfView().altitude*.84)},700)}}
function el(tag,text,cls){let e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
async function getTranslator(){let target=state.language.split('-')[0].toLowerCase();if(!state.translate||target==='en')return null;
 if(state.translator)return state.translator;
 try{if(!('Translator' in self))return null;let r=await self.Translator.availability({sourceLanguage:'en',targetLanguage:target});if(r==='unavailable')return null;state.translator=await self.Translator.create({sourceLanguage:'en',targetLanguage:target});return state.translator}catch{return null}
}
async function maybeTranslate(node,original){if(!state.translate)return;let key=state.language+'|'+original;let cached=translationCache.get(key);if(cached){node.textContent=cached;return}
 let t=await getTranslator();if(!t||!node.isConnected)return;
 try{let translated=await t.translate(original);if(translated){translationCache.set(key,translated);if(node.isConnected&&state.translate)node.textContent=translated}}catch{}
}
function paintDrawer(){const p=state.selected;if(!p)return; $('drawer').hidden=false;$('drawer-title').textContent=p.name;
 let members=p.members||[p];const total=members.reduce((n,x)=>n+x.count,0);let rising=members.filter(x=>x.velocity==='rising').length;let countries=members.some(x=>x.accuracy==='country');$('drawer-meta').textContent=`${total.toLocaleString()} ${state.layer==='news'?'deduplicated sampled articles':state.layer==='events'?'officially reported earthquake events':'posts'} · ${members.length} signals${rising?' · ↑ '+rising+' rising':''}${countries?' · Country pins are approximate':''}${members.some(x=>x.location_basis==='description')?' · Some locations from descriptions':''}${p.distance!=null?' · nearest signal '+p.distance+' km away':''}`;
 let area=$('drawer-stories');area.replaceChildren();
 const stories=new Map();for(let m of [...members].sort((a,b)=>b.count-a.count))for(let a of (m.articles||[])){if(a.url&&/^https?:\/\//.test(a.url)&&!stories.has(a.url))stories.set(a.url,{...a,category:m.category,place:m.name})}
 if(!stories.size){area.append(el('p',state.layer==='news'?'No article links available for this location in the current snapshot. Zoom out or select another signal.':state.layer==='events'?'No official event links available here.':'No location-verified social posts are available here.'));return}
 for(let s of [...stories.values()].slice(0,30)){
  let row=el('div',undefined,'story'),anchor=el('a',clean(s.title));anchor.href=s.url;anchor.target='_blank';anchor.rel='noopener noreferrer';row.append(anchor);
  let source='';try{source=new URL(s.url).hostname.replace(/^www\./,'')}catch{}
  row.append(el('small',`${s.publisher||source} · ${s.place} · ${LABELS[s.category]||'Social'}${s.published_at?' · '+age(s.published_at):''} ↗`));area.append(row);maybeTranslate(anchor,clean(s.title));
 }
 if(stories.size>30)area.append(el('p',`Showing 30 of ${stories.size} example links.`));
}
function updateStatus(){let d=state.feed||{};let st=d.status;let dot=$('status');dot.classList.toggle('live',st==='live');
 dot.lastChild.textContent=st==='live'?' Updated feed':st==='partial'?' Partial feed':st==='stale'?' Outdated feed':' Awaiting feed';
 $('updated').textContent=`Feed: ${age(d.updated_at)} · ${d.query_successes||'?'} / ${d.query_attempts||'?'} feeds · ${d.duplicates_removed||0} duplicates removed`; if($('sourceBreakdown'))$('sourceBreakdown').textContent=`${d.direct_sources_ok??0} direct feeds responding · ${d.source_count??0} source names in sample · 30-day summary stored`; 
 let notice=$('emptyNotice');notice.hidden=true;
 if(!state.news.length){notice.hidden=false;notice.textContent='No news snapshot yet. On GitHub, run Actions → Refresh geographic news → Run workflow, then reload this page.'}
 else if(st!=='live'){notice.hidden=false;notice.textContent=st==='partial'?'Some categories failed to refresh. Older category results may be shown.':'News is from the last successful update, not live.'}
}
async function loadData(){try{let r=await fetch('data/news.json?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('News HTTP '+r.status);let data=await r.json();state.feed=data;state.news=(data.points||[]).filter(p=>Number.isFinite(p.lat)&&Number.isFinite(p.lng)&&Number.isFinite(p.count)&&p.count>=0&&LABELS[p.category]);updateStatus();renderPoints()}
 catch(e){$('emptyNotice').hidden=false;$('emptyNotice').textContent='Could not load news data: '+e.message}
 try{let r=await fetch('data/social.json?t='+Date.now(),{cache:'no-store'});let d=await r.json();state.posts=(d.posts||[]).filter(p=>Number.isFinite(p.lat)&&Number.isFinite(p.lng)&&Array.isArray(p.articles)&&p.verified_location===true).map(p=>({...p,count:1,category:'social'}))}catch{}
}
async function loadEvents(){
 try{
  let r=await fetch('data/events.json?t='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('Event feed HTTP '+r.status);
  let d=await r.json();state.events=(d.events||[]).filter(e=>Number.isFinite(e.lat)&&Number.isFinite(e.lng)&&e.url?.startsWith('https://earthquake.usgs.gov/')).map(e=>({lat:e.lat,lng:e.lng,count:1,category:'hazards',name:e.name,accuracy:'observed coordinates',velocity:'steady',articles:[{title:e.title+(typeof e.magnitude==='number'?' · M'+e.magnitude.toFixed(1):''),url:e.url,publisher:'USGS',published_at:e.published_at}],location_basis:'observed_event_coordinates'}));
  if(state.layer==='events')renderPoints();
 }catch(err){console.warn('Optional events overlay unavailable:',err.message)}
}
function bind(){
 for(let [key,label] of Object.entries(LABELS)){let btn=el('button',undefined,'filter on');btn.type='button';btn.dataset.cat=key;let sw=el('span',undefined,'swatch');sw.style.background=COLORS[key];sw.style.color=COLORS[key];btn.append(sw,el('span',label));btn.addEventListener('click',()=>{if(state.categories.has(key))state.categories.delete(key);else state.categories.add(key);btn.classList.toggle('on',state.categories.has(key));renderPoints()});$('filters').append(btn)}
 $('allBtn').onclick=()=>{let all=state.categories.size!==Object.keys(LABELS).length;state.categories=all?new Set(Object.keys(LABELS)):new Set();document.querySelectorAll('.filter').forEach(b=>b.classList.toggle('on',all));renderPoints()};
 document.querySelectorAll('[data-layer]').forEach(b=>b.addEventListener('click',()=>{state.layer=b.dataset.layer;document.querySelectorAll('[data-layer]').forEach(x=>x.classList.toggle('active',x===b));$('socialExplain').hidden=state.layer!=='social';$('drawer').hidden=true;state.selected=null;renderPoints();if(state.layer==='events'&&!state.events.length){$('emptyNotice').hidden=false;$('emptyNotice').textContent='No recorded event snapshot available. The event adapter runs with the news workflow.'}else if(state.layer==='social'&&!state.posts.length){$('emptyNotice').hidden=false;$('emptyNotice').textContent='Social layer is ready for a verified-location feed. None is configured.'}else updateStatus()}));
 $('resetBtn').onclick=()=>{if(globe)globe.pointOfView({lat:17,lng:16,altitude:2.15},850);if(globe)globe.controls().autoRotate=state.rotate};
 $('rotate').onchange=e=>{state.rotate=e.target.checked;if(globe)globe.controls().autoRotate=state.rotate};
 $('clusters').onchange=e=>{state.cluster=e.target.checked;renderPoints()};
 $('precisionFilter').onchange=e=>{state.precision=e.target.value;renderPoints()};
 $('translate').onchange=e=>{state.translate=e.target.checked;if(state.selected)paintDrawer()};
 $('drawerClose').onclick=()=>{state.selected=null;$('drawer').hidden=true;if(globe)globe.controls().autoRotate=state.rotate};
 $('searchForm').onsubmit=e=>{e.preventDefault();let v=$('placeSearch').value.match(/^\s*(-?\d+(?:\.\d+)?)\s*[,; ]\s*(-?\d+(?:\.\d+)?)\s*$/);if(!v){$('placeSearch').setCustomValidity('Enter latitude,longitude, such as 35.68,139.69');$('placeSearch').reportValidity();return}let lat=+v[1],lng=+v[2];if(Math.abs(lat)>90||Math.abs(lng)>180){$('placeSearch').setCustomValidity('Coordinates out of range');$('placeSearch').reportValidity();return}$('placeSearch').setCustomValidity('');if(globe)globe.pointOfView({lat,lng,altitude:.75},1000);pickPlace({lat,lng})};
 $('placeSearch').oninput=()=>$('placeSearch').setCustomValidity('');
 $('aboutBtn').onclick=$('methodBtn').onclick=()=>{
  $('about').hidden=false;
  const body=$('about').querySelector('.modal-content');
  if(body&&!$('populationAttribution')){
   const note=el('p','Population brightness: where loaded, a preprocessed WorldPop 2020 1-km population-density model (CC BY 4.0) influences ambient cyan grid brightness, not news signals. If unavailable, the previous city-hub approximation is used. This is a historical population estimate, not a live feed.');
   note.id='populationAttribution';body.append(note);
  }
 };
 initCoverageControls();
 initVisualControls();
 $('healthBtn').onclick=()=>{ $('healthModal').hidden=false; showHealth(); };
 $('healthClose').onclick=()=>$('healthModal').hidden=true;
 $('aboutClose').onclick=()=>$('about').hidden=true;
 $('about').onclick=e=>{if(e.target===$('about'))$('about').hidden=true};
 $('healthModal').onclick=e=>{if(e.target===$('healthModal'))$('healthModal').hidden=true};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){$('about').hidden=true;$('healthModal').hidden=true;$('drawer').hidden=true}});
 function clock(){$('clock').textContent=new Intl.DateTimeFormat('en-GB',{timeZone:'UTC',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date())+' UTC'}clock();setInterval(clock,30000);
}
try{bind()}catch(error){console.error('WorldPulse control setup:',error)}
try{initGlobe()}catch(error){console.error('WorldPulse globe setup:',error);const n=$('emptyNotice');if(n){n.hidden=false;n.textContent='Globe setup error: '+error.message}}
loadData();loadEvents();setInterval(loadData,15*60*1000);

async function showHealth(){
 const host=$('healthContent');host.replaceChildren();
 try{
  const r=await fetch('data/data-health.json?t='+Date.now(),{cache:'no-store'});
  if(!r.ok)throw Error('HTTP '+r.status);
  const d=await r.json();
  if(!d.updated_at){host.textContent='Waiting for the first v1.4A.1 collector run.';return}
  const add=(k,v)=>{let row=el('p');let strong=el('strong',k+': ');row.append(strong,document.createTextNode(String(v)));host.append(row)};
  addHealthOverview(host,d);
  add('Latest update',d.updated_at);add('Successful feeds',`${d.feeds_ok} / ${d.feeds_total}`);add('Unmapped feed entries',d.unmapped_sample_count);add('Duplicates removed',d.duplicates_removed);
  add('Mapped category counts',Object.entries(d.mapped_articles_by_category||{}).map(([k,v])=>`${LABELS[k]||k} ${v}`).join(' · ')||'None');
  add('Place precision',Object.entries(d.mapped_articles_by_location_precision||{}).map(([k,v])=>`${k} ${v}`).join(' · ')||'None');
  add('Location evidence',Object.entries(d.location_evidence_counts||{}).map(([k,v])=>`${k} ${v}`).join(' · ')||'None');
  add('Gazetteer entries',d.gazetteer_entries??'Unknown');
  add('Distinct unmatched headlines',d.unmapped_distinct_titles??'Not available');
  add('Geographic quadrants (sampled records)',Object.entries(d.geographic_quadrants||{}).map(([k,v])=>`${k}: ${v}`).join(' · ')||'Not available');
  add('Most unmatched feeds',Object.entries(d.unmapped_by_feed||{}).slice(0,8).map(([k,v])=>`${k}: ${v}`).join(' · ')||'Not available');
  add('Independent publisher feeds', d.direct_source_breakdown ? `${d.direct_source_breakdown.successful}/${d.direct_source_breakdown.configured} successful · ${d.direct_source_breakdown.mapped_pre_dedupe} mapped before deduplication` : 'Awaiting new collection');
  add('Unmatched headline audit',d.unmapped_review_file ? `${d.unmapped_distinct_titles} distinct headlines · review data/unmatched-review.json` : 'Awaiting new collection');
  add('Google News regional editions',Object.entries(d.google_feeds_by_region||{}).map(([k,v])=>`${k}: ${v.ok}/${v.total} feeds · ${v.mapped_pre_dedupe} mapped before deduplication`).join(' · ')||'Awaiting new collection');
  add('Failed feeds',(d.feeds_failed||[]).join(' · ')||'None');
 }catch(e){host.textContent='Could not load data-health.json: '+e.message}
}


// v1.5.4C: approximate observed coverage, never a map of actual event frequency.
function coverageColor(n){if(!n)return 'rgba(57,94,111,0.14)';let t=Math.min(1,Math.log1p(n)/Math.log(60));return `rgba(${Math.round(32+29*t)},${Math.round(103+100*t)},${Math.round(139+83*t)},${(.17+.48*t).toFixed(2)})`}
function coverageSource(){return state.news.filter(p=>state.categories.has(p.category)&&(state.precision==='all'||p.accuracy===state.precision))}
function recomputeCountryStats(){
 if(!state.coverageReady||typeof d3==='undefined')return;
 const polygons=state.countries;
 const counts=new Map(polygons.map(c=>[c.id,0]));
 // Each map signal is counted once in the enclosing polygon. A country-level
 // subject remains approximate even if its anchor falls within a boundary.
 for(const p of coverageSource()){
  const feature=polygons.find(f=>d3.geoContains(f,[p.lng,p.lat]));
  if(feature)counts.set(feature.id,(counts.get(feature.id)||0)+p.count);
 }
 state.countryStats=counts;
 for(const country of polygons)country.properties.wpCount=counts.get(country.id)||0;
}
function renderCoverage(){
 if(!globe)return;
 if(!state.coverage||state.layer!=='news'||!state.coverageReady){globe.polygonsData([]);return}
 recomputeCountryStats();globe.polygonsData(state.countries);
}
function selectCoverageCountry(country){
 if(!state.coverage||state.layer!=='news')return;
 const members=coverageSource().filter(p=>typeof d3!=='undefined'&&d3.geoContains(country,[p.lng,p.lat]));
 state.selected={name:country.properties.name+' · sampled coverage',members,count:members.reduce((a,p)=>a+p.count,0)};
 paintDrawer();
}
function initCoverageControls(){
 const panel=$('precisionFilter')?.closest('.control-panel');if(!panel)return;
 const wrap=el('div',undefined,'wp-coverage-control');
 const label=el('label');label.className='toggle';
 const control=document.createElement('input');control.type='checkbox';control.id='coverageLayer';
 label.append(control,el('span','Shade countries by sampled reporting'));
 const explanation=el('p','Approximate coverage only. Unshaded countries may still have news; areas are not incident sites.','hint');
 const note=el('p','Country boundaries loading…','hint');note.id='coverageInfo';
 wrap.append(label,explanation,note);panel.append(wrap);
 control.onchange=()=>{state.coverage=control.checked;renderCoverage()};
 loadBoundaries();
 loadPopulationDensityTexture();
}
async function loadBoundaries(){
 if(bordersLoading||state.coverageReady)return;
 bordersLoading=true;
 const note=$('coverageInfo');
 try{
  // Ship actual boundaries with WorldPulse: no dependency on a third-party
  // CDN or on an optional coverage-mode checkbox for visible neon geography.
  let features=[];
  const local=await fetch('world-borders.geojson',{cache:'no-store'});
  if(local.ok){const geo=await local.json();features=geo.features||[]}
  if(!features.length)throw Error('Bundled geographic geometry unavailable');
  state.countries=features.filter(f=>f.geometry&&f.properties);
  state.coverageReady=true;
  permanentBorders=buildCartographicPaths(state.countries);
  updateCartographicPaths();
  if(note)note.textContent=`${state.countries.length} country/territory outlines loaded · stored locally`;
  if(state.visualMode==='neon')updateNeonTexture();
  renderCoverage();
 }catch(e){
  if(note)note.textContent='Country geography could not load. Check world-borders.geojson is in the repository root.';
  console.warn('WorldPulse cartography:',e);
 }finally{bordersLoading=false}
}
// Each polygon exterior becomes a permanent neon outline. Holes remain fine
// secondary strokes. All points are geographic lon/lat, never synthetic news.
function buildCartographicPaths(features){
 const paths=[];
 for(const f of features){
  const g=f.geometry;
  const polys=g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[];
  for(const poly of polys){for(let i=0;i<poly.length;i++){
   const ring=poly[i];if(!ring||ring.length<3)continue;
   // Simple line geometry, kept above the surface and below the markers.
   paths.push({coords:ring,kind:i===0?'coast':'border'});
  }}
 }
 return paths;
}
function updateCartographicPaths(){
 // Keep geographic borders baked into the equirectangular surface texture.
 // The three-globe paths API triggered an incompatible d3-geo runtime exception
 // (t.Adder is not a constructor) on the deployed dependency versions.
 // Texture lines are globe-fixed and do not depend on the news feed.
 if(globe && typeof globe.pathsData === 'function') globe.pathsData([]);
}

function healthStat(container,label,value){const c=el('div',undefined,'wp-health-stat');c.append(el('span',label),el('strong',String(value)));container.append(c)}
function addHealthOverview(host,d){
 const card=el('div',undefined,'wp-health-overview');
 healthStat(card,'Mapped articles',d.mapped_total??'—');
 healthStat(card,'Mapped signals',d.geo_signal_count??'—');
 healthStat(card,'Feeds responding',`${d.feeds_ok??'—'} / ${d.feeds_total??'—'}`);
 healthStat(card,'Distinct unmatched headlines',d.unmapped_distinct_titles??'—');
 host.append(card);
 const section=(heading,values)=>{
  const entries=Object.entries(values||{}).sort((a,b)=>b[1]-a[1]);if(!entries.length)return;
  const wrap=el('section',undefined,'wp-health-breakdown');wrap.append(el('h3',heading));const max=Math.max(1,...entries.map(x=>Number(x[1])||0));
  for(const [k,v] of entries.slice(0,12)){
   const line=el('div',undefined,'wp-bar-row');const title=el('span',LABELS[k]||k);const bar=el('div',undefined,'wp-bar-track');
   const fill=el('div',undefined,'wp-bar-fill');fill.style.width=(100*Number(v)/max).toFixed(1)+'%';bar.append(fill);
   line.append(title,bar,el('b',String(v)));wrap.append(line);
  }host.append(wrap);
 };
 section('Topic breakdown (mapped sample)',d.mapped_articles_by_category);
 section('Geographic precision',d.mapped_articles_by_location_precision);
 const note=el('p','Country-level counts are only available when supported by explicit geographic mapping. A missing country does not mean no news occurred. Counts are samples, not worldwide totals.','wp-caution');host.append(note);
}


/* v1.6A — neon globe: all location markers remain grounded in collected data. */
function neonPointColor(p){
 const base=COLORS[p.category]||COLORS.social;
 if(state.visualMode!=='neon'||!state.twinkle)return base;
 // Small deterministic variations per signal, not a changing news-velocity claim.
 let seed=Math.abs(Math.sin(p.lat*12.9898+p.lng*78.233)*43758.5453)%1;
 return seed>.87?'#ffffff':base;
}
function makeNeonTexture(){
 if(neonTextureUrl)return neonTextureUrl;
 const canvas=document.createElement('canvas');canvas.width=2048;canvas.height=1024;
 const ctx=canvas.getContext('2d');ctx.fillStyle='#020d1c';ctx.fillRect(0,0,2048,1024);
 // Latitude/longitude wireframe. Lines are decorative, not geographic events.
 ctx.lineWidth=1;
 for(let lat=-75;lat<=75;lat+=15){const y=(90-lat)/180*1024;ctx.strokeStyle=lat===0?'rgba(24,244,239,.34)':'rgba(26,201,221,.22)';ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(2048,y);ctx.stroke();}
 for(let lon=-180;lon<180;lon+=15){const x=(lon+180)/360*2048;ctx.strokeStyle=lon===0?'rgba(24,244,239,.34)':'rgba(26,201,221,.20)';ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,1024);ctx.stroke();}
 neonTextureUrl=canvas.toDataURL('image/png');return neonTextureUrl;
}
// v1.6B cartography: generated in-browser from country geometries, not news data.
// A raster mask avoids doing thousands of costly point-in-country searches.
// This image is generated separately using WorldPop data, not the news feed.
function loadPopulationDensityTexture(){
 if(measuredPopulationStatus!=='not-loaded')return;
 measuredPopulationStatus='loading';
 const image=new Image();
 image.onload=()=>{
  measuredPopulationImage=image;
  measuredPopulationStatus='ready';
  console.info('WorldPulse: measured population brightness raster ready.');
  if(globe&&state.coverageReady&&state.visualMode==='neon')updateNeonTexture();
 };
 image.onerror=()=>{
  measuredPopulationStatus='unavailable';
  console.info('WorldPulse: optional population raster not available; using existing approximate settlement brightness.');
 };
 image.src='assets/population-density.png';
}
function updateNeonTexture(){
 // Build a geographically accurate equirectangular image directly from the
 // bundled GeoJSON. This does NOT depend on D3, news data, or WebGL paths APIs.
 if(!globe||state.visualMode!=='neon'||!state.coverageReady||!state.countries.length)return;
 try{
  const W=2048,H=1024,c=document.createElement('canvas');c.width=W;c.height=H;
  const x=c.getContext('2d');x.fillStyle='#020c19';x.fillRect(0,0,W,H);
  const px=lon=>(lon+180)/360*W,py=lat=>(90-lat)/180*H;
  // Restrained latitude-longitude grid, well below geographic outlines.
  x.strokeStyle='rgba(24,140,166,.13)';x.lineWidth=1;
  for(let lat=-75;lat<=75;lat+=15){x.beginPath();x.moveTo(0,py(lat));x.lineTo(W,py(lat));x.stroke()}
  for(let lon=-180;lon<=180;lon+=15){x.beginPath();x.moveTo(px(lon),0);x.lineTo(px(lon),H);x.stroke()}
  const polys=[];
  for(const feat of state.countries){const g=feat.geometry;if(!g)continue;
   if(g.type==='Polygon')polys.push(g.coordinates);
   else if(g.type==='MultiPolygon')polys.push(...g.coordinates);
  }
  function traceRing(ring){
   if(!Array.isArray(ring)||ring.length<3)return;
   let last=null,segmentOpen=false;
   for(const pt of ring){if(!Array.isArray(pt)||pt.length<2)continue;
    const u=px(pt[0]),v=py(pt[1]);
    if(!last||Math.abs(u-last[0])>W*.5){if(segmentOpen)x.stroke();x.beginPath();x.moveTo(u,v);segmentOpen=true}
    else x.lineTo(u,v);
    last=[u,v];
   }
   if(segmentOpen)x.stroke();
  }
  // Land dotted texture with population-informed brightness.
  // The grid spacing stays uniform; only brightness changes with settlement density.
  const mask=document.createElement('canvas');mask.width=W;mask.height=H;
  const m=mask.getContext('2d',{willReadFrequently:true});m.fillStyle='#ffffff';
  for(const poly of polys){m.beginPath();let opened=false;
   for(const ring of poly){if(!ring?.length)continue;for(let k=0;k<ring.length;k++){
    const u=px(ring[k][0]),v=py(ring[k][1]);if(k===0)m.moveTo(u,v);else m.lineTo(u,v)
   }m.closePath();opened=true}
   if(opened)m.fill('evenodd');
  }
  const alpha=m.getImageData(0,0,W,H).data;
  let populationPixels=null;
  if(measuredPopulationImage){
   const populationCanvas=document.createElement('canvas');populationCanvas.width=W;populationCanvas.height=H;
   const pctx=populationCanvas.getContext('2d',{willReadFrequently:true});
   pctx.drawImage(measuredPopulationImage,0,0,W,H);
   populationPixels=pctx.getImageData(0,0,W,H).data;
  }

  // Keep the regular dot grid. Settlement intensity changes brightness only,
  // so background structure stays distinct from foreground news events.
  // City-hub estimates are an aesthetic proxy, NOT measured census density.
  if(!measuredPopulationImage)for(const hub of POP_HUBS){
   const u=px(hub.lng),v=py(hub.lat);
   const radius=Math.max(12,Math.min(29,hub.weight*1.8));
   const g=x.createRadialGradient(u,v,0,u,v,radius);
   g.addColorStop(0,`rgba(15,191,208,${Math.min(.11,.025+hub.weight*.009).toFixed(3)})`);
   g.addColorStop(.55,'rgba(13,128,168,.018)');
   g.addColorStop(1,'rgba(0,0,0,0)');
   x.fillStyle=g;x.beginPath();x.arc(u,v,radius,0,Math.PI*2);x.fill();
  }
  const gridStep=5;
  for(let v=2;v<H;v+=gridStep)for(let u=2;u<W;u+=gridStep){
   if(alpha[(v*W+u)*4+3]<128)continue;
   const lat=90-(v/H)*180,lon=(u/W)*360-180;
   const density=populationPixels ? populationPixels[(v*W+u)*4]/255 : ambientSettlementDensity(lat,lon);
   // Perceptually lift intermediate density without flattening contrast.
   const t=Math.pow(Math.max(0,Math.min(1,density)),.82);
   const variation=(Math.abs(Math.sin(u*12.9898+v*78.233)*43758.5453)%1-.5)*.045;
   const opacity=Math.max(.085,Math.min(.70,.09+.56*t+variation));
   const channelG=Math.round(150+77*t);
   const channelB=Math.round(172+59*t);
   x.fillStyle=`rgba(57,${channelG},${channelB},${opacity.toFixed(3)})`;
   x.fillRect(u,v,1.35,1.35);
  }
  // Permanent boundaries: doubled luminous strokes, fixed to the Earth texture.
  for(const [width,color,blur] of [[4,'rgba(0,240,233,.23)',7],[1.35,'rgba(56,240,235,.88)',0]]){
   x.save();x.lineWidth=width;x.strokeStyle=color;x.shadowColor='#03d6df';x.shadowBlur=blur;
   for(const poly of polys)for(const ring of poly)traceRing(ring);
   x.restore();
  }
  neonTextureUrl=c.toDataURL('image/png');globe.globeImageUrl(neonTextureUrl);
 }catch(error){console.error('WorldPulse neon cartography texture:',error);}
}
// Decorative glow around actual map signals. Never generates additional locations.
function refreshMarkerHalos(){
 // HTML markers leaked outside the globe near screen corners. Intentionally
 // disabled: native WebGL category markers remain on the actual sphere.
 if(globe&&typeof globe.htmlElementsData==='function')globe.htmlElementsData([]);
}

function applyVisualMode(){
 if(!globe)return;
 document.body.classList.toggle('wp-neon',state.visualMode==='neon');
 document.querySelectorAll('[data-visual]').forEach(b=>{b.classList.toggle('active',b.dataset.visual===state.visualMode);b.setAttribute('aria-pressed',String(b.dataset.visual===state.visualMode));});
 globe.globeImageUrl(state.visualMode==='neon'?makeNeonTexture():REAL_EARTH);
 globe.atmosphereColor(state.visualMode==='neon'?'#00e7ee':'#4baec0').atmosphereAltitude(state.visualMode==='neon'?.095:.14);
 globe.pointAltitude(p=>signalAltitude(p));
 globe.pointRadius(p=>signalRadius(p));
 globe.pointColor(p=>signalColor(p));
 if(state.visualMode==='neon'&&state.coverageReady)updateNeonTexture();
 updateCartographicPaths();
 refreshMarkerHalos();
 // Satellite view uses original bump texture; neon surface stays completely smooth.
 globe.bumpImageUrl(state.visualMode==='real'?'https://unpkg.com/three-globe/example/img/earth-topology.png':null);
 renderPoints();
}
// v1.6D: all decorative light is derived from actual signals. No synthetic locations.
function signalRadius(p){
 if(state.visualMode!=='neon')return p.broadAnchor?.32:Math.min(1.6,.19+Math.sqrt(p.count)*.11);
 const size=Math.min(1.55,.27+Math.sqrt(Math.max(1,p.count))*.17);
 return p.wpHalo ? Math.min(2.8,size*1.8) : size;
}
function signalAltitude(p){
 if(state.visualMode!=='neon')return Math.min(.08,.011+Math.log1p(p.count)*.008);
 return p.wpHalo ? .003 : .013;
}
function signalColor(p){
 const base=COLORS[p.category]||COLORS.social;
 if(state.visualMode!=='neon')return base;
 if(p.wpHalo){
  // Low-opacity cyan/category light under the core. Alpha deliberately capped.
  const rgb=hexRgb(base);
  const activity=Math.min(1,Math.log1p(p.count)/Math.log(25));
  return `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${(.085+.11*activity).toFixed(3)})`;
 }
 return neonPointColor(p);
}
function hexRgb(hex){return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16))}
function signalDisplayPoints(points){
 if(state.visualMode!=='neon')return points;
 const halos=points.filter(p=>p.count>=2).map(p=>({...p,wpHalo:true,signalSource:p}));
 return [...halos,...points];
}
function refreshSignalGlow(){
 if(!globe||!currentPoints.length)return;
 if(state.visualMode!=='neon'||!state.twinkle){globe.pointColor(p=>signalColor(p));return}
 const tick=Math.floor(Date.now()/1600);
 globe.pointColor(p=>{
  if(p.wpHalo)return signalColor(p);
  const base=COLORS[p.category]||COLORS.social;
  const phase=(Math.sin(p.lat*8.71+p.lng*2.29+tick*.45)+1)/2;
  if(phase>.97){const rgb=hexRgb(base);return `rgb(${Math.round(rgb[0]+(255-rgb[0])*.26)},${Math.round(rgb[1]+(255-rgb[1])*.26)},${Math.round(rgb[2]+(255-rgb[2])*.26)})`}
  return base;
 });
}
function initVisualControls(){
 const panel=document.getElementById('visualModes');if(!panel)return;
 panel.querySelectorAll('[data-visual]').forEach(button=>button.addEventListener('click',()=>{
  state.visualMode=button.dataset.visual;localStorage.setItem('worldpulse-globe-mode',state.visualMode);applyVisualMode();
 }));
 const glow=document.getElementById('twinkleToggle');
 if(glow)glow.onchange=()=>{state.twinkle=glow.checked;applyVisualMode()};
 document.body.classList.toggle('wp-neon',state.visualMode==='neon');
 document.querySelectorAll('[data-visual]').forEach(b=>b.classList.toggle('active',b.dataset.visual===state.visualMode));
 setInterval(refreshSignalGlow,1600);
}

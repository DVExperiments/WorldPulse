/* WorldPulse — static GitHub Pages viewer. The scheduled workflow owns data updates. */
'use strict';
const COLORS={politics:'#eeb67e',environment:'#6edcb3',hazards:'#ef797d',society:'#ae94f3',health:'#d3a1ff',education:'#a8a3ff',rights:'#ef9bd0',community:'#bb95dd',economy:'#72baf1',science:'#e4d475',conflict:'#ff5878',social:'#eb8eeb'};
const LABELS={politics:'Politics',environment:'Environment',hazards:'Hazards',health:'Health',education:'Education',rights:'Rights & justice',community:'Community & culture',society:'Society (legacy)',economy:'Economy',science:'Science',conflict:'War & conflict'};
const $=id=>document.getElementById(id);
const state={news:[],posts:[],events:[],layer:'news',categories:new Set(Object.keys(LABELS)),cluster:true,precision:'all',rotate:true,translate:true,selected:null,translator:null,language:navigator.language||'en',feed:null,coverage:false,countries:[],countryStats:new Map(),coverageReady:false};
let globe, currentPoints=[], lastTier=-1, translationCache=new Map();
function clean(s){return String(s??'').slice(0,500)}
function dist(a,b){let rad=Math.PI/180,dLat=(b.lat-a.lat)*rad,dLng=(b.lng-a.lng)*rad;let x=Math.sin(dLat/2)**2+Math.cos(a.lat*rad)*Math.cos(b.lat*rad)*Math.sin(dLng/2)**2;return 6371*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x))}
function age(ts){if(!ts)return 'not yet updated';let m=Math.floor((Date.now()-new Date(ts).getTime())/60000);if(!Number.isFinite(m))return 'unknown';if(m<0)return 'just updated';if(m<60)return `${m} minutes ago`;return `${Math.floor(m/60)} hours ago`}
function initGlobe(){
 if(typeof Globe==='undefined'){$('emptyNotice').hidden=false;$('emptyNotice').textContent='The 3D globe could not load. Check your internet connection or browser WebGL support.';return;}
 globe=Globe()($('globe'))
  .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
  .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
  .backgroundColor('rgba(0,0,0,0)')
  .showAtmosphere(true).atmosphereColor('#4baec0').atmosphereAltitude(.14)
  .pointsMerge(false).pointLat('lat').pointLng('lng')
  .pointColor(p=>COLORS[p.category]||COLORS.social)
  .pointAltitude(p=>Math.min(.08,.011+Math.log1p(p.count)*.008))
  .pointRadius(p=>p.broadAnchor?.32:Math.min(1.6,.19+Math.sqrt(p.count)*.11))
  .pointLabel(p=>`${clean(p.name)} · ${p.count.toLocaleString()} ${state.layer==='news'?'sampled articles':state.layer==='events'?'recorded events':'posts'}${p.accuracy==='country'?' · COUNTRY-LEVEL SUBJECT (approximate)':p.accuracy==='region'?' · regional reference':''}${p.velocity==='rising'?' · ↑ Rising':''}`)
  .ringsData([])
  .polygonsData([]).polygonCapColor(p=>coverageColor(p.properties.wpCount||0))
  .polygonSideColor(()=>'rgba(22,68,85,0.05)').polygonStrokeColor(()=>'rgba(167,204,219,0.26)')
  .polygonAltitude(()=>.004)
  .polygonLabel(p=>`${clean(p.properties.name)}: ${p.properties.wpCount||0} sampled mapped articles (approximate)`)
  .onPolygonClick(p=>selectCoverageCountry(p))
  .onPointClick(p=>openPoint(p))
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
 currentPoints=aggregate(mapped);globe.pointsData(currentPoints);renderCoverage();
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
 $('aboutBtn').onclick=$('methodBtn').onclick=()=>$('about').hidden=false;
 initCoverageControls();
 $('healthBtn').onclick=()=>{ $('healthModal').hidden=false; showHealth(); };
 $('healthClose').onclick=()=>$('healthModal').hidden=true;
 $('aboutClose').onclick=()=>$('about').hidden=true;
 $('about').onclick=e=>{if(e.target===$('about'))$('about').hidden=true};
 $('healthModal').onclick=e=>{if(e.target===$('healthModal'))$('healthModal').hidden=true};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){$('about').hidden=true;$('healthModal').hidden=true;$('drawer').hidden=true}});
 function clock(){$('clock').textContent=new Intl.DateTimeFormat('en-GB',{timeZone:'UTC',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date())+' UTC'}clock();setInterval(clock,30000);
}
bind();initGlobe();loadData();loadEvents();setInterval(loadData,15*60*1000);

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
}
async function loadBoundaries(){
 const note=$('coverageInfo');
 if(typeof topojson==='undefined'||typeof d3==='undefined'){if(note)note.textContent='Coverage layer unavailable (mapping library missing).';return}
 try{
  const r=await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json');
  if(!r.ok)throw Error('HTTP '+r.status);
  const topo=await r.json();const features=topojson.feature(topo,topo.objects.countries).features;
  state.countries=features.filter(f=>f.geometry&&f.properties);
  state.coverageReady=true;
  if(note)note.textContent=`${state.countries.length} country/territory shapes available · sampled counts only`;
  renderCoverage();
 }catch(e){if(note)note.textContent='Coverage outlines unavailable. News markers remain usable.'}
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

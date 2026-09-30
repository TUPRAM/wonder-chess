const grid = document.querySelector('#skill-grid');
const search = document.querySelector('#search');
const collection = document.querySelector('#collection');
const priority = document.querySelector('#priority');
const count = document.querySelector('#result-count');
let catalogue;
function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function normalized(s, kind) {
  return {...s, id:s.id || s.stable_id, kind,
    status:kind==='proposed' ? 'PROPOSED · NOT RUN' : `${s.maturity.grade} · SCOPED AUDIT`,
    dependencyText:[...(s.dependencies||[]).map(d=>typeof d==='string'?d:d.path),...(s.skill_dependencies||[])].join(', ')};
}
function render() {
  const all = (collection.value==='proposed' ? catalogue.proposed_skills : catalogue.existing_skills).map(s=>normalized(s, collection.value));
  const query = search.value.trim().toLowerCase();
  const filtered = all.filter(s=>(priority.value==='all'||s.priority.startsWith(priority.value)) && JSON.stringify(s).toLowerCase().includes(query));
  count.textContent = `${filtered.length} of ${all.length} ${collection.value==='proposed'?'proposed capabilities':'audited skills'} · ${collection.value==='proposed'?'planning specifications, not installed packages':'package maturity is separate from game acceptance'}`;
  grid.replaceChildren();
  if (!filtered.length) {grid.append(node('p','No matching skills. Change the search or priority filter.','empty'));return;}
  for (const s of filtered) {
    const card=node('article',undefined,'skill-card');
    const top=node('div',undefined,'card-top');
    top.append(node('span',s.id,'card-id'),node('span',s.priority,'priority-badge'));
    card.append(top,node('h3',s.name.replaceAll('-',' ')),node('p',s.purpose));
    const meta=node('div',undefined,'card-meta');meta.append(node('span',s.status),node('span',s.disposition.replaceAll('_',' ').toLowerCase()));card.append(meta);
    const details=node('details');details.append(node('summary','Inputs, gates & qualification'));
    const fields=s.kind==='proposed'
      ? [['Trigger',s.trigger],['Inputs',s.inputs.join('; ')],['Outputs',s.outputs.join('; ')],['Dependencies',s.dependencyText],['Gate',s.gate],['Human authority',s.human_authority],['Reuse',s.reuse_level],['Why separate',s.reason_separate]]
      : [['Coverage',s.actual_coverage],['Dependencies',s.dependencyText],['Routing',s.routing_issues.join('; ')],['Evidence',s.evidence_status],['Maturity limit',s.maturity.reason],['Qualification',s.qualification],['Human authority',s.human_authority_boundary],['Definition hash',s.definition_sha256]];
    const dl=node('dl');for(const [label,value] of fields)dl.append(node('dt',label),node('dd',value));details.append(dl);card.append(details);grid.append(card);
  }
}
fetch('data/skill-catalogue.json').then(r=>{if(!r.ok)throw new Error('Catalogue response '+r.status);return r.json();}).then(data=>{catalogue=data;render();}).catch(e=>{count.textContent='Catalogue could not load. The complete report and downloads remain available.';grid.replaceChildren(node('p',e.message));});
for(const control of [search,collection,priority])control.addEventListener('input',()=>{if(catalogue)render();});
document.querySelector('#expand-all').addEventListener('click',()=>document.querySelectorAll('.report-section').forEach(e=>e.open=true));
document.querySelector('#collapse-all').addEventListener('click',()=>document.querySelectorAll('.report-section').forEach(e=>e.open=false));
function revealHash() {
  const id=decodeURIComponent(location.hash.slice(1));
  const target=document.getElementById(id);
  if(target?.classList.contains('report-section'))target.open=true;
}
window.addEventListener('hashchange',revealHash);revealHash();

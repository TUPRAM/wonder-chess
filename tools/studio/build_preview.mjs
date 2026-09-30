import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

// Report publishing only. It does not install/execute any proposed production skill.
const root = path.resolve(import.meta.dirname, '../..');
const source = path.join(root, 'docs/studio-production-20260930');
const out = path.join(root, 'web/studio-production');
const markedArg = process.argv.indexOf('--marked-dir');
const require = createRequire(import.meta.url);
const markedPath = markedArg >= 0
  ? path.join(path.resolve(process.argv[markedArg + 1]), 'lib/marked.esm.js')
  : require.resolve('marked');
const { marked } = await import(pathToFileURL(markedPath).href);
const markedPackage = JSON.parse(fs.readFileSync(path.resolve(path.dirname(markedPath), '../package.json'), 'utf8'));
if (markedPackage.version !== '17.0.5') throw new Error('Use qualified report renderer marked 17.0.5');
const sha = (data) => crypto.createHash('sha256').update(data).digest('hex');
const read = (name) => fs.readFileSync(path.join(source, name), 'utf8').replace(/^\uFEFF/, '');
const escape = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sections = [
  ['recommendation','01','Recommendation','00-executive.md'],
  ['current-state','02','Current state','01-current-state.md'],
  ['skill-audit','02a','28-skill audit','02-skill-audit.md'],
  ['pipeline','03–04','Practices & lifecycle','03-practices-and-pipeline.md'],
  ['catalogue','05','Capability catalogue','05-catalogue.md'],
  ['priorities','06','Eight priority specifications','06-package-and-priorities.md'],
  ['orchestration','07','Tools & orchestration','07-orchestration.md'],
  ['evaluation','08','Evaluation & maturity','08-evaluation.md'],
  ['quality','09','Quality & Wonder Atlas','09-quality-and-atlas.md'],
  ['pilots','10','Pilots & next batches','10-pilots-and-batches.md'],
  ['limitations','11','Decisions & limitations','11-limitations.md']
];
const existing = JSON.parse(read('existing-skills.json'));
const proposed = JSON.parse(read('proposed-skills.json'));
const sources = JSON.parse(read('sources.json'));
const catalogue = {
  schema_version:'studio-catalogue/0.1-proposed', as_of:'2026-09-30', timezone:'Asia/Shanghai',
  status:'PROPOSED_PLANNING_ARTIFACT_NOT_INSTALLED_OR_TESTED',
  existing_inspection:existing.inspection, maturity_scale:existing.maturity_scale,
  existing_skills:existing.skills, proposed_skills:proposed.skills, evidence:existing.evidence,
  interpretation:'Existing route evidence is scoped; all new packages are proposals. No production qualification ran in this audit.'
};
if (existing.skills.length !== 28 || proposed.skills.length !== 16) throw new Error('Catalogue count mismatch');
const catalogueText = JSON.stringify(catalogue, null, 2) + '\n';
fs.writeFileSync(path.join(source, 'skill-catalogue.json'), catalogueText);
const report = '# Wonder Chess — Studio Production Architecture\n\nPrepared 30 September 2026, Asia/Shanghai. Proposed planning artifacts; not installed or qualified production skills.\n\n'
  + sections.map(s=>read(s[3]).trim()).join('\n\n---\n\n')
  + '\n\n## External primary-source register\n\n'
  + sources.sources.map(s=>`- [${s.title}](${s.url}) — ${s.publisher}, accessed ${s.accessed}. ${s.lesson} Limit: ${s.limits}`).join('\n') + '\n';
fs.writeFileSync(path.join(source,'REPORT.md'), report);
fs.mkdirSync(path.join(out,'downloads'), {recursive:true});
fs.mkdirSync(path.join(out,'data'), {recursive:true});
fs.writeFileSync(path.join(out,'data/skill-catalogue.json'), catalogueText);
const downloadable = [...sections.map(s=>s[3]),'REPORT.md','skill-catalogue.json','current-state.json','existing-skills.json','proposed-skills.json','sources.json'];
for (const name of downloadable) fs.writeFileSync(path.join(out,'downloads',name), read(name));
const renderer = new marked.Renderer();
renderer.link = ({href,title,tokens}) => {
  const label = marked.Parser.parseInline(tokens);
  if (/^https:\/\//.test(href)) return `<a href="${escape(href)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>`;
  const name = path.basename(href.split('#')[0]);
  if (!href.startsWith('../') && downloadable.includes(name)) return `<a href="downloads/${escape(name)}">${label}</a>`;
  if (href.startsWith('#')) return `<a href="${escape(href)}">${label}</a>`;
  // Local unpublished production evidence is not uploaded or linked to a false remote location.
  return `<span class="local-source" title="Local project evidence, not bundled: ${escape(href)}">${label} <span aria-label="local evidence">[local]</span></span>`;
};
marked.use({renderer, gfm:true});
const nav = sections.map(s=>`<a href="#${s[0]}"><span>${s[1]}</span>${escape(s[2])}</a>`).join('');
const body = sections.map(s=>`<details class="report-section" id="${s[0]}" ${s[0]==='recommendation'?'open':''}><summary><span class="section-number">${s[1]}</span><span>${escape(s[2])}</span><span class="expand" aria-hidden="true">+</span></summary><div class="prose">${marked.parse(read(s[3]))}</div></details>`).join('');
const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Wonder Chess studio architecture: evidence-based audit of 28 existing skills, 8 priority specifications and 3 bounded production pilots."><title>Wonder Chess · Studio Production Review</title><link rel="icon" href="data:,"><link rel="stylesheet" href="styles.css"><script src="app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to report</a><aside class="rail"><a class="brand" href="#main"><span class="sigil">W</span><span>WONDER CHESS<small>PRODUCTION REVIEW</small></span></a><p class="rail-label">THE STUDIO BLUEPRINT</p><nav aria-label="Report sections">${nav}</nav><div class="rail-bottom"><span class="status-dot"></span> Planning edition<small>30 September 2026 · Asia/Shanghai</small><a href="downloads/REPORT.md" download>Download full report ↓</a></div></aside>
<main id="main"><header class="masthead"><span>RESEARCH / SYSTEMS / PRODUCTION</span><a href="https://github.com/TUPRAM/wonder-chess/tree/codex/studio-production-20260930" target="_blank" rel="noopener noreferrer">View GitHub branch ↗</a></header>
<section class="hero"><div class="eyebrow"><span class="status-dot"></span> OWNER-LED STUDIO · PROPOSED ARCHITECTURE</div><h1>A studio system built<br>around a <em>playable loop.</em></h1><p class="intro">What Wonder Chess has, what needs proof, and the smallest production system that can take the game forward.</p><div class="hero-actions"><a class="button" href="#recommendation">Read the recommendation <span>↘</span></a><a class="text-link" href="downloads/skill-catalogue.json" download>Get the skill catalogue ↓</a></div><div class="metrics"><div><strong>28</strong><span>existing skills audited</span></div><div><strong>08</strong><span>priority specifications</span></div><div><strong>03</strong><span>bounded pilot plans</span></div><div><strong>07</strong><span>enabled creatures at snapshot</span></div></div></section>
<section class="takeaway"><div><span class="eyebrow">THE RECOMMENDATION</span><h2>Prove the small loop.<br>Then earn the next layer.</h2></div><p>Close recruitment, formation, combat, recap and adaptation with real human evidence. Complete one preserved creature delivery, exercise a controlled revision, then prove reuse on a second case.</p><span class="stamp">PLANNING<br>ONLY</span></section>
<section class="evidence-note"><strong>Evidence stays scoped.</strong> Current local snapshot: seven enabled / fourteen authored heroes; eighteen traits inactive. New packages are proposals. Recorded technical passes, owner art decisions and full-game acceptance remain separate. This preview contains report text and metadata, with local production evidence labeled.</section>
<section id="explore" class="catalogue"><div class="section-heading"><div><span class="eyebrow">THE CAPABILITY SYSTEM</span><h2>Explore the catalogue</h2></div><a class="text-link" href="downloads/skill-catalogue.json" download>Machine-readable JSON ↓</a></div><div class="filters"><label class="search"><span>⌕</span><input id="search" type="search" placeholder="Search skills, purpose or dependencies" aria-label="Search skills"></label><label>Collection<select id="collection"><option value="proposed">Proposed capabilities (16)</option><option value="existing">Existing skill audit (28)</option></select></label><label>Priority<select id="priority"><option value="all">All priorities</option><option value="P0">P0 · First stack</option><option value="P1">P1 · Extensions</option><option value="P2">P2 · Later</option><option value="P3">P3 · Specialist routes</option></select></label></div><p id="result-count" class="result-count" aria-live="polite"></p><div id="skill-grid" class="skill-grid"><p>Loading the audited catalogue…</p></div><noscript>Use the full report below or download the JSON catalogue. Catalogue filters require JavaScript.</noscript></section>
<section class="report"><div class="section-heading"><div><span class="eyebrow">THE COMPLETE REPORT</span><h2>From evidence to delivery</h2></div><div class="report-controls"><button id="expand-all" type="button">Expand all</button><button id="collapse-all" type="button">Collapse all</button></div></div>${body}</section>
<section class="sources"><span class="eyebrow">PRIMARY SOURCES</span><h2>Documented practice, applied carefully.</h2><p>Official engine, provider, accessibility and distribution references support the report's recommendations. Tool documentation does not establish local qualification.</p><div class="source-links">${sources.sources.map(s=>`<a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">${escape(s.publisher)}<strong>${escape(s.title)} ↗</strong></a>`).join('')}</div></section>
<footer><span>Wonder Chess · Studio Production Review</span><a href="downloads/REPORT.md" download>Markdown report ↓</a><a href="downloads/current-state.json" download>Evidence snapshot ↓</a><a href="downloads/sources.json" download>Source register ↓</a><p>Planning artifacts prepared 30 September 2026. Proposed skills are not installed or tested. Browser report verification does not certify the Unreal game.</p></footer></main></body></html>`;
fs.writeFileSync(path.join(out,'index.html'), html);
const inputs = [...new Set([...downloadable.filter(x=>!['REPORT.md','skill-catalogue.json'].includes(x))])].map(name=>({path:`docs/studio-production-20260930/${name}`,sha256:sha(read(name))}));
const outputs = ['index.html','app.js','styles.css','vercel.json','data/skill-catalogue.json', ...downloadable.map(n=>'downloads/'+n)].filter(n=>fs.existsSync(path.join(out,n))).map(n=>({path:`web/studio-production/${n}`,sha256:sha(fs.readFileSync(path.join(out,n)))}));
fs.writeFileSync(path.join(out,'build-manifest.json'),JSON.stringify({status:'REPORT_PREVIEW_ONLY',renderer:'marked@17.0.5',inputs,outputs},null,2)+'\n');
console.log(JSON.stringify({report_words:report.split(/\s+/).length,existing:28,proposed:16,sections:sections.length,output:out}));

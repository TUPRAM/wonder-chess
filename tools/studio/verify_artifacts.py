"""Verify report/catalogue integrity; never runs game or proposed-skill jobs."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/studio-production-20260930'
WEB = ROOT / 'web/studio-production'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

existing = json.loads((DOCS / 'existing-skills.json').read_text(encoding='utf-8'))
proposed = json.loads((DOCS / 'proposed-skills.json').read_text(encoding='utf-8'))
combined = json.loads((DOCS / 'skill-catalogue.json').read_text(encoding='utf-8'))
assert len(existing['skills']) == 28
assert len(proposed['skills']) == 16
assert len({s['stable_id'] for s in existing['skills']}) == 28
assert len({s['id'] for s in proposed['skills']}) == 16
assert combined['existing_skills'] == existing['skills']
assert combined['proposed_skills'] == proposed['skills']
assert [s['id'] for s in proposed['skills'] if s['priority'] == 'P0'] == [f'SP-{n:02d}' for n in range(1, 9)]
required = {'id', 'purpose', 'trigger', 'inputs', 'outputs', 'dependencies', 'gate', 'human_authority', 'reuse_level', 'priority', 'disposition', 'evidence_status', 'reason_separate'}
for skill in proposed['skills']:
    assert required <= set(skill), skill['id']
    assert 'NOT_RUN' in skill['evidence_status']
    assert skill['maturity'] == 'PROPOSED'
    for dep in skill['dependencies']:
        if re.fullmatch(r'SP-\d{2}', dep):
            assert dep in {s['id'] for s in proposed['skills']}

archive = ROOT / existing['inspection']['archive']
assert digest(archive) == existing['inspection']['sha256']
with zipfile.ZipFile(archive) as z:
    files = [n for n in z.namelist() if not n.endswith('/')]
    assert len(files) == 52
    assert sum(n.endswith('SKILL.md') for n in files) == 28
    assert sum(n.endswith('openai.yaml') for n in files) == 24
for skill in existing['skills']:
    assert digest(ROOT / skill['definition_path']) == skill['definition_sha256']
    if skill['agent_configuration']['path']:
        assert digest(ROOT / skill['agent_configuration']['path']) == skill['agent_configuration']['sha256']
    for dep in skill['dependencies']:
        assert (ROOT / dep['path']).exists(), dep['path']

manifest = json.loads((WEB / 'build-manifest.json').read_text(encoding='utf-8'))
for output in manifest['outputs']:
    assert digest(ROOT / output['path']) == output['sha256'], output['path']
for item in manifest['inputs']:
    raw = (ROOT / item['path']).read_bytes().decode('utf-8').removeprefix('\ufeff')
    assert hashlib.sha256(raw.encode()).hexdigest() == item['sha256'], item['path']
for artifact in list(DOCS.glob('*.json')) + list(DOCS.glob('*.md')):
    raw = artifact.read_text(encoding='utf-8')
    assert '\ufffd' not in raw, artifact.name
    assert not re.search(r'\b(?:ghp_|gho_|sk_live_)[A-Za-z0-9]{15,}', raw), artifact.name
html = (WEB / 'index.html').read_text(encoding='utf-8')
assert html.count('class="report-section"') == 11
for href in re.findall(r'href="([^"]+)"', html):
    if not href.startswith(('https:', 'data:', '#')):
        assert (WEB / href).is_file(), href
assert (WEB / 'downloads/REPORT.md').read_bytes() == (DOCS / 'REPORT.md').read_bytes()
assert (WEB / 'data/skill-catalogue.json').read_bytes() == (DOCS / 'skill-catalogue.json').read_bytes()
assert (DOCS / '06-package-and-priorities.md').read_text(encoding='utf-8').count('## SP-') == 8
print(json.dumps({'status': 'PASS_REPORT_ARTIFACT_INTEGRITY_ONLY', 'existing_skills': 28,
                  'proposed_capabilities': 16, 'priority_specs': 8, 'agent_yamls': 24,
                  'report_sections': 11, 'game_or_production_jobs_run': 0}))

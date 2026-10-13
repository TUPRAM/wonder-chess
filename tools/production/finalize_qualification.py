"""Seal this dated tool qualification and verify the preserved Bellback baseline."""
import csv
import json
import shutil
from pathlib import Path
from asset_checks import fingerprint, sha256, verify_manifest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/pipeline-tools-20260921'
FIX = ROOT / 'support/tools/pipeline/fixtures'

obs_path = OUT / 'obs-qualification.json'
obs = json.loads(obs_path.read_text())
obs['visual_review'] = 'Frame at 1s viewed: correct synthetic four-panel board, no desktop, black unused canvas. Audio fully silent.'
obs_path.write_text(json.dumps(obs, indent=2), encoding='utf-8')

accepted = json.loads((ROOT / 'reports/bellback-production-20260920/owner-acceptance.json').read_text())
errors = []
checked = []
for item in accepted['candidate_files']:
    path = ROOT / item['file']
    if not path.is_file(): errors.append('Missing: ' + item['file']); continue
    if path.stat().st_size != item['bytes'] or sha256(path) != item['sha256']:
        errors.append('Changed: ' + item['file'])
    checked.append(item['file'])
baseline = {'status': 'pass' if not errors else 'fail', 'files_checked': len(checked),
            'authority': 'reports/bellback-production-20260920/owner-acceptance.json', 'errors': errors}
(OUT / 'accepted-bellback-integrity.json').write_text(json.dumps(baseline, indent=2), encoding='utf-8')

backup = ROOT / 'support/archives/pipeline-upgrade-20260921/qualified-fixture-bundle'
restore = ROOT / 'support/archives/pipeline-upgrade-20260921/fixture-restored-copy'
if backup.exists() or restore.exists(): raise RuntimeError('Recovery copies already exist; preserve them')
backup.mkdir(parents=True)
shutil.copytree(FIX, backup / 'native')
diag = ROOT / 'game/Content/WonderChess/Diagnostics/PipelineTools20260921'
shutil.copytree(diag, backup / 'unreal-diagnostics')
files = [fingerprint(p, backup) for p in sorted(backup.rglob('*')) if p.is_file()]
manifest = {'schema_version': 1, 'files': files}
(OUT / 'fixture-bundle-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
shutil.copytree(backup, restore)
recovery_errors = verify_manifest(restore, manifest)
recovery = {'status': 'pass' if not recovery_errors else 'fail', 'files': len(files),
            'backup': backup.relative_to(ROOT).as_posix(), 'restored_copy': restore.relative_to(ROOT).as_posix(),
            'errors': recovery_errors, 'scope': 'fixture full-byte copy verification; no new game-package restore claim'}
(OUT / 'fixture-recovery.json').write_text(json.dumps(recovery, indent=2), encoding='utf-8')

analyses = {}
for kind in ('insights-cpu','insights-memory-light'):
    analyses[kind] = json.loads((OUT / kind / 'result.json').read_text(encoding='utf-8-sig'))
result = {'date': '2026-09-21', 'status': 'IMPLEMENTED_WITH_PROFILING_LIMIT', 'handbook_version': '1.2',
          'tool_modes': {'Krita':'native UI and layered-file interchange verified',
                         'Audacity':'native UI and PCM export verified',
                         'OBS':'built-in Lua capture and file decode verified',
                         'MeshLab':'native UI OBJ round trip verified',
                         'Unreal':'bundled editor APIs and opt-in Data Validation verified',
                         'Git LFS':'repository filters and local object recovery verified',
                         'Insights':'CPU timer export verified; memory analysis errors remain'},
          'baseline': baseline, 'fixture_recovery': recovery,
          'insights': analyses, 'paid_jobs_started': 0, 'production_art_accepted': False,
          'remaining': ['actual-board G1 look approval', 'actual creature pilot including deformation, package and recovery',
                        'memory profiling requalification; current traces report memory-analysis errors',
                        'reconcile pre-existing Bellback rig-inspection sequence hash mismatch without overwriting current work']}
(OUT / 'qualification-summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
state_path = ROOT / 'reports/implementation_state.json'
state = json.loads(state_path.read_text(encoding='utf-8-sig'))
state['creature_pipeline_engineering_20260921'] = {
    'date': '2026-09-21', 'status': result['status'], 'handbook_version': '1.2',
    'report': 'reports/pipeline-tools-20260921/README.md',
    'tool_evidence': 'reports/pipeline-tools-20260921/qualification-summary.json',
    'accepted_bellback_integrity': baseline['status'], 'production_jobs_started': 0,
    'scope': 'Engineering workflow, qualified local tools, reference studio and validation/recovery infrastructure',
    'remaining': result['remaining']}
state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'baseline': baseline, 'recovery': recovery}, indent=2))

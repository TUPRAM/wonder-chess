"""Hash current Ada source/export/content artifacts and cite existing authority only."""
import csv
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(r'C:/Users/iputu/Documents/Wonder Chess')
OUT = Path(__file__).resolve().parent
UID = 'wc_u_human_guardian'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest_path = ROOT / f'exports/heroes/{UID}/export_manifest.json'
manifest = json.loads(manifest_path.read_text())
csv_path = ROOT / 'reports/WC-U440/20260907T165200Z-closeout/asset-matrix-complete-inputs/hero-clips-168.csv'
rows = [r for r in csv.DictReader(csv_path.open(encoding='utf-8-sig', newline='')) if r['id'] == UID]
assert len(rows) == 7
exports = []
for name, expected in manifest['files'].items():
    if name.endswith('.fbx'):
        path = manifest_path.parent / name
        actual = sha(path)
        exports.append({'path': str(path), 'expected_manifest_sha256': expected,
                        'actual_sha256': actual, 'matches': actual == expected})
content = []
for row in rows:
    path = ROOT / row['content_path']
    actual = sha(path)
    content.append({'clip': row['clip'], 'path': str(path), 'actual_sha256': actual,
                    'previous_24hero_matrix_sha256': row['content_sha256'],
                    'matches_previous_24hero_matrix': actual == row['content_sha256'],
                    'previous_report_import_binding': row['current_content_binary_bound_to_import_report']})
paths = [manifest_path, csv_path,
         ROOT / 'reports/implementation_state.json',
         ROOT / 'reports/WC-U440/20260906T160431Z/ada9-import/import-wc_u_human_guardian.json',
         ROOT / 'game/Source/WonderChessRuntime/Private/WCBoardPresenter.cpp',
         ROOT / 'game/Source/WonderChessRuntime/Private/WCFrontEndScene.cpp',
         ROOT / 'game/Source/WonderChessRuntime/Private/WCFrontEnd.cpp',
         ROOT / 'tools/blender/author_alpha.py',
         ROOT / 'tools/blender/refine_update_ada.py',
         ROOT / 'production/asset-studio/supplements/BW3/docs/04_FIXED_GRIP_OPTION.md']
state = json.loads((ROOT / 'reports/implementation_state.json').read_text(encoding='utf-8-sig'))
result = {
    'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source_revision': manifest.get('source_revision'),
    'animation_revision': manifest.get('animation_revision'),
    'source_and_export_manifest': {'path': str(manifest_path), 'sha256': sha(manifest_path)},
    'exports': exports, 'current_content_vs_prior_24hero_matrix': content,
    'source_files_read': [{'path': str(p), 'sha256': sha(p)} for p in paths],
    'existing_update_delivery_record': state.get('update_delivery'),
    'not_run': ['game execution', 'Unreal asset decode', 'new import/reimport',
                'packaged binary equivalence', 'fixed-grip construction or adoption'],
    'limits': ['Prior importer report lacks content binary hashes; matching existing closeout hashes do not remedy that provenance gap.',
               'Authored source animation inspection cannot certify current packaged pixel output.'],
}
target = OUT / 'source_provenance.json'
assert not target.exists(), target
target.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'export_fbx_matches': [x['matches'] for x in exports],
                  'seven_content_hashes_match_24hero_matrix': [x['matches_previous_24hero_matrix'] for x in content],
                  'report': str(target)}, indent=2))

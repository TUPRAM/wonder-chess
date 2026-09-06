"""Verify the bounded animation revision and emit its exact import list."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids']
changed=[];heroes=[];errors=[];frame_count=0;minimum_floor=100;max_ankle=0;unchanged_count=0
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for uid in ids:
    folder=root/f'reports/WC-330/animation-refinement/{uid}'
    evidence=json.loads((folder/'applied.json').read_text())
    before=json.loads((folder/'manifest-before.json').read_text())
    current=json.loads((root/f'exports/heroes/{uid}/export_manifest.json').read_text())
    expected=set(evidence['exports']);actual=set()
    for name,old_hash in before['files'].items():
        path=root/f'exports/heroes/{uid}/{name}';digest=sha(path)
        if digest!=old_hash:actual.add(name)
        else:unchanged_count+=1
        if current['files'].get(name)!=digest:errors.append(f'{uid}: manifest mismatch {name}')
    if actual!=expected:errors.append(f'{uid}: unexpected export changes {sorted(actual^expected)}')
    if sha(root/f'art-source/heroes/{uid}/{uid}.blend')!=current['source_sha256']:
        errors.append(f'{uid}: source hash mismatch')
    changed.extend(f'exports/heroes/{uid}/{name}' for name in sorted(actual))
    floor=json.loads((folder/'all-mesh-floor.json').read_text())
    frame_count+=sum(r['sampled_frames'] for r in floor)
    minimum_floor=min(minimum_floor,min(r['minimum_all_mesh_vertex_z_m'] for r in floor))
    max_ankle=max(max_ankle,max(r['maximum_defeat_ankle_displacement_m'] for r in floor))
    if not evidence['geometry_weights_uv_rest_unchanged']:errors.append(f'{uid}: source geometry changed')
    heroes.append({'unit_id':uid,'source_revision':current['source_revision'],'source_sha256':current['source_sha256'],
                   'source_before_sha256':evidence['source_before_sha256'],'changed_clips':evidence['changed_clips'],
                   'changed_export_hashes':evidence['exports'],'source_geometry_signature':evidence['geometry_signature']})
if len(changed)!=36:errors.append(f'Expected 36 changed animation files, found {len(changed)}')
report={'status':'failed' if errors else 'production_animation_revision6_stable_verified','hero_count':len(heroes),
        'changed_animation_count':len(changed),'changed_animation_files':changed,'unchanged_export_file_count':unchanged_count,
        'all_mesh_frame_evaluations':frame_count,'minimum_all_mesh_vertex_z_m':minimum_floor,
        'maximum_defeat_ankle_displacement_m':max_ankle,'sampling':'every frame at 60 FPS for each revised clip',
        'heroes':heroes,'errors':errors,'not_proven':['Unreal revision6 reimport','packaged revision6 playback','final art acceptance']}
target=root/'reports/WC-330/animation-refinement-production.json';target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('heroes','changed_animation_files')},indent=2))
if errors:raise SystemExit(1)

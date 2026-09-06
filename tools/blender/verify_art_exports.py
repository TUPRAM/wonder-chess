"""Verify exported bytes against the executed per-hero manifests."""
from pathlib import Path
import hashlib
import json
import argparse

root=Path(__file__).resolve().parents[2]
alpha_ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids']
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+');parser.add_argument('--output',default='reports/WC-330/export-integrity.json')
args=parser.parse_args();ids=args.ids or alpha_ids
if any(uid not in alpha_ids for uid in ids):raise ValueError('Only canonical alpha IDs are valid')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
records=[];errors=[]
for uid in ids:
    out=root/f'exports/heroes/{uid}'
    manifest_path=out/'export_manifest.json'
    manifest=json.loads(manifest_path.read_text())
    source=root/f'art-source/heroes/{uid}/{uid}.blend'
    checked=[]
    if sha(source)!=manifest['source_sha256']:errors.append(f'{uid}: source hash mismatch')
    if sha(root/'data/units.json')!=manifest['units_source_sha256']:errors.append(f'{uid}: canonical data changed after export')
    expected=[f'SK_{uid}{suffix}.fbx' for suffix in ('','_LOD1','_LOD2')]
    expected += [f'AN_{uid}_{clip}.fbx' for clip in ('Idle','Move','Attack','Active','Hit','Defeat','Victory')]
    expected += [f'T_{uid}_{suffix}.png' for suffix in ('BaseColor','Normal','ORM')]+['portrait.png']
    for name in expected:
        path=out/name
        if not path.is_file():errors.append(f'{uid}: missing {name}');continue
        actual=sha(path)
        if actual!=manifest['files'].get(name):errors.append(f'{uid}: hash mismatch {name}')
        checked.append({'file':name,'bytes':path.stat().st_size,'sha256':actual})
    structural=json.loads((root/f'reports/WC-330/{uid}/structural.json').read_text())
    motion=json.loads((root/f'reports/WC-330/{uid}/motion-invariants.json').read_text())
    if structural.get('errors'):errors.append(f'{uid}: structural errors {structural["errors"]}')
    if motion['errors']:errors.append(f'{uid}: motion errors {motion["errors"]}')
    records.append({'unit_id':uid,'revision':manifest['source_revision'],'source':str(source.relative_to(root)),
                    'source_sha256':sha(source),'manifest_sha256':sha(manifest_path),'bones':manifest['bones'],
                    'triangles':manifest['triangles'],'clips':len(manifest['clips']),'lods':manifest['lods'],
                    'motion_samples':sum(c['samples'] for c in motion['clips']),'files':checked})
arena_path=root/'exports/arena/arena_manifest.json'
arena=json.loads(arena_path.read_text())
arena_source=root/'art-source/arena/WC_SevenLanternCourtyard.blend'
if sha(arena_source)!=arena['source_sha256']:errors.append('arena: source hash mismatch')
for name,digest in arena['files'].items():
    path=root/'exports/arena'/name
    if not path.is_file() or sha(path)!=digest:errors.append(f'arena: hash mismatch {name}')
report={'status':'failed' if errors else 'all_recorded_export_bytes_verified','heroes':records,
        'all_alpha_checked':set(ids)==set(alpha_ids),
        'hero_count':len(records),'animation_count':sum(r['clips'] for r in records),
        'hero_file_count':sum(len(r['files']) for r in records),'arena_manifest_sha256':sha(arena_path),
        'errors':errors,'not_proven':['Unreal source parity after reimport','visual acceptance','runtime performance']}
target=root/args.output;target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='heroes'},indent=2))
if errors:raise SystemExit(1)

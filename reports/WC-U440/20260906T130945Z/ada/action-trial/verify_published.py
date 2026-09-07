"""Fresh Blender readback of the promoted source, motion and manifest."""
import hashlib, json, runpy, sys
from pathlib import Path
import bpy

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
UID = 'wc_u_human_guardian'
sys.path.insert(0, str(ROOT/'tools/blender'))
from refine_update_ada import invariants, mesh_geometry_digest, action_curve_digest
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

export = ROOT/f'exports/heroes/{UID}'
source = ROOT/f'art-source/heroes/{UID}/{UID}.blend'
manifest = json.loads((export/'export_manifest.json').read_text())
evidence = json.loads((OUT/'export-result.json').read_text())
assert sha(source) == manifest['source_sha256'] == evidence['source_sha256']
assert sha(export/'export_manifest.json') == evidence['manifest_sha256']
assert manifest['source_revision'] == manifest['animation_revision'] == 8
assert manifest['geometry_source_revision'] == 7
for name, expected in manifest['files'].items(): assert sha(export/name) == expected, name
bpy.ops.wm.open_mainfile(filepath=str(source))
assert mesh_geometry_digest() == evidence['geometry_sha256']
assert invariants(bpy.data.objects['Armature'])['rest_skeleton_sha256'] == evidence['rest_skeleton_sha256']
for name, expected in evidence['unchanged_action_sha256'].items():
    assert action_curve_digest(bpy.data.actions[f'AN_{UID}_{name}']) == expected
saved = sys.argv
try:
    for collection in ('EXPORT', 'LOD_SOURCE'):
        sys.argv = ['inspect_scene.py','--','--collection',collection,'--require-skin',
                    '--output',str(OUT/(collection+'-published-inspection.json'))]
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
    sys.argv = ['audit_motion.py','--','--unit',UID,'--output',str(OUT/'published-motion-invariants.json')]
    runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
finally: sys.argv = saved
checks = ['EXPORT-published-inspection.json','LOD_SOURCE-published-inspection.json','published-motion-invariants.json']
for path in checks: assert not json.loads((OUT/path).read_text()).get('errors'), path
report = {'status':'PUBLISHED_SOURCE_EXPORT_AND_MOTION_CHECKS_PASS',
    'blender_version':bpy.app.version_string,
    'source_revision':8, 'geometry_revision':7, 'animation_revision':8,
    'source_sha256':sha(source), 'manifest_sha256':sha(export/'export_manifest.json'),
    'export_files_verified':len(manifest['files']), 'checks':checks,
    'unchanged_clips':list(evidence['unchanged_action_sha256']),
    'Unreal_reimport_verified':False, 'final_art_accepted':False}
(OUT/'published-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('WC_ADA_REVISION8_READBACK_PASS '+json.dumps(report), flush=True)

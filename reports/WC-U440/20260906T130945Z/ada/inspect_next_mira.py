"""Read-only inspection of the next existing hero; no scene or export promotion."""
import hashlib, json, sys
from pathlib import Path
import bpy

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent/'mira-readonly-inspection'
UID = 'wc_u_human_priest'
sys.path.insert(0, str(ROOT/'tools/blender'))
from refine_update_ada import components, invariants, render_views
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

OUT.mkdir(exist_ok=False)
source = ROOT/f'art-source/heroes/{UID}/{UID}.blend'
manifest_path = ROOT/f'exports/heroes/{UID}/export_manifest.json'
source_hash, manifest_hash = sha(source), sha(manifest_path)
manifest = json.loads(manifest_path.read_text())
assert source_hash == manifest['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source))
arm = bpy.data.objects['Armature']
arm.animation_data.action = bpy.data.actions[f'AN_{UID}_Idle']
arm.animation_data.action_slot = arm.animation_data.action.slots[0]
bpy.context.scene.frame_set(1)
renders = render_views(OUT, 'before')
report = {'status':'READ_ONLY_SOURCE_INSPECTION_NOT_REFINEMENT',
    'blender_version':bpy.app.version_string, 'source':str(source),
    'source_sha256':source_hash, 'manifest_sha256':manifest_hash,
    'invariants':invariants(arm), 'renders':renders,
    'components':components(bpy.data.objects['SK_'+UID]),
    'objects':[{'name':o.name,'type':o.type,'hide_render':o.hide_render} for o in bpy.data.objects]}
assert sha(source) == source_hash and sha(manifest_path) == manifest_hash
(OUT/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')
print('WC_MIRA_READ_ONLY_INSPECTION_PASS', flush=True)

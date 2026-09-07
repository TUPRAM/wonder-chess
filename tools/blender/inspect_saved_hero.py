"""Read one current hero source and render provenance-preserving reference views."""
import argparse, json, sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import sha, components, invariants, render_views
parser=argparse.ArgumentParser();parser.add_argument('--unit',required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);uid=args.unit;out=args.output.resolve()
source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';manifest_path=ROOT/f'exports/heroes/{uid}/export_manifest.json'
source_hash=sha(source);manifest_hash=sha(manifest_path);manifest=json.loads(manifest_path.read_text())
assert source_hash==manifest['source_sha256'];out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature']
action=bpy.data.actions[f'AN_{uid}_Idle'];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
bpy.context.scene.frame_set(1)
report={'status':'READ_ONLY_SOURCE_INSPECTION','source':str(source),'source_sha256':source_hash,
        'manifest_sha256':manifest_hash,'blender_version':bpy.app.version_string,
        'invariants':invariants(arm),'components':components(bpy.data.objects['SK_'+uid]),
        'renders':render_views(out,'before'),'objects':[{'name':o.name,'type':o.type,'hide_render':o.hide_render} for o in bpy.data.objects]}
assert sha(source)==source_hash and sha(manifest_path)==manifest_hash
(out/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')
print('WC_SAVED_HERO_INSPECTION_PASS '+uid,flush=True)

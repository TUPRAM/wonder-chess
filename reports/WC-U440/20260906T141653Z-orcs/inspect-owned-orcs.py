import json,sys
from pathlib import Path
import bpy
root=Path.cwd()
sys.path.insert(0,str(root/'tools/blender'))
from refine_update_ada import sha,components,invariants
out=Path(sys.argv[sys.argv.index('--')+1])
for uid in ('wc_u_orc_warrior','wc_u_orc_mage','wc_u_orc_rogue'):
    source=root/f'art-source/heroes/{uid}/{uid}.blend'
    manifest_path=root/f'exports/heroes/{uid}/export_manifest.json'
    source_hash=sha(source); manifest_hash=sha(manifest_path);manifest=json.loads(manifest_path.read_text())
    assert source_hash==manifest['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source))
    arm=bpy.data.objects['Armature']; mesh=bpy.data.objects['SK_'+uid]
    report={'status':'READ_ONLY_SOURCE_INSPECTION','unit_id':uid,'source':str(source),'source_sha256':source_hash,'manifest_sha256':manifest_hash,'blender_version':bpy.app.version_string,'source_revision':manifest['source_revision'],'invariants':invariants(arm),'components':components(mesh),'objects':[{'name':o.name,'type':o.type,'hide_render':o.hide_render} for o in bpy.data.objects]}
    (out/(uid+'-inspection.json')).write_text(json.dumps(report,indent=2)+'\n')
    assert sha(source)==source_hash and sha(manifest_path)==manifest_hash
    print('WC_READ_ONLY_ORC_INSPECTION '+uid,flush=True)

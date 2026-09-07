import json,sys
from pathlib import Path
import bpy
root=Path.cwd();sys.path.insert(0,str(root/'tools/blender'))
from refine_update_ada import sha,use_clip,render_views
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
meta=json.loads((out/'refinement.json').read_text());candidate=Path(meta['candidate'])
assert sha(candidate)==meta['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(candidate));use_clip(bpy.data.objects['Armature'],'Idle',unit_id=meta['unit_id'])
meta['renders']=render_views(out,'after');meta['status']='SOURCE_REFINEMENT_RENDERED_NOT_PROMOTED'
(out/'refinement.json').write_text(json.dumps(meta,indent=2)+'\n')
assert sha(candidate)==meta['candidate_sha256']
print('WC_ORC_CANDIDATE_RENDER_PASS '+meta['unit_id'],flush=True)

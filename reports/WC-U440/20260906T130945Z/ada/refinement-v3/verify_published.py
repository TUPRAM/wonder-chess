import hashlib,json,runpy,sys
from pathlib import Path
import bpy
root=Path.cwd();out=Path(r'C:/Users/iputu/Documents/Wonder Chess/reports/WC-U440/20260906T130945Z/ada/refinement-v3');sys.path.insert(0,str(root/'tools/blender'))
from refine_update_ada import invariants
manifest=json.loads((root/'exports/heroes/wc_u_human_guardian/export_manifest.json').read_text());previous=json.loads((out/'refinement.json').read_text())
assert invariants(bpy.data.objects['Armature'])==previous['preserved_invariants']
assert hashlib.sha256((root/'art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend').read_bytes()).hexdigest()==manifest['source_sha256']
for name,expected in manifest['files'].items():
 assert hashlib.sha256((root/'exports/heroes/wc_u_human_guardian'/name).read_bytes()).hexdigest()==expected,name
saved=sys.argv
for collection in ['EXPORT','LOD_SOURCE']:
 sys.argv=['inspect_scene.py','--','--collection',collection,'--output',str(out/(collection+'-published-inspection.json')),'--require-skin']
 runpy.run_path(str(root/'tools/blender/inspect_scene.py'),run_name='__main__')
sys.argv=saved
result={'status':'PUBLISHED_SOURCE_AND_EXPORT_CHECKSUMS_PASS','source_sha256':manifest['source_sha256'],'rest_skeleton_actions_preserved':True,'files_checked':len(manifest['files']),'source_revision':manifest['source_revision'],'meshes':[{'name':name,'vertices':len(bpy.data.objects[name].data.vertices)} for name in ['SK_wc_u_human_guardian','SK_wc_u_human_guardian_LOD1','SK_wc_u_human_guardian_LOD2']],'Unreal_import_tested':False}
(out/'published-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

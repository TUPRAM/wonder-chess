import bpy,collections,json
from pathlib import Path
OUT=Path('C:/Users/iputu/Documents/Wonder Chess/exports/lobby')
bpy.ops.wm.open_mainfile(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/lobby/brighthaven_approach.blend')
ob=bpy.data.objects['SM_WC_BrighthavenApproach_LOD2']
def faces(o):return [tuple(sorted(tuple(round(x,4) for x in o.matrix_world@o.data.vertices[i].co) for i in p.vertices)) for p in o.data.polygons]
source=collections.Counter(faces(ob));duplicates=[(k,n) for k,n in source.items() if n>1]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.scale_length=1;bpy.ops.import_scene.fbx(filepath=str(OUT/'SM_WC_BrighthavenApproach_LOD2.fbx'),use_anim=False)
ob=[o for o in bpy.context.scene.objects if o.type=='MESH'][0];actual=collections.Counter(faces(ob))
report={'duplicate_source_faces':duplicates,'source_minus_fbx':list((source-actual).items()),'fbx_minus_source':list((actual-source).items())}
(OUT/'review/lod2-topology-diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report)[:8000])

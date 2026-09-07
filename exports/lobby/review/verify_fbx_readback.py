"""Independent saved-source and nine-FBX roundtrip; this is not Unreal acceptance."""
import hashlib,json,math
from pathlib import Path
import bpy
from mathutils import Vector
OUT=Path('C:/Users/iputu/Documents/Wonder Chess/exports/lobby')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'lobby_manifest.json').read_text());source=Path(manifest['source'])
assert sha(source)==manifest['source_sha256'],'Source hash mismatch'
for name,digest in manifest['files'].items():assert sha(OUT/name)==digest,name
bpy.ops.wm.open_mainfile(filepath=str(source));source_measurements={}
for name in manifest['modules']+[x['mesh'] for x in manifest['lods']]:
    ob=bpy.data.objects[name];points=[ob.matrix_world@v.co for v in ob.data.vertices];ob.data.calc_loop_triangles()
    source_measurements[name]={'min_m':[min(v[i] for v in points) for i in range(3)],'max_m':[max(v[i] for v in points) for i in range(3)],'triangles':len(ob.data.loop_triangles)}
results=[]
for name,expected in source_measurements.items():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    bpy.ops.import_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_anim=False)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1,(name,len(meshes));ob=meshes[0]
    points=[ob.matrix_world@v.co for v in ob.data.vertices];assert all(math.isfinite(x) for v in points for x in v)
    measured={'min_m':[min(v[i] for v in points) for i in range(3)],'max_m':[max(v[i] for v in points) for i in range(3)]};ob.data.calc_loop_triangles()
    dims=[measured['max_m'][i]-measured['min_m'][i] for i in range(3)];expected_dims=[expected['max_m'][i]-expected['min_m'][i] for i in range(3)]
    assert all(abs(a-b)<.001 for a,b in zip(dims,expected_dims)),(name,dims,expected_dims)
    assert len(ob.data.loop_triangles)==expected['triangles'],(name,len(ob.data.loop_triangles),expected['triangles'])
    assert len(ob.data.uv_layers)==1 and len(ob.data.materials)==1,name
    assert all(math.isfinite(x) and -.001<=x<=1.001 for uv in ob.data.uv_layers.active.data for x in uv.uv),name
    results.append({'mesh':name,'dimensions_m':dims,'world_bounds':measured,'source_bounds':expected,'object_scale':list(ob.scale),'triangles':len(ob.data.loop_triangles),'uv_layers':len(ob.data.uv_layers),'materials':len(ob.data.materials)})
report={'status':'PASS_BLENDER_SOURCE_AND_FBX_ROUNDTRIP_ONLY','blender_version':bpy.app.version_string,'source_sha256':sha(source),'manifest_sha256':sha(OUT/'lobby_manifest.json'),'verified_file_hashes':len(manifest['files']),'fbx_readbacks':results,'unreal_import_verified':False,'final_art_accepted':False}
(OUT/'review/fbx-readback.json').write_text(json.dumps(report,indent=2)+'\n');print('WC_LOBBY_FBX_ROUNDTRIP_PASS '+str(len(results)),flush=True)

import json,shutil,sys
from pathlib import Path
import bpy
from mathutils import Vector
root=Path.cwd();sys.path.insert(0,str(root/'tools/blender'))
from refine_update_ada import sha,use_clip
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();meta=json.loads((out/'refinement.json').read_text());uid=meta['unit_id']
assert uid=='wc_u_orc_mage';bpy.ops.wm.open_mainfile(filepath=meta['candidate']);use_clip(bpy.data.objects['Armature'],'Idle',unit_id=uid)
scene=bpy.context.scene;cam=scene.camera;cam.location=(3,5,2.7);cam.rotation_euler=(Vector((0,0,1.08))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';bpy.context.view_layer.update()
mesh=bpy.data.objects['SK_'+uid].evaluated_get(bpy.context.evaluated_depsgraph_get());geo=mesh.to_mesh();inverse=cam.matrix_world.inverted()
try:points=[inverse@(mesh.matrix_world@v.co) for v in geo.vertices]
finally:mesh.to_mesh_clear()
lo=[min(p[a] for p in points) for a in (0,1)];hi=[max(p[a] for p in points) for a in (0,1)]
cam.location+=cam.matrix_world.to_3x3()@Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,0));cam.data.ortho_scale=max(hi[a]-lo[a] for a in (0,1))*1.14
scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.image_settings.file_format='PNG'
framed=out/'after-three-quarter-framed.png';assert not framed.exists();scene.render.filepath=str(framed);bpy.ops.render.render(write_still=True)
shutil.copy2(out/'after-three-quarter.png',out/'portrait-before-framing.png');shutil.copy2(framed,out/'after-three-quarter.png')
(out/'portrait-framing.json').write_text(json.dumps({'source_candidate_sha256':sha(Path(meta['candidate'])),'method':'Actual posed mesh projected bounds with14percent margin; original Cycles material rendering','orthographic_scale_m':cam.data.ortho_scale,'portrait':str(framed),'sha256':sha(framed),'retained_cropped_source':str(out/'portrait-before-framing.png')},indent=2)+'\n')

import bpy,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];SOURCE=R/'ada_bw6_side_return_r002_context.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
names=json.loads(s['BW6_side_return_owned'])
def signature(o):
 return hashlib.sha256(str(([(tuple(v.co),[(o.vertex_groups[g.group].name,round(g.weight,8)) for g in v.groups]) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(m.name,m.type,m.show_viewport,m.show_render) for m in o.modifiers])).encode()).hexdigest()
before={n:signature(bpy.data.objects[n]) for n in names}
out=R/'ada_bw6_side_return_work.blend';frozen=R/'ada_bw6_side_return_checkpoint_r001_REVIEW_CANDIDATE.blend'
assert not out.exists() and not frozen.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(out));shutil.copyfile(out,frozen)
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
after={n:signature(bpy.data.objects[n]) for n in names};assert before==after
rec={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'checkpoint':str(frozen),'sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'work':str(out),'save_reopen_signatures':after,'owned':names,'status':'LOCAL_REVIEW_CANDIDATE','actual_game_clips':'NOT_RUN','reviewer_approval':'NOT_ISSUED','captures':[]}
s.cycles.samples=12;s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=960;s.render.resolution_percentage=100
def render(name,frame=1):
 s.frame_set(frame);s.render.filepath=str(R/'captures'/name);bpy.ops.render.render(write_still=True);rec['captures'].append({'path':s.render.filepath,'frame':frame,'camera':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world]})
clay=bpy.data.materials.new('BW6_SIDE_DIAGNOSTIC_CLAY');clay.use_nodes=True;p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.42,.40,.38,1);p.inputs['Roughness'].default_value=.67
s.view_layers[0].material_override=clay;s.camera=bpy.data.objects['BW4_Camera_three_quarter']
render('frozen_clay_three_quarter.png');render('frozen_clay_pose49.png',49);render('frozen_clay_pose73.png',73)
s.frame_set(1)
for o in s.objects:
 if o.type=='LIGHT':o.location.y=-o.location.y;o.rotation_euler=(Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler()
render('frozen_reversed_clay.png')
for o in s.objects:
 if o.type=='MESH' and o.name not in names:o.hide_render=True
for n in names:
 o=bpy.data.objects[n]
 for m in o.modifiers:
  if m.type in ['SUBSURF','SOLIDIFY','BEVEL']:m.show_render=False
 w=o.modifiers.new('Actual raw cage edges diagnostic','WIREFRAME');w.thickness=.00055;w.use_replace=False;w.offset=1
data=bpy.data.cameras.new('BW6_SIDE_ACTUAL_CAGE');camera=bpy.data.objects.new('BW6_SIDE_ACTUAL_CAGE',data);s.collection.objects.link(camera);camera.location=(1.05,.58,1.43);camera.rotation_euler=(Vector((.18,-.005,1.28))-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=.32;s.camera=camera
render('frozen_actual_control_cage.png')
(R/'records/verification.json').write_text(json.dumps(rec,indent=2))
assert hashlib.sha256(frozen.read_bytes()).hexdigest()==rec['sha256'];print('FROZEN_REOPEN_CAPTURE_DONE')

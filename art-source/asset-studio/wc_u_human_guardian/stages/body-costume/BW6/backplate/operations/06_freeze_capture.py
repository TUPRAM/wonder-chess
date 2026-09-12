import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];source=R/'ada_bw6_backplate_correction2.blend';baseline=R.parent/'armor/ada_bw6_torso_recut_neck.blend'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);o=bpy.data.objects['BW6_BackPlate_Rebuilt']
o['BW6_scope']='Upper back/armhole recut and connected local edge bands. Main lower profiles and original hem boundary retained; one internal lower support row repositioned for safe band curvature.'
o['BW6_edge_construction']='Narrow overlapping rims retired; broad connected neck/hem raised bands share one 3.5mm Solidify wall. Upper and lower boundary points are retained. This is stylized edge construction, not a historically exact rolled rim.'
s['BW6_backplate_status']='LOCAL_CANDIDATE_REVIEW_REQUIRED';s['BW6_backplate_human_approval']=False;s['BW6_backplate_runtime']='NOT_RUN'
s['BW6_backplate_replaces']=json.dumps(['BW6_BackPlate','BW6_Back_Neck_TurnedBorder','BW6_Back_Hem_TurnedBorder']);s['BW6_backplate_append_objects']=json.dumps([o.name])
work=R/'ada_bw6_backplate_work.blend';frozen=R/'ada_bw6_backplate_checkpoint_REVIEW.blend';s.camera=bpy.data.objects['BW4_Camera_back'];bpy.ops.wm.save_as_mainfile(filepath=str(work));bpy.ops.wm.save_as_mainfile(filepath=str(frozen),copy=True)
digest=sha(frozen);report={'source':str(source),'source_sha256':sha(source),'baseline':str(baseline),'baseline_sha256':sha(baseline),'work':str(work),'work_sha256':sha(work),'frozen':str(frozen),'frozen_sha256':digest,'captures':[],'source_saved_before_capture':True}
def render(name):
 p=R/'captures'/name;s.render.filepath=str(p);bpy.ops.render.render(write_still=True);report['captures'].append({'path':str(p),'sha256':sha(p),'source_sha256':digest,'frame':s.frame_current,'camera':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world]})
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='OBJECT';s.display.shading.light='STUDIO';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
for ob in s.objects:
 if ob.type=='MESH':ob.color=(.55,.55,.55,1)
for fr in [1,49,73,97]:
 s.frame_set(fr)
 for view in (['back','profile'] if fr!=1 else ['back','profile','three_quarter']):s.camera=bpy.data.objects['BW4_Camera_'+view];render(f'retained_context_{view}_{fr}.png')
s.frame_set(1)
for ob in s.objects:
 if ob.type=='MESH' and ob.name not in [o.name,'BW6_PaddedCoat_Tailored']:ob.hide_render=True
bpy.data.objects['BW6_PaddedCoat_Tailored'].color=(.36,.17,.13,1)
for view in ['back','profile']:s.camera=bpy.data.objects['BW4_Camera_'+view];render(f'retained_pair_{view}.png')
# Actual control edges over the raw shell, not a remeshed cage illustration.
bpy.data.objects['BW6_PaddedCoat_Tailored'].hide_render=True
mods=[m for m in o.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
for m in mods:m.show_render=False
w=bpy.data.objects.new('BW6_Backplate_Actual_Cage',o.data.copy());s.collection.objects.link(w);w.color=(.018,.022,.03,1);w.matrix_world=o.matrix_world.copy();md=w.modifiers.new('Actual source edges','WIREFRAME');md.thickness=.00055
s.camera=bpy.data.objects['BW4_Camera_back'];render('retained_actual_cage_back.png');bpy.data.objects.remove(w,do_unlink=True)
for m in mods:m.show_render=True
# True surface lighting reversal exposes the ridge and edge bands.
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4
for ob in s.objects:
 if ob.type=='LIGHT':ob.hide_render=True
mat=bpy.data.materials.new('BW6_Backplate_Uniform_Clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.34,.34,.34,1);bs.inputs['Roughness'].default_value=.66;o.data.materials.clear();o.data.materials.append(mat)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.2
target=Vector((0,-.15,1.345));d=bpy.data.lights.new('BW6_Backplate_DiagnosticKey','AREA');lamp=bpy.data.objects.new(d.name,d);s.collection.objects.link(lamp);d.energy=95;d.size=.8
for sign,label in [(1,'key'),(-1,'reversed_key')]:
 lamp.location=(sign*.6,-1.1,1.9);lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler();render('retained_uniform_clay_'+label+'.png')
assert sha(frozen)==digest
(R/'records/capture_manifest.json').write_text(json.dumps(report,indent=2));print('BACKPLATE_FROZEN',digest)

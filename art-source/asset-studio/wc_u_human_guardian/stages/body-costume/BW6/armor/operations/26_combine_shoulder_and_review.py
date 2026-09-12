import bpy,json,importlib.util,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_upper_color_layout_work.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig']
path=R.parent/'shoulder/operations/append_bw6_shoulder_r003.py';spec=importlib.util.spec_from_file_location('bw6_append_shoulder',path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);added=helper.append_bw6_shoulder(s,rig)
steel=bpy.data.materials['BW6_ColorLayout_Steel'];clay=bpy.data.materials.get('BW6_Review_Clay') or bpy.data.materials.new('BW6_Review_Clay')
clay.use_fake_user=True;clay.use_nodes=True;clay.diffuse_color=(.43,.43,.43,1)
clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.43,.43,.43,1)
clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72
for n in added['parts']:
 o=bpy.data.objects[n];o.data.materials.clear();o.data.materials.append(steel)
plate=bpy.data.objects['BW6_FrontPlate']
for f in plate.data.polygons:f.use_smooth=True
for e in plate.data.edges:
 a,b=e.vertices;e.use_edge_sharp=(a%7==3 and b%7==3) or (a//7==2 and b//7==2)
normal=plate.modifiers.new('Manufactured broad field normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50
coat=bpy.data.objects['BW6_PaddedCoat_Tailored']
for f in coat.data.polygons:
 p=f.center;in_collar=(p.x/.14)**2+((p.y+.05)/.13)**2<1.24
 f.material_index=int((p.z<1.245 and abs(p.x)<.21) or (p.z>1.465 and in_collar and p.x>0))
owned=json.loads(s['BW6_owned_visible_parts']);s['BW6_owned_visible_parts']=json.dumps(owned+added['parts']);s['BW6_combined_sources']=json.dumps({'torso':'ada_bw6_upper_color_layout_work.blend','shoulder':added['source']});s['BW6_combined_status']='ART_REVISE; combined surface and motion tests pending, legacy left shoulder and bracers contextual.'
for layer in s.view_layers:layer.material_override=None
out=R/'ada_bw6_upper_combined_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
s.cycles.samples=20;s.render.threads=4
for pose in ['rest','lowered',49]:
 if pose=='lowered':
  s.frame_set(1);action=rig.animation_data.action;rig.animation_data.action=None
  matrices={p.name:p.matrix_basis.copy() for p in rig.pose.bones};modes={p.name:p.rotation_mode for p in rig.pose.bones}
  for p in rig.pose.bones:p.matrix_basis.identity()
  for side in ['R','L']:
   p=rig.pose.bones['upperarm01.'+side];basis=rig.matrix_world@p.bone.matrix_local;ax=(basis.to_3x3().inverted()@Vector((0,1,0))).normalized();p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion(ax,math.radians(32 if side=='R' else -32))
  ha=helper.apply_lowered_support_pose();bpy.context.view_layer.update()
 elif isinstance(pose,int):s.frame_set(pose)
 for kind in ['clay','color_layout']:
  for layer in s.view_layers:layer.material_override=clay if kind=='clay' else None
  for view in (['front','three_quarter'] if pose!='rest' else ['three_quarter']):
   s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/f'combined_r001_{pose}_{kind}_{view}.png');bpy.ops.render.render(write_still=True)
 if pose=='lowered':
  rig.animation_data.action=action
  for p in rig.pose.bones:p.rotation_mode=modes[p.name];p.matrix_basis=matrices[p.name]
  bpy.data.objects['BW6_R_Cap_SecondaryHinge'].animation_data.action=ha;s.frame_set(1)
(R/'records/combined_r001_sources.json').write_text(json.dumps({'source':str(out),'shoulder':added,'poses':['authoring frame1','independent world-axis32deg lowered diagnostic','authoring frame49'],'material_scope':'diagnostic layout; not textures/material approval'},indent=2));print('BW6_COMBINED_REVIEW_COMPLETE')

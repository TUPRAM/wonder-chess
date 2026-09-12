import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw5_armor_correction2.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig']
failed=bpy.data.objects['BW5_Tailored_Collar'];failed.hide_render=True;failed.hide_set(True);failed['status']='REJECTED_COLLAR_FOLDS_RETAINED_FOR_INSPECTION'
old=bpy.data.objects['BW4_CONTEXT_BW1_PaddedCollar'];old.hide_render=False;old.hide_set(False)
old['BW5_scope']='UNCHANGED BW4 CONTEXT; collar proportion/neckline rebuild unresolved.'
active=[x for x in json.loads(s['armor_parts']) if x!=failed.name and 'Pauldron' not in x]
s['BW5_owned_visible_parts']=json.dumps(active)
s['BW5_failed_parts']=json.dumps([failed.name])
s['BW5_context_notice']='BW4 collar and both shoulders, old head/neck, bracers, hands and lower costume are unresolved context. BW5 rejected shoulder and glove proofs remain separate files.'
s['BW5_scope']='Front/back plate proportion correction; retained navy waist experiment and side returns ART_REVISE; failed new collar hidden, unchanged BW4 collar restored. No game candidate.'
# Duplicate only the visible assembly into an independent posing context.
rs=bpy.data.scenes.new('BW5_REFERENCE_POSE_APPROXIMATE');rs.world=s.world
rc=bpy.data.collections.new('BW5_REFERENCE_POSE_ONLY');rs.collection.children.link(rc)
rr=rig.copy();rr.data=rig.data.copy();rr.name='BW5_ReferencePose_Rig';rc.objects.link(rr);rr.animation_data_clear()
for pb in rr.pose.bones:pb.matrix_basis=Matrix.Identity(4)
copies={rig:rr}
visible=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
for o in visible:
    n=o.copy();n.name='BW5_REF_'+o.name;rc.objects.link(n);n.hide_set(False);copies[o]=n
    if n.animation_data:n.animation_data_clear()
    for m in n.modifiers:
        if m.type=='ARMATURE' and m.object==rig:m.object=rr
for o,n in copies.items():
    if o==rig:continue
    if o.parent in copies:
        n.parent=copies[o.parent];n.matrix_parent_inverse=o.matrix_parent_inverse.copy();n.matrix_basis=o.matrix_basis.copy()
for o in s.objects:
    if o.type=='LIGHT':rc.objects.link(o)
bpy.context.window.scene=rs;bpy.context.view_layer.update()
pose={}
for name,angle in [('upperarm01.R',30),('upperarm01.L',-30)]:
    pb=rr.pose.bones[name];world=rr.matrix_world@pb.matrix;h=world.translation.copy()
    rot=Matrix.Translation(h)@Matrix.Rotation(math.radians(angle),4,'Y')@Matrix.Translation(-h)
    pb.matrix=rr.matrix_world.inverted()@rot@world;bpy.context.view_layer.update()
    pb.keyframe_insert(data_path='rotation_euler',frame=1)
    pose[name]={'world_Y_delta_degrees':angle,'matrix_basis':[list(x) for x in pb.matrix_basis]}
if rr.animation_data and rr.animation_data.action:rr.animation_data.action.name='BW5_Approximate_Lowered_Reference_Pose_ONLY'
target=Vector((0,-.045,1.34));cams={}
for name,loc in [('front',(0,3,1.34)),('back',(0,-3,1.34)),('right',(3,-.045,1.34)),('left',(-3,-.045,1.34)),('three_quarter',(2.4,3.2,1.68))]:
    d=bpy.data.cameras.new('BW5_Reference_'+name);o=bpy.data.objects.new(d.name,d);rc.objects.link(o);o.location=loc;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=.92;cams[name]=o
for scene in [s,rs]:
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=960;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.render.film_transparent=False
rs.camera=cams['front'];rs['scope']='Approximate reference-like lowered arms on separate rig/action; unchanged body/rest/source motion. Painted reference perspective and covered anchors prevent exact registration.'
pose['body_anchors_m']={'clavicle_midpoint':[0,-.04501,1.461896],'natural_waist_spine03_head':[0,-.07005,1.098645]}
pose['cameras']={k:{'matrix_world':[list(r) for r in o.matrix_world],'type':o.data.type,'ortho_scale':o.data.ortho_scale,'resolution':[960,960]} for k,o in cams.items()}
(R/'reference_pose.json').write_text(json.dumps(pose,indent=2))
bpy.context.window.scene=s;s.frame_set(1);s.camera=bpy.data.objects['BW4_Camera_three_quarter']
s['status']='ART_REVISE';s['human_approval']='NOT_ISSUED';s['runtime']='NOT_RUN'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_armor_work.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_armor_checkpoint_ART_REVISE.blend'),copy=True)
def render(scene,name,camera,frame=1):
    bpy.context.window.scene=scene;scene.frame_set(frame);scene.camera=camera;scene.render.filepath=str(R/'captures'/f'{name}.png');bpy.ops.render.render(write_still=True)
for v in ['front','back','profile','three_quarter','rear_three_quarter','context']:
    render(s,'retained_'+v,bpy.data.objects['BW4_Camera_'+v])
for fr in [20,28,29,49,54,73]:render(s,f'retained_pose_{fr:03}',bpy.data.objects['BW4_Camera_three_quarter'],fr)
key=bpy.data.objects['BW4_Key'];location=key.location.copy();rotation=key.rotation_euler.copy();key.location.x=-key.location.x;key.rotation_euler=(Vector((0,0,1.3))-key.location).to_track_quat('-Z','Y').to_euler()
render(s,'retained_reversed_key',bpy.data.objects['BW4_Camera_three_quarter']);key.location=location;key.rotation_euler=rotation
for v,o in cams.items():render(rs,'reference_pose_'+v,o)
# Actual cage edges, separately labeled; this is not the smoothed render with a fake grid.
bpy.context.window.scene=s;s.frame_set(1)
black=bpy.data.materials.new('BW5_CageEdges');black.diffuse_color=(.008,.008,.008,1);black.use_nodes=True;black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.008,.008,.008,1)
for name in active:
    ob=bpy.data.objects[name]
    for m in ob.modifiers:
        if m.type in ['SUBSURF','BEVEL','SOLIDIFY']:m.show_render=False
    ob.data.materials.append(black);m=ob.modifiers.new('ACTUAL_CONTROL_EDGES','WIREFRAME');m.use_replace=False;m.thickness=.00065;m.use_even_offset=False;m.material_offset=len(ob.data.materials)-1
render(s,'retained_actual_control_cage',bpy.data.objects['BW4_Camera_three_quarter'])
for name in active:
    ob=bpy.data.objects[name];ob.modifiers.remove(ob.modifiers['ACTUAL_CONTROL_EDGES']);ob.data.materials.pop(index=len(ob.data.materials)-1)
    for m in ob.modifiers:m.show_render=True
# A color-ID image distinguishes the new waist coverage without claiming texturing.
for layer in s.view_layers:layer.material_override=None
navy=bpy.data.objects['BW5_Navy_Waist_Enclosure'];navy.data.materials.clear();mat=bpy.data.materials.new('BW5_Navy_ID_ONLY');mat.diffuse_color=(.022,.040,.073,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color;navy.data.materials.append(mat)
render(s,'retained_waist_color_ID_NOT_TEXTURED',bpy.data.objects['BW4_Camera_front'])
print('BW5_DELIVERY_VIEWS_COMPLETE',flush=True)

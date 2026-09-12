import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

out=Path(__file__).parent
source=out.parents[2]/'BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend'
expected='03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene;scene.frame_set(1)
rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];glove=bpy.data.objects['BW1_Glove_Pair_SourceFit']
names=[b.name for b in rig.pose.bones if b.name.endswith('.R') and ('finger' in b.name or 'wrist' in b.name or 'metacarpal' in b.name)]
prior={n:rig.pose.bones[n].matrix_basis.copy() for n in names}
action=rig.animation_data.action if rig.animation_data else None
if rig.animation_data:rig.animation_data.action=None
for n in names:
    if 'finger' in n:rig.pose.bones[n].matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();re=rig.evaluated_get(dg)
def point(n,tail=False):
    pb=re.pose.bones[n];return re.matrix_world@(pb.tail if tail else pb.head)
O=point('wrist.R');M=point('finger3-1.R');I=point('finger2-1.R');L=point('finger5-1.R');T=point('finger3-3.R',True)
Y=(M-O).normalized();rx=I-L;X=(rx-rx.dot(Y)*Y).normalized();Z=X.cross(Y).normalized();C=(O+M)/2
g=glove.evaluated_get(dg);mesh=g.to_mesh();world=[g.matrix_world@v.co for v in mesh.vertices];polys=[tuple(p.vertices) for p in mesh.polygons];bvh=BVHTree.FromPolygons(world,polys)
surfaces={}
for label,sign in [('positive',1),('negative',-1)]:
    loc,normal,index,distance=bvh.ray_cast(C+Z*.07*sign,-Z*sign,.14)
    surfaces[label]={'world':list(loc) if loc else None,'normal_world':list(normal) if normal else None,'evaluated_face_index':index,'ray_distance_m':distance,'signed_plane_distance_m':(loc-C).dot(Z) if loc else None}
report={'source':str(source),'source_sha256':expected,'scene':scene.name,'units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length,'length_unit':scene.unit_settings.length_unit},'frame':1,'open_calibration':'Only anatomical-right finger basis transforms temporarily set to identity; action temporarily detached; arm chain kept at saved frame1 pose. No save.','saved_finger_basis':{n:[list(r) for r in prior[n]] for n in prior},'rig_matrix_world':[list(r) for r in re.matrix_world],'glove_matrix_world':[list(r) for r in g.matrix_world],'bones':{},'landmarks_world_BU':{'wrist':list(O),'middle_MCP':list(M),'index_MCP':list(I),'little_MCP':list(L),'middle_tip':list(T)},'provisional_joint_plane_frame':{'origin':list(O),'X_to_index':list(X),'Y_distal':list(Y),'Z_UNCLASSIFIED':list(Z),'middle_tip_direction_dot_Y':(T-M).normalized().dot(Y),'palm_joint_midpoint':list(C)},'glove_surface_candidates':surfaces,'glove_evaluated_vertex_count':len(mesh.vertices),'glove_modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render} for m in glove.modifiers]}
for n in names:
    b=rig.data.bones[n];pb=re.pose.bones[n]
    report['bones'][n]={'parent':b.parent.name if b.parent else None,'rest_matrix_armature':[list(r) for r in b.matrix_local],'pose_matrix_armature':[list(r) for r in pb.matrix],'world_pose_matrix':[list(r) for r in re.matrix_world@pb.matrix],'world_head':list(point(n)),'world_tail':list(point(n,True)),'rotation_mode':rig.pose.bones[n].rotation_mode,'constraints':[(c.name,c.type,c.mute,c.influence) for c in pb.constraints]}
g.to_mesh_clear()
(out/'open_inspection.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ('units','landmarks_world_BU','provisional_joint_plane_frame','glove_surface_candidates','glove_evaluated_vertex_count')}),flush=True)

# Unsaved diagnostic views: only the evaluated glove, never a handle or grip.
for o in scene.objects:o.hide_render=True
glove.hide_render=False
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.63,.63,.63);scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.world.color=(.07,.07,.07);scene.use_nodes=False
camdata=bpy.data.cameras.new('BW2_TEMP_independent_camera');cam=bpy.data.objects.new('BW2_TEMP_independent_camera',camdata);scene.collection.objects.link(cam);camdata.type='ORTHO';camdata.ortho_scale=.25;scene.camera=cam
target=(O+T)*.5
for label,axis in [('joint_positive_Z',Z),('joint_negative_Z',-Z),('joint_index_side',X)]:
    cam.location=target+axis*.6
    viewz=axis.normalized();viewy=Y;viewx=viewy.cross(viewz).normalized();viewy=viewz.cross(viewx).normalized()
    cam.matrix_world=Matrix(((viewx.x,viewy.x,viewz.x,cam.location.x),(viewx.y,viewy.y,viewz.y,cam.location.y),(viewx.z,viewy.z,viewz.z,cam.location.z),(0,0,0,1)))
    scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
for n,m in prior.items():rig.pose.bones[n].matrix_basis=m
if rig.animation_data:rig.animation_data.action=action
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected

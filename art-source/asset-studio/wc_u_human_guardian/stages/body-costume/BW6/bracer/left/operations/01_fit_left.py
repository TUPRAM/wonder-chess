import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];SOURCE=R.parent/'ada_bw6_bracer_checkpoint_r002_REVIEW_CANDIDATE.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);srcscene=bpy.data.scenes['BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=srcscene;srcscene.frame_set(1)
src_rig=bpy.data.objects['BW6_Bracer_Independent_Rig'];M=Matrix.Diagonal((-1.,1.,1.,1.));bone_names=[b.name for b in src_rig.data.bones if b.name.endswith('.R') and any(b.name.startswith(n) for n in ['clavicle','shoulder','upperarm','lowerarm','wrist','finger','metacarpal'])]
# Snapshot actual authored right world deltas, independently from left bone rolls/rest matrices.
targets={}
for f in range(1,98):
 srcscene.frame_set(f);bpy.context.view_layer.update();targets[f]={}
 for n in bone_names:
  rest=src_rig.matrix_world@src_rig.data.bones[n].matrix_local;pose=src_rig.matrix_world@src_rig.pose.bones[n].matrix
  ln=n.removesuffix('.R')+'.L';leftrest=src_rig.matrix_world@src_rig.data.bones[ln].matrix_local
  targets[f][ln]=M@(pose@rest.inverted())@M@leftrest
srcscene.frame_set(1)
s=bpy.data.scenes.new('BW6_LEFT_BRACER_AUTHORING_ONLY');bpy.context.window.scene=s;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.world=srcscene.world.copy();s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=3;s.render.fps=24;s.frame_start=1;s.frame_end=97;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1.3
col=bpy.data.collections.new('BW6_LEFT_BRACER_NEW_SURFACES');s.collection.children.link(col);ctxcol=bpy.data.collections.new('BW6_LEFT_BRACER_SOURCE_CONTEXT');s.collection.children.link(ctxcol)
rig=src_rig.copy();rig.data=src_rig.data.copy();rig.name='BW6_LeftBracer_Independent_Rig';ctxcol.objects.link(rig);rig.animation_data.action=src_rig.animation_data.action.copy();rig.animation_data.action.name='BW6_LeftBracer_WorldDelta97_AUTHORING_NOT_GAME'
ctx=[]
for nm in json.loads(srcscene['BW6_bracer_context']):
 old=bpy.data.objects[nm];o=old.copy();o.data=old.data.copy();o.name=old.name.replace('BW6_Bracer_CONTEXT_','BW6_LeftBracer_CONTEXT_');ctxcol.objects.link(o)
 for md in o.modifiers:
  if md.type=='ARMATURE':md.object=rig
 if o.parent==src_rig:o.parent=rig
 o.hide_render=False;o.hide_set(False);ctx.append(o);assert o.data!=old.data
owned=[]
for nm in json.loads(srcscene['BW6_bracer_owned']):
 old=bpy.data.objects[nm];o=old.copy();o.data=old.data.copy();o.name=nm.replace('BW6_R_Bracer_','BW6_L_Bracer_');col.objects.link(o);o.matrix_world=Matrix.Identity(4)
 for v,ov in zip(o.data.vertices,old.data.vertices):v.co=M@(old.matrix_world@ov.co)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 for vg in o.vertex_groups:
  if vg.name.endswith('.R'):vg.name=vg.name.removesuffix('.R')+'.L'
 for md in o.modifiers:
  if md.type=='ARMATURE':md.object=rig
 o['owner_bone']=str(old.get('owner_bone','')).replace('.R','.L');o['method']='World-X reflected new right cage with reversed winding; actual left rest bones and explicit world-delta articulation, not copied Euler signs.';o.hide_render=False;o.hide_set(False);owned.append(o)
# Bake the geometric motion mapping into the independent left action only.
ordered=sorted(targets[1],key=lambda n:len(rig.data.bones[n].parent_recursive));maxerr=0
for f,row in targets.items():
 s.frame_set(f)
 for n in ordered:
  p=rig.pose.bones[n];p.rotation_mode='QUATERNION';p.matrix=rig.matrix_world.inverted()@row[n];bpy.context.view_layer.update()
  p.keyframe_insert('location',frame=f);p.keyframe_insert('rotation_quaternion',frame=f);p.keyframe_insert('scale',frame=f)
 for n in ordered:
  actual=rig.matrix_world@rig.pose.bones[n].matrix;maxerr=max(maxerr,max(abs(actual[i][j]-row[n][i][j]) for i in range(4) for j in range(4)))
for lay in rig.animation_data.action.layers:
 for st in lay.strips:
  for bag in st.channelbags:
   for curve in bag.fcurves:
    if '.L' in curve.data_path:
     for k in curve.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);bpy.context.view_layer.update()
W=rig.matrix_world@rig.data.bones['wrist.L'].head_local;E=rig.matrix_world@rig.data.bones['lowerarm01.L'].head_local;A=(E-W).normalized()
I=rig.matrix_world@rig.data.bones['finger2-1.L'].head_local;P=rig.matrix_world@rig.data.bones['finger5-1.L'].head_local;C=rig.matrix_world@rig.data.bones['finger3-1.L'].head_local
Y=(C-W).normalized();X=(I-P);X=(X-Y*X.dot(Y)).normalized();N=X.cross(Y).normalized()
body=next(o for o in ctx if o.name.endswith('IndexedBody'));vg=body.vertex_groups.get('fingernails');normal=Vector((0,0,0));samples=0
for v in body.data.vertices:
 p=body.matrix_world@v.co
 if p.x<-.45 and any(g.group==vg.index and g.weight>.4 for g in v.groups):normal+=body.matrix_world.to_3x3().inverted().transposed()@v.normal;samples+=1
normal.normalize()
if N.dot(normal)<0:N=-N
D=(N-A*N.dot(A)).normalized();T=A.cross(D).normalized();target=W+A*.085
axes={'wrist':list(W),'elbow':list(E),'index_MCP':list(I),'little_MCP':list(P),'middle_MCP':list(C),'distal_hand':list(Y),'transverse_hand_toward_index':list(X),'dorsal_nail_normal':list(normal),'nail_vertices':samples,'dorsal_plane_agreement':N.dot(normal),'proximal':list(A),'dorsal':list(D),'transverse':list(T),'bone_axes_world':{n:[list(x) for x in rig.matrix_world@rig.data.bones[n].matrix_local] for n in ['wrist.L','lowerarm01.L','lowerarm02.L']}}
for label,offset,scale in [('Dorsal',D*.65+A*.07,.39),('Volar',-D*.65+A*.03,.39),('Side',T*.65+A*.06,.39),('ThreeQuarter',D*.52+T*.35-A*.09,.39),('Axial',-A*.65+D*.05,.20)]:
 d=bpy.data.cameras.new('BW6_LeftBracer_Camera_'+label);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=target+offset;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
for nm,loc,power,size in [('Key',target+D*.55+T*.3+A*.2,35,.42),('Fill',target-D*.4-T*.3,18,.5),('Rim',target+T*.6+A*.15,25,.4)]:
 d=bpy.data.lights.new('BW6_LeftBracer_'+nm,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler()
s['BW6_bracer_owned']=json.dumps([o.name for o in owned]);s['BW6_bracer_context']=json.dumps([o.name for o in ctx]);s['BW6_bracer_frame']=json.dumps(axes);s['runtime_status']='LEFT_AUTHORING_FIT_NOT_GAME_OR_HUMAN_APPROVED';s.camera=bpy.data.objects['BW6_LeftBracer_Camera_ThreeQuarter']
out=R/'ada_bw6_left_bracer_initial.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/left_calibration_and_mapping.json').write_text(json.dumps({'right_source':str(SOURCE),'right_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'candidate':str(out),'frame':axes,'motion_method':'Reflected world-space posed/rest deltas multiplied by each actual left rest bone, then baked into independent action. No copied Euler signs.','mapped_bones':ordered,'97_integer_pose_max_world_matrix_error':maxerr,'body_glove_coat_copies_independent':True,'new_geometry_only_reflected':True,'reversed_mesh_winding':True},indent=2))
print('LEFT_NATIVE_READY',maxerr)

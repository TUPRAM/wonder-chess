import bpy,json,hashlib,math,re
from pathlib import Path
from mathutils import Matrix,Vector
out=Path(__file__).parent;bw2=out.parents[3]/'BW2/r001';source=bw2/'ada_bw2_grip_checkpoint_r001_ART_REVISE.blend'
sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf'
s=bpy.context.scene;r=bpy.data.objects['BW1_Temporary_Pose_Rig'];g=bpy.data.objects['BW1_Glove_Pair_SourceFit'];body=bpy.data.objects['BW1_IndexedBody'];rec=json.loads(s['BW2_hand_contract']);relative=Matrix(rec['frame_relative_to_wrist'])
s.frame_set(1);openbasis={p.name:p.matrix_basis.copy() for p in r.pose.bones if p.name.endswith('.R') and re.match(r'finger[2-5]-',p.name)};originalaction=r.animation_data.action
for o in s.objects:
    if o.type=='MESH':o.hide_render=True
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.6,.6,.6);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=900;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='Standard'
record={'source_sha256':sha,'only_pose_override':'Source action sampled then detached in memory; all source pose bases assigned explicitly, except fingers2..5 fixed at source frame1 OPEN. Evaluated non-thumb bases asserted OPEN. Original fixture used for coordinates.','thumb_pad_trajectory':[],'renders':[]}
cam=bpy.data.objects['BW2_cam_oblique'];s.camera=cam
# Expand saved view only to include the entire OPEN hand; no source camera save.
cam.data.ortho_scale=.285
for frame in range(1,26):
    r.animation_data.action=originalaction;s.frame_set(frame);bpy.context.view_layer.update()
    pose={p.name:p.matrix_basis.copy() for p in r.pose.bones};pose.update(openbasis);r.animation_data.action=None
    for name,matrix in pose.items():r.pose.bones[name].matrix_basis=matrix
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rr=r.evaluated_get(dg)
    assert max(abs(rr.pose.bones[n].matrix_basis[i][j]-m[i][j]) for n,m in openbasis.items() for i in range(4) for j in range(4))<1e-6
    F=rr.matrix_world@rr.pose.bones['wrist.R'].matrix@relative;ev=g.evaluated_get(dg);me=ev.to_mesh();transform=F.inverted()@ev.matrix_world
    points=[transform@me.vertices[i].co for i in rec['patches']['1']['indices']];point6670=transform@me.vertices[6670].co;center=sum(points,Vector())/len(points)
    record['thumb_pad_trajectory'].append({'frame':frame,'pad_center_hand_m':list(center),'pad_minmax_Z_m':[min(p.z for p in points),max(p.z for p in points)],'vertex6670_hand_m':list(point6670),'thumb_local_Euler_degrees':{n:[math.degrees(x) for x in r.pose.bones[n].rotation_euler] for n in ['finger1-1.R','finger1-2.R','finger1-3.R']}});ev.to_mesh_clear()
    if frame in [1,14,15,25]:
        for ob,label in ([(g,'glove'),(body,'body')] if frame in [15,25] else [(g,'glove')]):
            g.hide_render=ob!=g;body.hide_render=ob!=body;s.render.filepath=str(out/f'isolated_verified_{label}_frame{frame:02}_oblique.png');bpy.ops.render.render(write_still=True);record['renders'].append(s.render.filepath)
record['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert record['source_sha256_after']==sha;(out/'thumb_isolation_trajectory_verified.json').write_text(json.dumps(record,indent=2))

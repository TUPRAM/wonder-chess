import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
out=Path(__file__).parent;source=out.parents[2]/'BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend'
expected='03829ab406d6bd5e6a1c5f86e045e9f2edc720b05e620e70017667c59be8b3f8'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene;scene.frame_set(1)
rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];glove=bpy.data.objects['BW1_Glove_Pair_SourceFit']
prior_action=rig.animation_data.action;rig.animation_data.action=None
names=[p.name for p in rig.pose.bones if p.name.startswith('finger') and p.name.endswith('.R')]
prior={n:rig.pose.bones[n].matrix_basis.copy() for n in names}
for n in names:rig.pose.bones[n].matrix_basis=Matrix.Identity(4)
def update():
    bpy.context.view_layer.update();return bpy.context.evaluated_depsgraph_get()
def readmesh(dg):
    ev=glove.evaluated_get(dg);me=ev.to_mesh();world=[ev.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return world,faces
dg=update();re=rig.evaluated_get(dg)
def head(n):return re.matrix_world@re.pose.bones[n].head
def tail(n):return re.matrix_world@re.pose.bones[n].tail
O=head('wrist.R');M=head('finger3-1.R');I=head('finger2-1.R');L=head('finger5-1.R');T=tail('finger3-3.R')
Y=(M-O).normalized();raw=I-L;X=(raw-raw.dot(Y)*Y).normalized();Z=X.cross(Y).normalized();C=(O+M)/2
# Positive joint-plane Z was independently identified as palmward by inspected body nails/creases.
F=Matrix(((X.x,Y.x,Z.x,O.x),(X.y,Y.y,Z.y,O.y),(X.z,Y.z,Z.z,O.z),(0,0,0,1)))
handworld=re.matrix_world@re.pose.bones['wrist.R'].matrix
baseline,faces=readmesh(dg);bvh=BVHTree.FromPolygons(baseline,faces)
palmloc,palmnormal,palmface,_=bvh.ray_cast(C+Z*.07,-Z,.14)
patches={};base_tips={}
for digit in range(1,6):
    n=f'finger{digit}-3.R';center=head(n).lerp(tail(n),.65)
    p,normal,faceid,dist=bvh.ray_cast(center+Z*.035,-Z,.07)
    assert p is not None,n
    # A small fixed localized patch around the actual ray-hit surface, chosen before probing.
    candidates=sorted(range(len(baseline)),key=lambda i:(baseline[i]-p).length)
    indices=[i for i in candidates if (baseline[i]-p).length<=.004]
    if len(indices)<3:indices=candidates[:3]
    indices=indices[:9]
    centroid=sum((baseline[i] for i in indices),Vector())/len(indices)
    patches[str(digit)]={'description':'Distal glove pad on observed palmward side, localized before tests; not a handle contact patch','distal_bone':n,'ray_hit_world':list(p),'normal_world':list(normal),'evaluated_face_index':faceid,'evaluated_vertex_indices':indices,'patch_extent_from_hit_m':max((baseline[i]-p).length for i in indices),'baseline_centroid_world':list(centroid),'sample_count':len(indices)}
    base_tips[digit]=tail(n).copy()
report={'source':str(source),'source_sha256':expected,'units':'metres (scene METRIC, scale_length1)','calibration_frame':1,'open_pose_basis':'Anatomical-right finger matrix_basis identity; no arm-chain reset; original action temporarily detached in unsaved process','palmar_sign_evidence':['body_positive_Z.png shows pads/creases','body_negative_Z.png shows actual fingernails; this is dorsal'],'semantic_frame_world':[list(r) for r in F],'frame_in_evaluated_wrist_bone':[list(r) for r in handworld.inverted()@F],'X_anatomical_sign':'toward index','frame_determinant':F.to_3x3().determinant(),'axis_lengths':[a.length for a in (X,Y,Z)],'axis_dot_products':[X.dot(Y),X.dot(Z),Y.dot(Z)],'middle_MCP_to_tip_dot_Y':(T-M).normalized().dot(Y),'world_local_roundtrip_error_m':max(((F@(F.inverted()@p))-p).length for p in (O,M,I,L,T,palmloc)),'palm_surface_landmark':{'object':glove.name,'world':list(palmloc),'normal_world':list(palmnormal),'evaluated_face_index':palmface,'signed_distance_from_joint_plane_m':(palmloc-C).dot(Z)},'rig_transform':{'matrix':[list(r) for r in re.matrix_world],'axis_lengths':[re.matrix_world.to_3x3().col[i].length for i in range(3)],'determinant':re.matrix_world.to_3x3().determinant()},'glove_transform':{'matrix':[list(r) for r in glove.matrix_world],'axis_lengths':[glove.matrix_world.to_3x3().col[i].length for i in range(3)],'determinant':glove.matrix_world.to_3x3().determinant()},'distal_pad_patches':patches,'tested_angle_degrees':5,'probe_assignments':'pb.matrix_basis = Matrix.Rotation(radians(sign*5),4,local_axis); restoration to the exact open basis after every probe','safe_range':'Only -5 to +5 degrees was tested per axis; no broad safe range, closure or contact acceptance is inferred','joints':{},'restoration_max_world_vertex_error_m':0}
for digit in range(1,6):
    ids=patches[str(digit)]['evaluated_vertex_indices'];padbase=Vector(patches[str(digit)]['baseline_centroid_world'])
    for segment in range(1,4):
        n=f'finger{digit}-{segment}.R';pb=rig.pose.bones[n];base=pb.matrix_basis.copy();dg=update();re=rig.evaluated_get(dg);basis=re.matrix_world@re.pose.bones[n].matrix
        joint={'local_control':n,'zero_matrix_basis':[list(r) for r in base],'world_local_rotation_axes_at_open':{axis:list(basis.to_3x3().col[i].normalized()) for i,axis in enumerate('XYZ')},'probes':[],'constraints':[(c.name,c.type,c.influence) for c in pb.constraints]}
        for axis in 'XYZ':
            for sign in [1,-1]:
                pb.matrix_basis=base@Matrix.Rotation(math.radians(sign*5),4,axis)
                dg=update();re=rig.evaluated_get(dg);posed,_=readmesh(dg);assert len(posed)==len(baseline)
                pad=sum((posed[i] for i in ids),Vector())/len(ids);tip=tail(f'finger{digit}-3.R');delta=pad-padbase;tipdelta=tip-base_tips[digit]
                thumb_to_fingers=(M-padbase).normalized()
                joint['probes'].append({'axis':axis,'degrees':sign*5,'pad_delta_world_m':list(delta),'pad_delta_hand_XYZ_mm':[1000*delta.dot(a) for a in (X,Y,Z)],'tip_delta_world_m':list(tipdelta),'tip_palmward_mm':1000*tipdelta.dot(Z),'pad_distance_to_middle_MCP_change_mm':1000*((pad-M).length-(padbase-M).length),'pad_toward_middle_MCP_mm':1000*delta.dot(thumb_to_fingers),'pad_centroid_world':list(pad)})
                pb.matrix_basis=base;dg=update();restored,_=readmesh(dg)
                err=max((a-b).length for a,b in zip(restored,baseline));report['restoration_max_world_vertex_error_m']=max(err,report['restoration_max_world_vertex_error_m'])
        ranked=sorted(joint['probes'],key=lambda p:p['pad_delta_hand_XYZ_mm'][2],reverse=True)
        joint['largest_palmward_probe']={k:ranked[0][k] for k in ('axis','degrees','pad_delta_hand_XYZ_mm','tip_palmward_mm')}
        if digit==1:joint['thumb_toward_finger_probe']=max(joint['probes'],key=lambda p:p['pad_toward_middle_MCP_mm'])
        report['joints'][n]=joint
        print(n,json.dumps(joint['largest_palmward_probe']),flush=True)
for n,m in prior.items():rig.pose.bones[n].matrix_basis=m
rig.animation_data.action=prior_action
report['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert report['source_sha256_after']==expected
report['status']='EXECUTED_REVERSIBLE_AXIS_CALIBRATION_ONLY_NOT_GRIP'
(out/'finger_axis_calibration.json').write_text(json.dumps(report,indent=2))
print('DONE',report['restoration_max_world_vertex_error_m'],flush=True)

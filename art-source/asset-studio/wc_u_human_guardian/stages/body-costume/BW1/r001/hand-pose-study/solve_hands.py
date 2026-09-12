import bpy, json, math, random
import numpy as np
from mathutils import Vector, Matrix, Euler
from pathlib import Path
out=Path(__file__).parent
scene=bpy.context.scene
rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
glove=bpy.data.objects['BW1_Glove_Pair_SourceFit']
for pb in rig.pose.bones: pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
world=rig.matrix_world.copy()
def transform_point(matrix,p):
    return matrix@Vector(p)
def basis(side):
    roots=[world@rig.data.bones[f'finger{i}-1.{side}'].head_local for i in range(2,6)]
    axis=(roots[0]-roots[-1]).normalized()
    forward=sum((world.to_3x3()@rig.data.bones[f'finger{i}-1.{side}'].y_axis for i in range(2,6)),Vector()).normalized()
    forward=(forward-axis*forward.dot(axis)).normalized()
    palmar=sum((world.to_3x3()@rig.data.bones[f'finger{i}-1.{side}'].z_axis for i in range(2,6)),Vector()).normalized()
    palmar=(palmar-axis*palmar.dot(axis)-forward*palmar.dot(forward)).normalized()
    center=sum(roots,Vector())/4+forward*.012+palmar*.022
    return center,axis,forward,palmar
handles={}
for side,diameter,length in [('R',.032,.13),('L',.030,.12)]:
    center,axis,forward,palmar=basis(side)
    handles[side]={'center_world':list(center),'axis_world':list(axis),'forward_world':list(forward),'palmar_world':list(palmar),'diameter_m':diameter,'length_m':length,'radius_m':diameter/2}

# Offline FK matching Blender's unscaled local bone chains. No source mesh edits.
def fk(side,finger,values):
    names=[f'finger{finger}-{i}.{side}' for i in (1,2,3)]
    parent=rig.data.bones[names[0]].parent
    pm=parent.matrix_local.copy()
    points=[]
    for j,name in enumerate(names):
        bone=rig.data.bones[name]
        rel=bone.parent.matrix_local.inverted()@bone.matrix_local
        rot=Euler(tuple(values[j*3:j*3+3]),'XYZ').to_matrix().to_4x4()
        matrix=pm@rel@rot
        if j==0: points.append(world@matrix.translation)
        points.append(world@(matrix@Vector((0,bone.length,0))))
        pm=matrix
    return points
def objective(side,finger,values):
    h=handles[side]; c=Vector(h['center_world']); axis=Vector(h['axis_world']); rad=h['radius_m']
    points=fk(side,finger,values)
    radius=rad+(.007 if finger==5 else .0085)
    score=0
    # Centerline stays outside the physical handle, with tips and distal joints near it.
    for j in range(3):
        for k in range(1,6):
            p=points[j].lerp(points[j+1],k/5)
            d=p-c; axial=d.dot(axis); radial=(d-axis*axial).length
            score+=max(0,radius-radial)**2*30
    for j,w in [(1,1),(2,6),(3,12)]:
        p=points[j]; d=p-c; axial=d.dot(axis); radial=(d-axis*axial).length
        score+=(radial-radius)**2*w
        score+=max(0,abs(axial)-h['length_m']/2+.006)**2*10
    if finger!=1:
        # Tips must finish beyond the far side of the cylinder, not merely hover near it.
        forward=Vector(h['forward_world']); palmar=Vector(h['palmar_world'])
        direction=points[3]-c; direction-=axis*direction.dot(axis)
        desired=(-forward*.60+palmar*.80).normalized()*radius
        score+=(direction-desired).length_squared*2
        score+=sum(values[j]**2 for j in (1,2,4,5,7,8))*.00001
    return score
def optimize(side,finger):
    if finger==1:
        vals=[.2,0,-.50,.6,0,0,.5,0,0]
        bounds=[(-.65,.65),(-.55,.55),(-1.45,.60),(0,1.55),(-.2,.2),(-.3,.3),(0,1.55),(-.15,.15),(-.2,.2)]
    else:
        vals=[.65,0,0,1.2,0,0,.85,0,0]
        bounds=[(-.15,1.7),(-.10,.10),(-.35,.35),(0,1.9),(0,0),(0,0),(0,1.75),(0,0),(0,0)]
    best=objective(side,finger,vals)
    for step in [.22,.10,.045,.02,.009]:
        for repeat in range(10):
            changed=False
            for n,(lo,hi) in enumerate(bounds):
                if lo==hi: continue
                for sign in (-1,1):
                    trial=list(vals);trial[n]=max(lo,min(hi,trial[n]+sign*step))
                    score=objective(side,finger,trial)
                    if score<best:
                        vals,best=trial,score;changed=True
            if not changed:break
    return vals,best
grips={}
for side in ('R','L'):
    grip={}
    for finger in range(1,6):
        vals,score=optimize(side,finger)
        for j in range(3):grip[f'finger{finger}-{j+1}.{side}']=vals[j*3:j*3+3]
        print(side,finger,score,[round(math.degrees(v),1) for v in vals])
    grips[side]=grip

def apply_pose(pose):
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    for name,angles in pose.items():
        pb=rig.pose.bones[name];pb.rotation_mode='XYZ';pb.rotation_euler=angles
    bpy.context.view_layer.update()

# Dedicated neutral review scene, explicit render allowlist.
for obj in scene.objects:
    obj.hide_render=obj!=glove
glove.hide_render=False
mat=bpy.data.materials.new('HAND_STUDY_Clay');mat.diffuse_color=(.46,.43,.38,1);mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.46,.43,.38,1);bsdf.inputs['Roughness'].default_value=.6
glove.data.materials.clear();glove.data.materials.append(mat)
handle_objs={}
for side in ('R','L'):
    h=handles[side];axis=Vector(h['axis_world'])
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=h['radius_m'],depth=h['length_m'],location=h['center_world'])
    obj=bpy.context.object;obj.name='STUDY_FIXED_HANDLE_'+side;obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(axis)
    h['matrix_world']=[list(row) for row in obj.matrix_world]
    handle_objs[side]=obj
    material=bpy.data.materials.new('HANDLE_'+side);material.diffuse_color=(.075,.095,.115,1);material.use_nodes=True
    material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.075,.095,.115,1)
    obj.data.materials.append(material)
camdata=bpy.data.cameras.new('HAND_STUDY_CAMERA');cam=bpy.data.objects.new('HAND_STUDY_CAMERA',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=.27
for name,power,size in [('HAND_KEY',150,.30),('HAND_FILL',60,.40)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('HAND_REVIEW_WORLD');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.11,.11,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
scene.view_settings.view_transform='Standard'
def render(name,side,pose,show_handle=True,view='palmar'):
    apply_pose(pose)
    for s,obj in handle_objs.items():obj.hide_render=not(show_handle and s==side)
    h=handles[side];c=Vector(h['center_world']);axis=Vector(h['axis_world']);forward=Vector(h['forward_world']);palmar=Vector(h['palmar_world'])
    target=c-forward*.02
    viewdir=(palmar*.95-forward*.4+axis*.28).normalized()
    if view=='dorsal':viewdir=(-palmar*.95-forward*.4+axis*.28).normalized()
    cam.location=target+viewdir*.6;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.data.objects['HAND_KEY'].location=target+viewdir*.30+axis*.20+forward*.16
    bpy.data.objects['HAND_FILL'].location=target+viewdir*.30-axis*.28
    for light in (bpy.data.objects['HAND_KEY'],bpy.data.objects['HAND_FILL']):light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
relaxed={}
for side in ('R','L'):
    for f in range(1,6):
        for j in (1,2,3):relaxed[f'finger{f}-{j}.{side}']=[([.12,.25,.15][j-1] if f>1 else [.05,.12,.08][j-1]),0,0]
pose_records={'open':{},'relaxed':relaxed,'sword_grip':grips['R'],'shield_grip':grips['L']}
json_out={'status':'CANDIDATE_INITIAL_CONSTRUCTION_UNREVIEWED','input_file':'../bw1_hand_pose_input.blend','rotation_mode':'XYZ','angle_units':'radians','handles':handles,'poses':pose_records,'method':'Local bone-angle coordinate search around two fixed cylindrical handles; no mesh topology or coordinate edits','limits':'Bone-centerline objective only; not yet a mesh-contact or artistic pass'}
(out/'poses_initial.json').write_text(json.dumps(json_out,indent=2))
render('open_R','R',{},False)
render('relaxed_R','R',relaxed,False)
render('sword_grip_initial','R',grips['R'])
render('shield_grip_initial','L',grips['L'])
render('sword_grip_initial_dorsal','R',grips['R'],True,'dorsal')
apply_pose({**grips['R'],**grips['L']})
bpy.ops.wm.save_as_mainfile(filepath=str(out/'hand_pose_study_initial.blend'))

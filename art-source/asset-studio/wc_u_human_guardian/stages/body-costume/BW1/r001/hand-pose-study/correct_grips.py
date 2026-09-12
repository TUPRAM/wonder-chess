import bpy,json,math,itertools
from pathlib import Path
from mathutils import Vector,Matrix,Euler
out=Path(__file__).parent
rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];world=rig.matrix_world.copy()
record=json.loads((out/'poses_initial.json').read_text());handles=record['handles']
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
def fk(side,finger,angles):
    pm=rig.data.bones[f'finger{finger}-1.{side}'].parent.matrix_local.copy();points=[]
    for j in range(3):
        b=rig.data.bones[f'finger{finger}-{j+1}.{side}'];rel=b.parent.matrix_local.inverted()@b.matrix_local
        matrix=pm@rel@Euler(tuple(angles[j*3:j*3+3]),'XYZ').to_matrix().to_4x4()
        if not points:points.append(world@matrix.translation)
        points.append(world@(matrix@Vector((0,b.length,0))));pm=matrix
    return points
def objective(side,finger,vals):
    h=handles[side];c=Vector(h['center_world']);axis=Vector(h['axis_world']);forward=Vector(h['forward_world']);palmar=Vector(h['palmar_world'])
    radius=h['radius_m']+(.0065 if finger==5 else .008)
    pts=fk(side,finger,vals);score=0
    for j in range(3):
        for k in range(1,6):
            p=pts[j].lerp(pts[j+1],k/5);d=p-c;rad=(d-axis*d.dot(axis)).length
            score+=max(0,radius-rad)**2*100
    for j,w in [(1,.5),(2,2),(3,5)]:
        d=pts[j]-c;rad=(d-axis*d.dot(axis)).length;score+=(rad-radius)**2*w
    # Encourage complete wrap with contact on the opposite half from the palm.
    d=pts[-1]-c;d-=axis*d.dot(axis)
    desired=(palmar*.80-forward*.60).normalized()*radius
    score+=(d-desired).length_squared*1.5
    # Reject reversals and exaggerated spread/twist.
    score+=sum(vals[k]**2 for k in (1,2,4,5,7,8))*.00007
    return score
def optimize(side,finger):
    seeds=[]
    if finger>1:
        bounds=[(-.2,1.55),(-.10,.10),(-.30,.30),(0,1.92),(0,0),(0,0),(0,1.75),(0,0),(0,0)]
        for a,b,c in itertools.product(range(-10,91,20),range(10,111,20),range(10,101,30)):
            vals=[math.radians(a),0,0,math.radians(b),0,0,math.radians(c),0,0];seeds.append((objective(side,finger,vals),vals))
    else:
        bounds=[(-.65,.80),(-.70,.70),(-1.5,1.0),(0,1.7),(-.15,.15),(-.3,.3),(0,1.7),(-.15,.15),(-.2,.2)]
        for a,b,c in itertools.product([-.5,0,.5],[-.5,0,.5],[-1.2,-.6,0,.6]):
            vals=[a,b,c,.5,0,0,.5,0,0];seeds.append((objective(side,finger,vals),vals))
    overall=(float('inf'),None)
    for initial,vals in sorted(seeds,key=lambda x:x[0])[:5]:
        best=initial
        for step in [.15,.06,.025,.010]:
            for repeat in range(12):
                changed=False
                for n,(lo,hi) in enumerate(bounds):
                    if lo==hi:continue
                    for sign in (-1,1):
                        trial=list(vals);trial[n]=max(lo,min(hi,trial[n]+sign*step));score=objective(side,finger,trial)
                        if score<best:vals,best=trial,score;changed=True
                if not changed:break
        if best<overall[0]:overall=(best,vals)
    return overall
for side,key in [('R','sword_grip'),('L','shield_grip')]:
    pose={}
    for f in range(1,6):
        score,vals=optimize(side,f)
        print(side,f,round(score,6),[round(math.degrees(v),1) for v in vals])
        for j in range(3):pose[f'finger{f}-{j+1}.{side}']=vals[j*3:j*3+3]
    record['poses'][key]=pose
record['status']='CORRECTION_1_PENDING_IMAGE_REVIEW';record['correction']='Multiple bounded initial chains and stronger cylinder clearance; fixed handle unchanged.'
(out/'poses_correction1.json').write_text(json.dumps(record,indent=2))
for name,vals in {**record['poses']['sword_grip'],**record['poses']['shield_grip']}.items():rig.pose.bones[name].rotation_euler=vals
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'hand_pose_correction1.blend'))

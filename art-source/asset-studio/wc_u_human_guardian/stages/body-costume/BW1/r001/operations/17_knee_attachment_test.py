import bpy,math,bmesh,json
from mathutils import Vector,Matrix
s=bpy.data.scenes['BW1_BODY_COSTUME'];s.frame_set(1);rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
def plate(name,vs,fs,bone,thickness):
    me=bpy.data.meshes.new(name+'_Cage');me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.data.collections['BW1_ARMOR'].objects.link(ob);me.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
    m=ob.modifiers.new('Plate thickness','SOLIDIFY');m.thickness=thickness;m.offset=-1
    m=ob.modifiers.new('Controlled edge','BEVEL');m.width=.0015;m.segments=2
    ob.parent=rig;ob.parent_type='BONE';ob.parent_bone=bone;ob.matrix_world=Matrix.Identity(4)
    ob['status']='LOCAL_KNEE_ATTACHMENT_CANDIDATE';return ob
old=bpy.data.objects['BW1_KneePlate_R'];old.hide_render=True;old.hide_set(True);old['status']='REJECTED_SHIN_PARENT_KNEE_FLIP'
# Cup has independent concavity/thickness and follows the thigh-side attachment, not the shin rotation.
center=Vector((.153428,.087,.514));n=16;vs=[];fs=[]
for radius,depth in [(1,-.030),(.58,-.007),(.20,0)]:
    for i in range(n):
        a=i*2*math.pi/n;x=.066*math.cos(a)*radius;z=.061*math.sin(a)*radius
        vs.append(center+Vector((x,depth,z)))
for row in range(2):
    for i in range(n):fs.append((row*n+i,row*n+(i+1)%n,(row+1)*n+(i+1)%n,(row+1)*n+i))
fs.append(tuple(range(2*n,3*n)))
ob=plate('BW1_KneeCup_R_ThighAttachment',vs,fs,'upperleg02.R',.004)
ob['attachment_policy']='Rigid thigh-side cup with strap; shin clearance must pass at bend. No source/shared bone changes.'
# Upper strap provides an explicit attachment across the posterior thigh instead of a floating badge.
vs=[];fs=[];n=32
for row in [-1,1]:
    for i in range(n):
        a=i*2*math.pi/n;vs.append((.151+.064*math.cos(a),-.018+.074*math.sin(a),.551+row*.012))
for i in range(n):fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
plate('BW1_KneeCup_ThighStrap_R',vs,fs,'upperleg02.R',.003)
# Two independent calf closures for the existing rigid shin shell; no knee-crossing shell.
for j,z in enumerate([.26,.40]):
    t=(z-.20)/.24;cx=.188-(.035*t);rx=.052+.018*t;ry=.060+.021*t;cy=-.030
    vs=[];fs=[]
    for row in [-1,1]:
        for i in range(32):
            a=i*2*math.pi/32;vs.append((cx+rx*math.cos(a),cy+ry*math.sin(a),z+row*.010))
    for i in range(32):fs.append((i,(i+1)%32,(i+1)%32+32,i+32))
    plate('BW1_Greave_Closure_R_'+str(j+1),vs,fs,'lowerleg01.R',.003)
s.camera=bpy.data.objects['BW1_Camera_leg_proof'];s.render.resolution_x=900;s.render.resolution_y=900
for frame,name in [(1,'stance'),(121,'bend')]:
    s.frame_set(frame)
    s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/knee_attachment_'+name+'.png';bpy.ops.render.render(write_still=True)
s.frame_set(145);s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.resolution_x=850;s.render.resolution_y=1100;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/knee_attachment_kneel.png';bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Right cup method replaced, thigh attachment and calf closures rendered; left remains blockout')

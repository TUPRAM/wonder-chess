import bpy,math,bmesh,json
from mathutils import Vector,Matrix
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig'];col=bpy.data.collections['BW1_EQUIPMENT']
frames=json.loads("{\"R\":{\"mcp_center_world\":[0.5323286056518555,0.18016177415847778,1.051831841468811],\"axis_world\":[-0.38251402974128723,0.8434769511222839,0.37713339924812317],\"forward_world\":[0.14629368484020233,0.4583166837692261,-0.8766664266586304],\"palmar_world\":[-0.9122945070266724,-0.2801649868488312,-0.29870790243148804],\"center_world_proposed\":[0.5140136480331421,0.17949794232845306,1.0347403287887573],\"center_offsets_m\":{\"finger_forward\":0.012,\"palmar\":0.022},\"diameter_m\":0.032,\"length_m\":0.13,\"matrix_world_proposed\":[[0.14629368484020233,-0.9122945070266724,-0.38251402974128723,0.5140136480331421],[0.4583166837692261,-0.2801649868488312,0.8434769511222839,0.17949794232845306],[-0.8766664266586304,-0.29870790243148804,0.37713339924812317,1.0347403287887573],[0,0,0,1]],\"matrix_relative_to_wrist_rest_proposed\":[[-0.307578980922699,-0.8151082992553711,-0.07315687835216522,-0.015825511887669563],[0.7616219520568848,-0.31369835138320923,0.2930580675601959,0.0897626131772995],[-0.29947444796562195,0.03937061131000519,0.820440411567688,-0.01777563989162445],[0,0,0,1]],\"axis_validation\":{\"forward_dot_mean_mcp_to_tip\":0.9981108233332634,\"palmar_dot_positive_local_x_curl\":0.9785312563180923}},\"L\":{\"mcp_center_world\":[-0.532328724861145,0.18016162514686584,1.051831841468811],\"axis_world\":[0.38251402974128723,0.8434769511222839,0.37713339924812317],\"forward_world\":[-0.14629368484020233,0.4583166837692261,-0.8766663074493408],\"palmar_world\":[0.9122945070266724,-0.2801649570465088,-0.2987079322338104],\"center_world_proposed\":[-0.5140137672424316,0.17949779331684113,1.0347403287887573],\"center_offsets_m\":{\"finger_forward\":0.012,\"palmar\":0.022},\"diameter_m\":0.03,\"length_m\":0.12,\"matrix_world_proposed\":[[-0.14629368484020233,-0.9122945070266724,0.38251402974128723,-0.5140137672424316],[0.4583166837692261,0.2801649570465088,0.8434769511222839,0.17949779331684113],[-0.8766663074493408,0.2987079322338104,0.37713339924812317,1.0347403287887573],[0,0,0,1]],\"matrix_relative_to_wrist_rest_proposed\":[[0.30757904052734375,-0.8151082396507263,0.07315708696842194,0.01582546904683113],[0.7616218328475952,0.31369850039482117,0.29305797815322876,0.08976266533136368],[-0.29947429895401,-0.03937043249607086,0.8204404711723328,-0.01777563989162445],[0,0,0,1]],\"axis_validation\":{\"forward_dot_mean_mcp_to_tip\":0.9981107339262962,\"palmar_dot_positive_local_x_curl\":0.9785312488675117}}}")
def part(name,vs,fs,bone,thickness=0,bevel=.001):
    me=bpy.data.meshes.new(name+'_Cage');me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
    if thickness:
        m=ob.modifiers.new('Manufactured shell thickness','SOLIDIFY');m.thickness=thickness;m.offset=-1
    if bevel:
        m=ob.modifiers.new('Edge treatment','BEVEL');m.width=bevel;m.segments=2
    ob.parent=rig;ob.parent_type='BONE';ob.parent_bone=bone;ob.matrix_world=Matrix.Identity(4)
    ob['status']='BLOCKOUT_CONTACT_UNPROVEN';ob['construction']='Original editable geometry around dimensioned handle; contact not approved'
    return ob
def cylinder(name,c,a,r,length,bone):
    a=a.normalized();u=a.orthogonal().normalized();v=a.cross(u).normalized();vs=[];fs=[];n=16
    for row in range(2):
        for i in range(n):vs.append(c+a*((row-.5)*length)+r*(u*math.cos(i*2*math.pi/n)+v*math.sin(i*2*math.pi/n)))
    for i in range(n):fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
    fs.extend([tuple(reversed(range(n))),tuple(range(n,2*n))])
    ob=part(name,vs,fs,bone);ob['handle_diameter_m']=2*r;ob['handle_length_m']=length
    return ob
h=frames['R'];C=Vector(h['center_world_proposed']);A=Vector(h['axis_world']);F=Vector(h['forward_world']);N=A.cross(F).normalized()
cylinder('BW1_Sword_Handle_R',C,A,.016,.13,'wrist.R')
# Broad, flattened guard with two subtly downturned quillons.
g=C+A*.078;vs=[];fs=[]
for t in [-1,-.45,0,.45,1]:
    center=g+F*(t*.105)-A*(.012*abs(t)**2)
    for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:vs.append(center+A*(u*.009)+N*(v*.008))
for j in range(4):
    for i in range(4):fs.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
fs.extend([(3,2,1,0),(16,17,18,19)])
part('BW1_Sword_Crossguard_R',vs,fs,'wrist.R',bevel=.002)
# Diamond cross-section blade, tapered in width and thickness with a small terminal edge.
vs=[];fs=[]
for t,width,thick in [(0,.029,.004),(.05,.029,.004),(.51,.020,.003),(.63,.0008,.0008)]:
    base=g+A*(.014+t)
    vs.extend([base+F*width,base+N*thick,base-F*width,base-N*thick])
for j in range(3):
    for i in range(4):fs.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
fs.extend([(3,2,1,0),(12,13,14,15)])
part('BW1_Sword_Blade_R',vs,fs,'wrist.R',bevel=.0004)
cylinder('BW1_Sword_Pommel_R',C-A*.089,A,.023,.030,'wrist.R')
# Shield: true convex kite surface with separate rim and rear handle.
h=frames['L'];C=Vector(h['center_world_proposed']);A=Vector(h['axis_world']);normal=-Vector(h['palmar_world'])
up=(Vector((0,0,1))-normal*normal.z).normalized();right=up.cross(normal).normalized()
center=C+normal*.090+up*.075
outline=[(-.16,.32),(.16,.32),(.245,.225),(.218,.015),(.145,-.20),(0,-.37),(-.145,-.20),(-.218,.015),(-.245,.225)]
vs=[center+normal*.043];fs=[]
for scale,depth in [(.50,.032),(1,0)]:
    for x,z in outline:vs.append(center+right*x*scale+up*z*scale+normal*depth)
n=len(outline)
for i in range(n):fs.append((0,1+i,1+(i+1)%n));fs.append((1+i,1+n+i,1+n+(i+1)%n,1+(i+1)%n))
shield=part('BW1_Shield_ConvexKite_L',vs,fs,'lowerarm02.L',thickness=.014,bevel=.003)
shield['design']='Convex kite blockout; emblem and trim await forms gate'
# Distinct perimeter band.
vs=[];fs=[]
for scale,dep in [(.95,.004),(1.01,.003)]:
    for x,z in outline:vs.append(center+right*x*scale+up*z*scale+normal*dep)
for i in range(n):fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
part('BW1_Shield_Rim_L',vs,fs,'lowerarm02.L',thickness=.005)
cylinder('BW1_Shield_Handle_L',C,A,.015,.12,'lowerarm02.L')
# Visible handle standoffs, mechanically connecting the handle axis to the rear shell.
for sign in [-1,1]:
    endpoint=C+A*(sign*.050);delta=center-endpoint;depth=delta.dot(normal)-.015
    cylinder('BW1_Shield_HandleMount_'+str(sign),endpoint+normal*depth*.5,normal,.011,depth,'lowerarm02.L')
# Two separate rear forearm strap arches. Fit is a blockout assumption, exposed for inspection.
for j,offset in enumerate([.10,.20]):
    strapcenter=C+up*offset+normal*.020;vs=[];fs=[]
    for row in [-1,1]:
        for i in range(13):
            a=math.pi*i/12
            vs.append(strapcenter+right*(.059*math.cos(a))+normal*(-.050*math.sin(a))+up*(row*.014))
    for i in range(12):fs.append((i,i+1,i+14,i+13))
    part('BW1_Shield_ForearmStrap_'+str(j+1),vs,fs,'lowerarm02.L',thickness=.004)
s['equipment_frame_status']='Corrected MCP-to-tip frame used for blockout only; failed grip poses remain separate ART_REVISE'
# Saved arm proof camera; same camera throughout the local range test.
data=bpy.data.cameras.new('BW1_Camera_arm_proof');cam=bpy.data.objects.new('BW1_Camera_arm_proof',data);bpy.data.collections['BW1_PRESENTATION'].objects.link(cam)
cam.location=(1.6,2.7,1.75);target=Vector((.34,.10,1.28));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=.92
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.resolution_x=850;s.render.resolution_y=1100;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/equipment_blockout.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'equipment_parts':[o.name for o in col.objects],'contact_status':'UNPROVEN_NO_GRIP_APPROVAL'}))

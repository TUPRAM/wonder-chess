import bpy, math, bmesh, json
from mathutils import Vector,Matrix
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
boot=bpy.data.objects['BW1_Boot_Pair_SourceFit'];ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get())
points=sorted(set([(round(p.x,4),round(p.y,4)) for v in ev.data.vertices for p in [boot.matrix_world@v.co] if p.x>0 and p.z<.018]))
def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
lower=[]
for p in points:
    while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
    lower.append(p)
upper=[]
for p in reversed(points):
    while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
    upper.append(p)
hull=lower[:-1]+upper[:-1]
# Keep a compact editable contour, retaining actual hull extrema.
outline=[]
for p in hull:
    if not outline or (Vector(p)-Vector(outline[-1])).length>.009:outline.append(p)
cx=sum(p[0] for p in outline)/len(outline);cy=sum(p[1] for p in outline)/len(outline)
verts=[]
for row in range(3):
    for x,y in outline:
        rad=Vector((x-cx,y-cy)).normalized()
        rim=[.0015,.002,.0005][row]
        z= [-.024,-.017,.002][row]
        if y>.075 and row<2:z+=.004*(y-.075)/.115
        verts.append((x+rad.x*rim,y+rad.y*rim,z))
n=len(outline);faces=[]
for j in range(2):
    for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
faces.extend([tuple(reversed(range(n))),tuple(range(2*n,3*n))])
me=bpy.data.meshes.new('BW1_FootprintSole_R_Cage');me.from_pydata(verts,[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
ob=bpy.data.objects.new('BW1_FootprintSole_R',me);bpy.data.collections['BW1_CLOTH'].objects.link(ob);me.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
m=ob.modifiers.new('Restrained perimeter edge','BEVEL');m.width=.0015;m.segments=2
ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='foot.R';ob.matrix_world=Matrix.Identity(4)
ob['construction']='New closed three-ring sole loft from evaluated boot footprint; no master body removal';ob['source_outline_points']=n
old=bpy.data.objects['BW1_BootSole_R'];old.hide_render=True;old.hide_set(True);old['status']='REJECTED_BROAD_SOLE'
s.camera=bpy.data.objects['BW1_Camera_leg_proof'];s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/footprint_sole_stance.png';bpy.ops.render.render(write_still=True)
rig.pose.bones['foot.R'].rotation_euler.x=math.radians(-20);bpy.context.view_layer.update()
s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/footprint_sole_ankle.png';bpy.ops.render.render(write_still=True)
rig.pose.bones['foot.R'].rotation_euler.x=0;bpy.context.view_layer.update()
s.camera=bpy.data.objects['BW1_Camera_profile'];s.render.resolution_x=850;s.render.resolution_y=1100;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/footprint_sole_profile.png';bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'sole_contour_points':n,'vertices':len(verts),'faces':len(faces),'left_side':'retained previous blockout; new method not propagated'}))

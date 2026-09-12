import bpy,math,json
from mathutils import Matrix,Vector
s=bpy.data.scenes['BW1_BODY_COSTUME'];rig=bpy.data.objects['BW1_Temporary_Pose_Rig']
# Correct the plate clearance observed in armor_blockout_r000; never hide the underlying coat.
for name in ['BW1_Breastplate','BW1_Backplate']:
    ob=bpy.data.objects[name];front=name=='BW1_Breastplate'
    for v in ob.data.vertices:
        j=v.index//13;i=v.index%13;u=-1+2*i/12
        if front:
            centers=[.124,.138,.186,.193,.165,.143];v.co.y=centers[j]-.044*abs(u)**1.8
        else:
            centers=[-.191,-.199,-.225,-.235,-.210,-.185];v.co.y=centers[j]+.034*abs(u)**1.8
    ob.data.update()
for ob in bpy.data.collections['BW1_ARMOR'].objects:
    for p in ob.data.polygons:p.use_smooth=True
# Make the adapted boot toe broader, retaining topology, UVs and correspondence-derived weights.
boot=bpy.data.objects['BW1_Boot_Pair_SourceFit'];inv=boot.matrix_world.inverted()
for v in boot.data.vertices:
    p=boot.matrix_world@v.co;side=1 if p.x>0 else -1
    if p.y>.035 and p.z<.11:
        t=min(1,(p.y-.035)/.12);cx=side*(.195+.08*p.y)
        p.x=cx+(p.x-cx)*(1+.13*t)
        p.z+=.009*t*max(0,min(1,(p.z+.012)/.055))
        v.co=inv@p
boot.data.update();boot['adaptation']='Broader toe box; original topology/weights retained. Added separately editable flat outsole.'
def solid_part(name,verts,faces,bone,collection='BW1_ARMOR',bevel=.002):
    me=bpy.data.meshes.new(name+'_Cage');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.data.collections[collection].objects.link(ob);me.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
    if bevel:m=ob.modifiers.new('Manufactured edge radius','BEVEL');m.width=bevel;m.segments=2
    ob.parent=rig;ob.parent_type='BONE';ob.parent_bone=bone;ob.matrix_world=Matrix.Identity(4);ob['wc_part_id']=name;ob['approval']='CANDIDATE';return ob
outline=[(-.103,-.032),(-.085,-.045),(-.035,-.045),(.045,-.052),(.125,-.064),(.168,-.055),(.194,-.024),(.194,.021),(.172,.059),(.130,.071),(.055,.068),(-.032,.048),(-.080,.042)]
for side in [1,-1]:
    suffix='R' if side==1 else 'L_Blockout';bn='foot.'+('R' if side==1 else 'L');verts=[]
    for z in [-.027,-.006]:
        for y,dx in outline:verts.append((side*(.195+.08*y+dx),y,z))
    n=len(outline);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=solid_part('BW1_BootSole_'+suffix,verts,faces,bn,collection='BW1_CLOTH',bevel=.003)
    ob['sole_thickness_m']=.021;ob['construction']='Original broad flat outsole with distinct heel and toe boundary';ob['behavior']='Foot-following rigid proof sole; forefoot flex remains a separate check'
# Right boot vamp strap is a distinct construction layer with an open underside.
verts=[];faces=[]
for j,y in enumerate([.040,.043,.065,.068]):
    for i in range(13):
        a=math.radians(-88+176*i/12);verts.append((.200+.071*math.sin(a),y,.025+.065*math.cos(a)))
        if j<3 and i<12:k=j*13+i;faces.append((k,k+1,k+14,k+13))
ob=solid_part('BW1_BootVampStrap_R',verts,faces,'foot.R',collection='BW1_CLOTH');m=ob.modifiers.new('Strap thickness','SOLIDIFY');m.thickness=.004;m.offset=0
# Readable buckles have actual hollow centers, not stamped solid squares.
def buckle(name,center,width,height,depth,bone):
    x,y,z=center;v=[]
    for yy in [y-depth/2,y+depth/2]:
        for w,h in [(width,height),(width-.009,height-.009)]:
            v.extend([(x-w/2,yy,z-h/2),(x+w/2,yy,z-h/2),(x+w/2,yy,z+h/2),(x-w/2,yy,z+h/2)])
    f=[]
    for i in range(4):
        k=(i+1)%4;f.extend([(i,k,k+4,i+4),(i+8,i+12,k+12,k+8),(i,k,k+8,i+8),(i+4,i+12,k+12,k+4)])
    return solid_part(name,v,f,bone)
buckle('BW1_BeltBuckle',(0,.137,1.094),.057,.060,.007,'root')
# Contrast-free clay rim surfaces clarify the three overlapping right shoulder pieces.
for name in ['BW1_Pauldron_R_Cap','BW1_Pauldron_R_Lame1','BW1_Pauldron_R_Lame2','BW1_Bracer_R','BW1_Greave_R']:
    ob=bpy.data.objects[name];ob['proof_side']='anatomical_right'
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/body_costume_r001_clay.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Adjusted breast/back clearance against coat; retained broad boot toe adaptation and authored separate flat soles/vamp strap.')


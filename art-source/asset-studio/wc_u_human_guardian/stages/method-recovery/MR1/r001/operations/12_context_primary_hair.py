import bpy,bmesh,json
from mathutils import Vector
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
sc=bpy.data.scenes['MR1_CONTEXT_HEAD_CANDIDATE'];bpy.context.window.scene=sc;col=bpy.data.collections['MR1_CONTEXT_CANDIDATE_ALLOWLIST']
def authored_mass(name,centers,widths,depths,crest_shifts):
    verts=[];faces=[];fractions=[-1,-.55,0,.55,1];frames=[]
    for i,point in enumerate(centers):
        c=Vector(point);n=Vector((c.x,(c.y+.021),c.z-1.705)).normalized()
        tangent=Vector(centers[min(i+1,len(centers)-1)])-Vector(centers[max(i-1,0)])
        tangent=(tangent-n*tangent.dot(n)).normalized();across=n.cross(tangent).normalized();frames.append([list(tangent),list(across),list(n)])
        # Asymmetric flattened wedge, independently varying width, depth and crest.
        profiles=[[-.0005,depths[i]*(.68+crest_shifts[i]),depths[i],depths[i]*(.68-crest_shifts[i]),-.0005],[-.003,-.0015,-.001,-.0015,-.003]]
        for profile in profiles:
            for j,f in enumerate(fractions):verts.append(tuple(c+across*(widths[i]*f)+n*profile[j]))
    for i in range(len(centers)-1):
        for j in range(4):
            faces.append((i*10+j,i*10+j+1,(i+1)*10+j+1,(i+1)*10+j))
            faces.append((i*10+5+j,(i+1)*10+5+j,(i+1)*10+6+j,i*10+6+j))
        faces.extend([(i*10,(i+1)*10,(i+1)*10+5,i*10+5),(i*10+4,i*10+9,(i+1)*10+9,(i+1)*10+4)])
    for i in [0,len(centers)-1]:
        for j in range(4):faces.append((i*10+j,i*10+5+j,i*10+6+j,i*10+j+1))
    me=bpy.data.meshes.new(name+'_ControlMesh');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(bpy.data.materials['MR1_Uniform_Clay'])
    for f in me.polygons:f.use_smooth=True
    sub=o.modifiers.new('One level broad mass preview','SUBSURF');sub.levels=1;sub.render_levels=1
    o['mr1_authored_stations']=json.dumps({'centers':centers,'half_widths':widths,'depths':depths,'crest_shifts':crest_shifts,'frames':frames})
    o['scope']='Primary mass in contextual candidate; independently authored path and section, unapproved hairstyle'
    return o
counter=authored_mass('MR1_CONTEXT_Hair_Counter_Sweep',[(-.022,.003,1.803),(-.048,.015,1.790),(-.066,.027,1.770),(-.085,.016,1.742),(-.098,-.010,1.715),(-.09,-.058,1.694),(-.070,-.079,1.688)],[.007,.016,.021,.023,.018,.012,.002],[.001,.009,.014,.015,.012,.008,.001],[0,-.10,-.20,-.18,.1,.20,0])
crown=authored_mass('MR1_CONTEXT_Hair_Crown_Rear',[(-.024,-.003,1.803),(.0,-.027,1.808),(.032,-.059,1.792),(.039,-.093,1.764),(.022,-.120,1.732),(.0,-.117,1.700),(-.015,-.102,1.686)],[.006,.024,.037,.041,.035,.020,.004],[.001,.014,.020,.022,.019,.012,.002],[0,.18,.20,.08,-.18,-.22,0])
gather=authored_mass('MR1_CONTEXT_Hair_Rear_Gathering',[(.059,-.085,1.739),(.060,-.107,1.730),(.040,-.129,1.712),(.018,-.142,1.690),(.0,-.143,1.674),(.003,-.137,1.655)],[.006,.018,.028,.035,.028,.012],[.001,.010,.017,.022,.016,.003],[0,-.1,-.2,-.15,.12,0])
sc['mr1_primary_hair_masses']=4
sc['mr1_render_allowlist']=json.dumps([o.name for o in sc.objects if not o.hide_render])
sc.camera=bpy.data.objects['MR1_CONTEXT_three_quarter']
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.wm.save_as_mainfile(filepath=root+'/contextual_head_candidate_r001.blend',copy=True)
for v in ['front','three_quarter','profile','opposite','rear','top']:
    sc.camera=bpy.data.objects['MR1_CONTEXT_'+v];sc.render.filepath=root+'/captures/context_primary_r001_clay_'+v+'.png';bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['MR1_CONTEXT_three_quarter']
print(json.dumps({'primary_hair_masses':4,'new_objects':[counter.name,crown.name,gather.name],'braid_geometry_changed':False,'full_head_status':'UNAPPROVED_CONTEXT_CANDIDATE'}))

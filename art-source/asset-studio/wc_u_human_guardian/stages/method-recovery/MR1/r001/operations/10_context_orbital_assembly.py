import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
assert bpy.data.scenes.get('MR1_CONTEXT_HEAD_CANDIDATE') is None
bpy.context.window.scene=bpy.data.scenes['Scene'];dep=bpy.context.evaluated_depsgraph_get();source_head=bpy.data.objects['ADA_Head_Continuous'];tree=BVHTree.FromObject(source_head,dep)
sc=bpy.data.scenes.new('MR1_CONTEXT_HEAD_CANDIDATE');bpy.context.window.scene=sc
col=bpy.data.collections.new('MR1_CONTEXT_CANDIDATE_ALLOWLIST');sc.collection.children.link(col)
def copy_obj(src,name):
    o=src.copy();o.data=src.data.copy();o.name=name;col.objects.link(o);o.hide_render=False;o.hide_viewport=False;o.hide_set(False);o.show_wire=False;o.show_all_edges=False;return o
head=copy_obj(source_head,'MR1_CONTEXT_Retained_Head_Outside_Orbital_Regions')
# Retain AS1 torso, collar, neck, shoulder and ear context as independent copies.
keep=['ADA_Neck','ADA_Ear_Pinna_L','ADA_Ear_Helix_L','ADA_Ear_Pinna_R','ADA_Ear_Helix_R','ADA_Fitted_Brow_L','ADA_Fitted_Brow_R','ADA_Torso_Undercoat','ADA_Padded_Collar','ADA_Study_Sleeve_R','ADA_Collar_Fitted_Roll','ADA_Breastplate','ADA_Backplate','ADA_Upper_Attachment_L','ADA_Upper_Attachment_R','ADA_Cupped_Shoulder_R_1','ADA_Cupped_Shoulder_R_2','ADA_Cupped_Shoulder_R_3','ADA_Braid_Strand_0','ADA_Braid_Strand_1','ADA_Braid_Strand_2','ADA_Braid_Tail']
for n in keep:copy_obj(bpy.data.objects[n],'MR1_CONTEXT_'+n)
proof=bpy.data.objects['MR1_Right_Orbital_Cage']
orb=copy_obj(proof,'MR1_CONTEXT_Orbital_Cage_R');orb['scope']='Context derivative: boundary fitting only; isolated proof remains frozen'
# Fit only the outer interface row to the retained cranial envelope. No eyelid,
# globe, entire face, cheek surface or old relief is projected.
fit=[]
for j in range(20):
    v=orb.data.vertices[80+j];before=v.co.copy();near,normal,idx,dist=tree.find_nearest(before)
    v.co=near;fit.append({'vertex':80+j,'before':list(before),'after':list(v.co)})
    orb.data.vertices[60+j].co+=(near-before)*.25
orb.data.update();orb['mr1_boundary_fit']=json.dumps(fit)
left=copy_obj(orb,'MR1_CONTEXT_Orbital_Cage_L')
for v in left.data.vertices:v.co.x=-v.co.x
bm=bmesh.new();bm.from_mesh(left.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(left.data);bm.free()
for side,sign in [('R',1),('L',-1)]:
    g=copy_obj(bpy.data.objects['MR1_Right_Eye_Globe'],'MR1_CONTEXT_Globe_'+side);g.location.x*=sign
# Remove old front skin from the new orbital regions using the curved planned
# perimeter. This diagnostic assembly reserves a narrow peripheral join strip.
poly=[(v.co.x,v.co.z) for v in orb.data.vertices[80:100]]
def inside(x,z,points):
    hit=False;j=len(points)-1
    for i in range(len(points)):
        a,b=points[i];c,d=points[j]
        if ((b>z)!=(d>z)) and x<(c-a)*(z-b)/(d-b)+a:hit=not hit
        j=i
    return hit
bm=bmesh.new();bm.from_mesh(head.data)
mask=[(.035+(x-.035)*.90,1.689+(z-1.689)*.90) for x,z in poly]
remove=[]
for f in bm.faces:
    p=f.calc_center_median()
    if p.y>-.014 and inside(abs(p.x),p.z,mask):remove.append(f)
removed=len(remove);bmesh.ops.delete(bm,geom=remove,context='FACES')
bm.to_mesh(head.data);bm.free();head['mr1_removed_front_faces']=removed
head['scope']='Retained context outside curved eye/cheek apertures; peripheral joins are diagnostic and unapproved'
# Candidate foundation inherits the corrected temple; close only the small
# pre-existing crown boundary in this context copy.
cap=copy_obj(bpy.data.objects['MR1_HAIR_CONTEXT_ADA_Hair_Foundation'],'MR1_CONTEXT_Hair_Foundation')
bm=bmesh.new();bm.from_mesh(cap.data);top_edges=[e for e in bm.edges if e.is_boundary and all(v.co.z>1.79 for v in e.verts)]
result=bmesh.ops.holes_fill(bm,edges=top_edges,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cap.data);bm.free()
cap['mr1_crown_closure_faces']=len(result.get('faces',[]))
copy_obj(bpy.data.objects['MR1_Hair_Leading_Sweep_Cage'],'MR1_CONTEXT_Hair_Leading_Sweep')
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True
sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.world=bpy.data.worlds['MR1_Neutral_World'];sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0;sc.view_settings.gamma=1
sc.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
target=Vector((0,-.01,1.704))
def camera(name,p,scale=.34):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);col.objects.link(o);o.location=p;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=20;d.dof.use_dof=False
for n,p in [('front',(0,.7,1.704)),('profile',(.7,-.01,1.704)),('three_quarter',(.45,.58,1.765)),('opposite',(-.45,.58,1.765)),('rear',(0,-.7,1.704)),('top',(0,-.01,2.4))]:camera('MR1_CONTEXT_'+n,p)
for n,p,e in [('Key',(-.28,.38,2.06),3.4),('Fill',(.32,.24,1.83),.8)]:
    d=bpy.data.lights.new('MR1_CONTEXT_'+n,'AREA');o=bpy.data.objects.new('MR1_CONTEXT_'+n,d);col.objects.link(o);o.location=p;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.energy=e;d.shape='DISK';d.size=.35
sc.camera=bpy.data.objects['MR1_CONTEXT_three_quarter'];sc['mr1_scope']='Unapproved contextual assembly; eye perimeter joins, proportions and expression require review';sc['mr1_operation']='context_initial_orbital_interface'
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        s=a.spaces.active;s.region_3d.view_location=target;s.region_3d.view_distance=.45;s.region_3d.view_rotation=sc.camera.rotation_euler.to_quaternion();s.region_3d.view_perspective='ORTHO';s.overlay.show_wireframes=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for v in ['front','three_quarter','profile']:
    sc.camera=bpy.data.objects['MR1_CONTEXT_'+v];sc.render.filepath=root+'/captures/context_assembly_initial_'+v+'.png';bpy.ops.render.render(write_still=True)
print(json.dumps({'new_context_scene':sc.name,'old_front_faces_removed':removed,'boundary_samples_fitted':20,'crown_hole_faces_added':cap['mr1_crown_closure_faces']}))

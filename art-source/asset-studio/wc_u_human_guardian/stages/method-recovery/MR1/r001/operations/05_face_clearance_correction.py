import bpy,json
assert bpy.context.scene.name=='MR1_FACE_PROOF'
s=bpy.data.objects['MR1_Right_Orbital_Cage'];scene=bpy.context.scene
assert scene['mr1_face_corrections']==1
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
bpy.ops.wm.save_as_mainfile(filepath=root+'/face_before_correction_02.blend',copy=True)
# Last bounded correction: several upper/lateral margin spans cut the spherical
# guide by 0.09-0.17 mm after level-one subdivision. Adjust these cage spans only.
edited=[]
for j in range(2,18):
    s.data.vertices[j].co.y+=.00045
    s.data.vertices[20+j].co.y+=.00060
    edited.extend([j,20+j])
for j in [6,7,8,11,12]:
    s.data.vertices[40+j].co.y+=.00025;edited.append(40+j)
s.data.update()
wire=bpy.data.objects['MR1_FACE_Control_Cage_Wire'];wire.data=s.data.copy();wire.data.materials.clear();wire.data.materials.append(bpy.data.materials['MR1_Cage_Dark'])
scene['mr1_face_corrections']=2;scene['mr1_operation']='face_correction_02_lid_clearance'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for v in ['front','profile','three_quarter','opposite']:
    scene.camera=bpy.data.objects['MR1_FACE_'+v];scene.render.filepath=root+'/captures/face_final_gaze_'+v+'.png';bpy.ops.render.render(write_still=True)
print(json.dumps({'corrective_pass':2,'vertices_edited':edited,'relation':'lid/globe clearance after subdivision','further_correction_requires_review':True}))


import bpy,bmesh,json
assert bpy.context.scene.name=='MR1_FACE_PROOF'
scene=bpy.context.scene;skin=bpy.data.objects['MR1_Right_Orbital_Cage'];wire=bpy.data.objects['MR1_FACE_Control_Cage_Wire']
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
bpy.ops.wm.save_as_mainfile(filepath=root+'/face_before_correction_01.blend',copy=True)
edits={0:(.0145,.0436,1.6872),1:(.017,.0458,1.6903),18:(.017,.0447,1.6845),19:(.0148,.0437,1.6860),
20:(.0135,.0463,1.6876),21:(.0157,.0486,1.6920),38:(.0162,.0480,1.6833),39:(.0137,.0471,1.6851),
40:(.0095,.0560,1.6881),41:(.0125,.0560,1.6961),58:(.012,.061,1.6798),59:(.0097,.0575,1.6837)}
for i,co in edits.items():skin.data.vertices[i].co=co
skin.data.update()
bm=bmesh.new();bm.from_mesh(skin.data)
if sum(f.normal.y*f.calc_area() for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
bm.to_mesh(skin.data);bm.free()
wire.data=skin.data.copy();wire.data.materials.clear();wire.data.materials.append(bpy.data.materials['MR1_Cage_Dark'])
wire.hide_set(False);wire.hide_render=True
scene['mr1_operation']='face_correction_01_inner_corner'
scene['mr1_face_corrections']=1
# Wireframe orientation repair makes the actual cage visible; no extra skin samples.
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.overlay.show_wireframes=True
skin.show_wire=True;skin.show_all_edges=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for view in ['front','three_quarter','opposite']:
    scene.camera=bpy.data.objects['MR1_FACE_'+view];scene.render.filepath=root+'/captures/face_r002_gaze_'+view+'.png'
    bpy.ops.render.render(write_still=True)
wire.hide_render=False;skin.modifiers[0].show_render=False
scene.camera=bpy.data.objects['MR1_FACE_three_quarter'];scene.render.filepath=root+'/captures/face_r002_cage_three_quarter.png'
bpy.ops.render.render(write_still=True)
skin.modifiers[0].show_render=True;wire.hide_render=True
print(json.dumps({'edited_control_points':list(edits),'normals':'outward toward +Y','cage_points':len(skin.data.vertices),'corrective_pass':1}))


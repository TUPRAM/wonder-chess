import bpy,json,bmesh
from mathutils import Vector
scene=bpy.data.scenes['MR1_FACE_PROOF'];bpy.context.window.scene=scene
root='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/method-recovery/MR1/r001'
s=bpy.data.objects['MR1_Right_Orbital_Cage'];g=bpy.data.objects['MR1_Right_Eye_Globe'];w=bpy.data.objects['MR1_FACE_Control_Cage_Wire'];key=bpy.data.objects['MR1_FACE_Key'];fill=bpy.data.objects['MR1_FACE_Fill']
def cap(name,view):
    scene.camera=bpy.data.objects['MR1_FACE_'+view];scene.render.filepath=root+'/captures/'+name+'_'+view+'.png';bpy.ops.render.render(write_still=True)
scene.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
for v in ['front','profile','three_quarter','opposite']:cap('face_final_clay',v)
g.hide_render=True;cap('face_final_opening','three_quarter');g.hide_render=False
scene.view_layers[0].material_override=None;w.hide_render=False;s.modifiers[0].show_render=False
cap('face_final_cage','three_quarter')
s.modifiers[0].show_render=True;cap('face_final_cage_surface','three_quarter');w.hide_render=True
target=Vector((.039,.025,1.687))
key.location=(.328,.35,1.95);fill.location=(-.202,.23,1.77)
for o in [key,fill]:o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
scene.view_layers[0].material_override=bpy.data.materials['MR1_Uniform_Clay']
for v in ['front','three_quarter']:cap('face_final_reverse',v)
key.location=(-.25,.35,1.95);fill.location=(.28,.23,1.77)
for o in [key,fill]:o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
scene.view_layers[0].material_override=None;scene.camera=bpy.data.objects['MR1_FACE_three_quarter']
w.hide_set(True)
bm=bmesh.new();bm.from_mesh(s.data)
audit={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_internal':sum(len(e.link_faces)>2 for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'winding_conflicts':sum(not e.is_contiguous for e in bm.edges if len(e.link_faces)==2)}
bm.free();scene['mr1_face_audit']=json.dumps(audit)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);bpy.ops.wm.save_as_mainfile(filepath=root+'/face_proof_r002.blend',copy=True)
print(json.dumps(audit))


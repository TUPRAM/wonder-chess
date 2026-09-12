import bpy,bmesh,json
from mathutils import Vector
ROOT='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/features-head/FH1/r001'
scene=bpy.data.scenes['FH1_COMBINED_HEAD'];bpy.context.window.scene=scene
head=bpy.data.objects['FH1_Combined_Head_Control_Cage_r004'];eyes=[bpy.data.objects['FH1_Diagnostic_Eye_'+s] for s in ['R','L']]
clay=bpy.data.materials['MR1_Uniform_Clay']
for label in ['front','three_quarter']:
    scene.view_layers[0].material_override=clay
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/final_uniform_clay_'+label+'.png';bpy.ops.render.render(write_still=True)
scene.view_layers[0].material_override=None
for eye in eyes:eye.hide_render=True
for label in ['front','three_quarter']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/final_openings_'+label+'.png';bpy.ops.render.render(write_still=True)
for eye in eyes:eye.hide_render=False
key=bpy.data.objects[scene.name+'_Key'];fill=bpy.data.objects[scene.name+'_Fill'];key_pos=key.location.copy();fill_pos=fill.location.copy();target=Vector((0,-.008,1.680))
key.location.x=-key.location.x;fill.location.x=-fill.location.x
key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
for label in ['front','three_quarter']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/final_reversed_key_'+label+'.png';bpy.ops.render.render(write_still=True)
key.location=key_pos;fill.location=fill_pos;key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
# Capture actual unsmoothed control mesh plus a render-only wire overlay.
dark=bpy.data.materials.new('FH1_Review_Cage_Dark');dark.diffuse_color=(.015,.015,.015,1);dark.use_nodes=True;dark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.015,.015,.015,1)
wire=head.copy();wire.data=head.data.copy();wire.name='FH1_REVIEW_Only_Control_Wire';scene.collection.objects.link(wire);wire.modifiers.clear();wire.data.materials.clear();wire.data.materials.append(dark)
wire_mod=wire.modifiers.new('Review only cage wire','WIREFRAME');wire_mod.thickness=.00018;wire_mod.offset=1;wire_mod.use_replace=True
head.modifiers[0].show_render=False
for eye in eyes:eye.hide_render=True
for label in ['front','three_quarter']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/final_control_cage_'+label+'.png';bpy.ops.render.render(write_still=True)
head.modifiers[0].show_render=True;wire.hide_render=True;wire.hide_set(True)
for eye in eyes:eye.hide_render=False
scene.camera=bpy.data.objects[scene.name+'_three_quarter']
scene['render_allowlist']=json.dumps([o.name for o in scene.objects if not o.hide_render]);scene['status']='FH1 review candidate. Components executed and joined; facial likeness and surface forms REVISE.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Eight executed diagnostic captures: clay, actual openings, reversed light, and unsmoothed cage. Review overlay hidden after captures.')

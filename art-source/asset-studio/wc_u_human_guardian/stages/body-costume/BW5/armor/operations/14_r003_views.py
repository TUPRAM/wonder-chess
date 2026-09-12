import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];rs=bpy.data.scenes['BW5_REFERENCE_POSE_APPROXIMATE']
active=json.loads(s['BW5_owned_visible_parts']);cams={v:bpy.data.objects['BW5_Reference_'+v] for v in ['front','back','right','left','three_quarter']}
def render(scene,name,camera,frame=1):
    bpy.context.window.scene=scene;scene.frame_set(frame);scene.camera=camera;scene.render.filepath=str(R/'captures'/f'r003_{name}.png');bpy.ops.render.render(write_still=True)
for v in ['front','back','profile','three_quarter','rear_three_quarter','context']:
    render(s,'retained_'+v,bpy.data.objects['BW4_Camera_'+v])
for fr in [20,28,29,49,54,73]:render(s,f'retained_pose_{fr:03}',bpy.data.objects['BW4_Camera_three_quarter'],fr)
key=bpy.data.objects['BW4_Key'];location=key.location.copy();rotation=key.rotation_euler.copy();key.location.x=-key.location.x;key.rotation_euler=(Vector((0,0,1.3))-key.location).to_track_quat('-Z','Y').to_euler()
render(s,'retained_reversed_key',bpy.data.objects['BW4_Camera_three_quarter']);key.location=location;key.rotation_euler=rotation
for v,o in cams.items():render(rs,'reference_pose_'+v,o)
# Actual cage edges, separately labeled; this is not the smoothed render with a fake grid.
bpy.context.window.scene=s;s.frame_set(1)
black=bpy.data.materials.new('BW5_CageEdges');black.diffuse_color=(.008,.008,.008,1);black.use_nodes=True;black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.008,.008,.008,1)
for name in active:
    ob=bpy.data.objects[name]
    for m in ob.modifiers:
        if m.type in ['SUBSURF','BEVEL','SOLIDIFY']:m.show_render=False
    ob.data.materials.append(black);m=ob.modifiers.new('ACTUAL_CONTROL_EDGES','WIREFRAME');m.use_replace=False;m.thickness=.00065;m.use_even_offset=False;m.material_offset=len(ob.data.materials)-1
render(s,'retained_actual_control_cage',bpy.data.objects['BW4_Camera_three_quarter'])
for name in active:
    ob=bpy.data.objects[name];ob.modifiers.remove(ob.modifiers['ACTUAL_CONTROL_EDGES']);ob.data.materials.pop(index=len(ob.data.materials)-1)
    for m in ob.modifiers:m.show_render=True
# A color-ID image distinguishes the new waist coverage without claiming texturing.
for layer in s.view_layers:layer.material_override=None
navy=bpy.data.objects['BW5_Navy_Waist_Enclosure'];navy.data.materials.clear();mat=bpy.data.materials.new('BW5_Navy_ID_ONLY');mat.diffuse_color=(.022,.040,.073,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color;navy.data.materials.append(mat)
render(s,'retained_waist_color_ID_NOT_TEXTURED',bpy.data.objects['BW4_Camera_front'])
print('BW5_DELIVERY_VIEWS_COMPLETE',flush=True)

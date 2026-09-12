import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'ada_fixed_hand_checkpoint_ART_REVISE.blend'),load_ui=False,use_scripts=False)
s=bpy.context.scene;o=bpy.data.objects['BW4_ClosedGlove_Correction2']
# Uniform clay lighting diagnostic. Both images share geometry, camera, fill and exposure.
s.camera=bpy.data.objects['BW4_oblique']
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
mat=bpy.data.materials.new('BW4_Diagnostic_Clay');mat.diffuse_color=(.34,.32,.29,1);mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.34,.32,.29,1);bs.inputs['Roughness'].default_value=.7;o.data.materials.clear();o.data.materials.append(mat)
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.12,.12,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
def area(name,pos,energy,size):
 d=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,.065,.025))-ob.location).to_track_quat('-Z','Y').to_euler();d.energy=energy;d.shape='DISK';d.size=size;return ob
key=area('BW4_Key',( .16,.06,.30),1.3,.22);fill=area('BW4_Fill',(-.22,.05,.18),.35,.25)
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.filepath=str(OUT/'captures/final_uniform_clay_key_review.png');bpy.ops.render.render(write_still=True)
key.location=(-.16,.06,.30);key.rotation_euler=(Vector((0,.065,.025))-key.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(OUT/'captures/final_uniform_clay_reversed_key_review.png');bpy.ops.render.render(write_still=True)

print('DIAGNOSTIC_LIGHTING_ONLY_NO_SOURCE_SAVED')

"""Read-only supplementary captures; correct the occluded review board floor."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parents[1]
source=OUT/'Bellback_forms_r003.blend'
expected='5a2931e42bbb8523f3e84ba39f02a5ceab0b1fa31abc3e8319fcf6a1c0d6066b'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
assert Path(bpy.data.filepath).resolve()==source.resolve()
scene=bpy.context.scene; cam=scene.camera; forms=bpy.data.collections['BELLBACK_FORMS']
out=OUT/'review_crowded_aligned';out.mkdir(exist_ok=True)
records=[]
def capture(name,loc,target,scale,size=(960,960),clay=True):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.view_layers[0].material_override=bpy.data.materials['Review_clay'] if clay else None
    scene.render.filepath=str(out/(name+'.png'))
    bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
    records.append(dict(view=name,type='Blender render',camera=list(loc),target=list(target),orthographic_scale_m=scale,resolution=list(size),source_sha256=expected))

bpy.data.objects['Review_floor'].hide_render=True
hidden=[]
for ob in forms.objects:
    if ob.type=='MESH' and ob.get('wc_part_id') not in {'dorsal_bell_shell','bell_trim','bell_carrier_frame','saddle_pad_pair','bell_clapper','clapper_crown_hanger'}:
        ob.hide_render=True;hidden.append(ob)
light_data=bpy.data.lights.new('Review_underside_fill','AREA');light_data.energy=180;light_data.shape='DISK';light_data.size=2
light=bpy.data.objects.new('Review_underside_fill',light_data);scene.collection.objects.link(light)
light.location=(0,0,.4);light.rotation_euler=(Vector((0,0,1.8))-light.location).to_track_quat('-Z','Y').to_euler()
# Previous supplementary review already captured the underside.
for ob in forms.objects:
    if ob.get('wc_part_id')=='saddle_pad_pair':ob.hide_render=True
# Previous supplementary review already captured the clapper.
for ob in forms.objects:ob.hide_render=False
bpy.data.objects.remove(light,do_unlink=True)

# Create board helpers directly outside the excluded source collection.
for i in range(8):
    for j in range(8):
        mesh=bpy.data.meshes.new('Review_tile_mesh')
        x,y=(i-3.5)*2,(j-3.5)*2
        mesh.from_pydata([(x-.99,y-.99,-.003),(x+.99,y-.99,-.003),(x+.99,y+.99,-.003),(x-.99,y+.99,-.003)],[],[(0,1,2,3)])
        tile=bpy.data.objects.new(f'Review_tile_{i}_{j}',mesh);scene.collection.objects.link(tile)
        mat=bpy.data.materials.new(tile.name);mat.diffuse_color=(.08,.14,.105,1) if (i+j)%2 else (.21,.28,.23,1)
        mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=mat.diffuse_color
        mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
        mesh.materials.append(mat)
for index,(x,y) in enumerate(( (x,y) for y in [-3,-1,1,3] for x in [-3,-1,1] )):
    ob=bpy.data.objects.new('Stationary_Bellback_'+str(index),None);scene.collection.objects.link(ob)
    ob.instance_type='COLLECTION';ob.instance_collection=forms;ob.location=(x,y,0);ob.rotation_euler.z=math.pi if y>0 else 0
scene.view_layers[0].layer_collection.children.get(forms.name).exclude=True
capture('crowded12_board_lab_projection_1920x1080',(0,19,27),(0,0,0),max(17.4/1600,16.4/880)*1920,(1920,1080),False)
capture('crowded12_board_lab_elevation_detail',(0,19,27),(0,0,0),11.8,(1280,960),False)
report=dict(source_sha256=expected,source_unchanged=hashlib.sha256(source.read_bytes()).hexdigest()==expected,renders=records,
    correction='Final crowd view aligns all 12 unit roots with the 2 m tile centers. Earlier captures are preserved; supplementary first placements were shifted 1 m in X.',
    limitations=['Static Blender projection proxy with source fallback camera, not a measured live Slate or Unreal capture.',
                 'Cavity isolation hides the organic body; one interior view also hides saddle pads as labeled.',
                 'No source geometry, saved scene, rig, animation or gate was changed.'])
(OUT/'review_crowded_aligned.json').write_text(json.dumps(report,indent=2)+'\n')
print('BELLBACK_REVIEW_SUPPLEMENT_COMPLETE',flush=True)

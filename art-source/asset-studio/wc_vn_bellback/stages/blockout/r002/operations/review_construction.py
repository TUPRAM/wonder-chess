"""Read-only review render of the r002 Bellback source; no saved source mutation."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT=Path(__file__).resolve().parents[1]
source=OUT/'Bellback_forms_r002.blend'
expected='7dca34dcb88513be63894fbd5853f39c80f2155baf7b43ec2c54823b017c3496'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
assert Path(bpy.data.filepath).resolve()==source.resolve()
scene=bpy.context.scene;forms=bpy.data.collections['BELLBACK_FORMS'];cam=scene.camera
render=OUT/'review';render.mkdir(exist_ok=True)
clay=bpy.data.materials['Review_clay'];records=[]
def capture(name,loc,target,scale,size=(960,960),clay_override=True):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.view_layers[0].material_override=clay if clay_override else None
    scene.render.filepath=str(render/(name+'.png'))
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    records.append({'view':name,'type':'Blender render','camera':list(loc),'target':list(target),'orthographic_scale_m':scale,
                    'resolution':list(size),'source_sha256':expected,'material_mode':'neutral clay' if clay_override else 'material IDs'})

capture('face_closeup_clay',(1.7,4,1.25),(0,1,.98),.93)
capture('paw_contact_clay',(1.5,3,.85),(.53,.57,.24),.9)

# The construction isolation hides the body to reveal real carrier/hanger/cavity, not a drawn cutaway.
hidden=[]
for ob in forms.objects:
    if ob.type=='MESH' and ob.get('wc_part_id') not in {'dorsal_bell_shell','bell_trim','bell_carrier_frame','saddle_pad_pair','bell_clapper','clapper_crown_hanger'}:
        ob.hide_render=True;hidden.append(ob)
bpy.data.objects['Review_floor'].hide_render=True
capture('bell_cavity_and_carrier',(3,4,.15),(0,0,1.6),2.1)
for ob in hidden:ob.hide_render=False
bpy.data.objects['Review_floor'].hide_render=False

# Full-board projection uses the exact lab camera direction and the source's fallback 1920x1080 bounds.
# Actual live Slate bounds may differ; this is not an Unreal capture or engine performance pass.
for i in range(8):
    for j in range(8):
        bpy.ops.mesh.primitive_cube_add(size=1,location=((i-3.5)*2,(j-3.5)*2,-.10))
        tile=bpy.context.object;tile.name=f'Review_tile_{i}_{j}';tile.scale=(1.98,1.98,.16)
        mat=bpy.data.materials.new(tile.name);mat.diffuse_color=(.11,.16,.13,1) if (i+j)%2 else (.17,.22,.18,1)
        mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=mat.diffuse_color
        mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
        tile.data.materials.append(mat)
positions=[(-2,-3),(0,-3),(2,-3),(-2,-1),(0,-1),(2,-1),(-2,1),(0,1),(2,1),(-2,3),(0,3),(2,3)]
instances=[]
for index,(x,y) in enumerate(positions):
    instance=bpy.data.objects.new('Stationary_Bellback_'+str(index),None)
    scene.collection.objects.link(instance);instance.instance_type='COLLECTION';instance.instance_collection=forms
    instance.location=(x,y,0);instance.rotation_euler.z=math.pi if y>0 else 0;instances.append(instance)
# Hide the original direct collection via layer exclusion. Instances retain their source geometry.
layer=scene.view_layers[0].layer_collection.children.get(forms.name)
layer.exclude=True
width,height=1920,1080
board_width,board_height=1600,880
world_per_pixel=max(17.4/board_width,16.4/board_height)
ortho_width=world_per_pixel*width
capture('crowded12_lab_projection_1920x1080',(0,19,27),(0,0,0),ortho_width,(width,height),False)
capture('crowded12_lab_elevation_detail',(0,19,27),(0,0,0),11.8,(1280,960),False)
for ob in instances:bpy.data.objects.remove(ob,do_unlink=True)
layer.exclude=False
for ob in list(scene.objects):
    if ob.name.startswith('Review_tile_'):bpy.data.objects.remove(ob,do_unlink=True)
capture('native96_preview',(4,6,3.2),(0,0,1.05),2.75,(96,96),False)

organic=bpy.data.objects['Bellback_organic_continuous_forms']
contact=[organic.matrix_world@v.co for v in organic.data.vertices if v.co.z<=.001]
contact_bounds={'min':[min(v[i] for v in contact) for i in range(3)],'max':[max(v[i] for v in contact) for i in range(3)]}
assert len(contact)>0
material_count=len({m.name for ob in forms.objects if ob.type=='MESH' for m in ob.data.materials if m})
report={'source_sha256':expected,'blender_version':bpy.app.version_string,'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==expected,
        'floor_contact_vertices':len(contact),'contact_bounds_m':contact_bounds,'source_material_ID_count':material_count,
        'camera_basis':{'source':'game/Source/WonderChessRuntime/Private/WCVNextLab.cpp UpdateCamera/BoardPixelBounds fallback',
          'direction_source_units':[0,1900,2700],'declared_viewport':[1920,1080],'fallback_board_pixels':[1600,880],
          'orthographic_width_m':ortho_width,'measured_live_slate_bounds':False,'engine_capture':False},
        'renders':records,'limitations':['12 static linked models; no rig or combat movement','Original dimensions include modeled secondary geometry; no automatic proportion acceptance',
        'No clipping-free animation or engine performance claim','Material colors are source identification only; no texture, UV or material acceptance']}
(OUT/'construction_review.json').write_text(json.dumps(report,indent=2)+'\n')
print('BELLBACK_CONSTRUCTION_REVIEW_COMPLETE',json.dumps(contact_bounds),flush=True)

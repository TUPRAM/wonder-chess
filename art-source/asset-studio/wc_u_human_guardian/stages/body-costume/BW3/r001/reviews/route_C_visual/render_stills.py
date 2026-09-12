"""Read-only C candidate visual packet. In-memory render isolation only."""
import bpy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
SOURCE=OUT.parents[1]/'thumb_route_C_final_method_input.blend'
BW2=OUT.parents[3]/'BW2/r001/ada_bw2_grip_checkpoint_r001_ART_REVISE.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(SOURCE):sha(SOURCE),str(BW2):sha(BW2)}
assert before[str(SOURCE)]=='2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d'
assert before[str(BW2)]=='d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf'
assert Path(bpy.data.filepath).resolve()==SOURCE
s=bpy.context.scene
s.frame_set(25)
g=bpy.data.objects['BW3_Derived_Glove'];body=bpy.data.objects['BW3_Derived_Body'];handle=bpy.data.objects['BW3_Locked_Handle_28mm']
rig=bpy.data.objects['BW3_Derived_Rig']
pose={p.name:[list(row) for row in p.matrix_basis] for p in rig.pose.bones}
lights={o.name:{'matrix':[list(row) for row in o.matrix_world],'energy':o.data.energy} for o in s.objects if o.type=='LIGHT'}
outputs=[]
def render(name,view,visible,kind):
    for o in s.objects:
        if o.type=='MESH':
            o.hide_render=o not in visible
            if o in visible:o.hide_set(False)
    s.camera=bpy.data.objects['BW3_cam_'+view]
    path=OUT/(name+'.png');assert not path.exists()
    s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    outputs.append({'path':str(path),'sha256':sha(path),'frame':25,'camera':s.camera.name,'camera_matrix':[list(row) for row in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale,'render_kind':kind,'engine':s.render.engine,'visible_meshes':[o.name for o in visible]})
for label,obj in [('glove',g),('body',body)]:
    for view in ['oblique','axial']:
        render('C_'+label+'_hidden_'+view,view,[obj],'evaluated original subdivided surface; handle hidden')
# Separate neutral gray values are diagnostic identifiers, not asset materials.
oldmats={g:list(g.data.materials),body:list(body.data.materials)}
for obj,value in [(body,.23),(g,.60)]:
    mat=bpy.data.materials.new('TEMP_DIAG_'+obj.name);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(value,value,value,1);bs.inputs['Roughness'].default_value=.7
    obj.data.materials.clear();obj.data.materials.append(mat)
render('C_body_dark_glove_light_both','oblique',[body,g],'body dark gray and glove light gray; diagnostic distinction only')
for obj,mats in oldmats.items():
    obj.data.materials.clear()
    for mat in mats:obj.data.materials.append(mat)
key=bpy.data.objects['BW3_light_key'];fill=bpy.data.objects['BW3_light_fill']
km=key.matrix_world.copy();fm=fill.matrix_world.copy();key.matrix_world=fm;fill.matrix_world=km
render('C_glove_reversed_key','oblique',[g,handle],'same energies; key/fill locations swapped temporarily')
key.matrix_world=km;fill.matrix_world=fm
cage=g.copy();cage.data=g.data.copy();cage.name='TEMP_C_ActualPosedCage';s.collection.objects.link(cage)
for mod in cage.modifiers:
    if mod.type=='SUBSURF':mod.levels=0;mod.render_levels=0
wiremat=bpy.data.materials.new('TEMP_C_Wire');wiremat.use_nodes=True
bs=wiremat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.012,.012,.012,1)
cage.data.materials.append(wiremat)
w=cage.modifiers.new('Actual cage edges; authoring diagnostic','WIREFRAME');w.thickness=.00016;w.use_replace=False;w.offset=1;w.material_offset=len(cage.data.materials)-1
for view in ['oblique','axial']:
    render('C_actual_posed_base_cage_'+view,view,[cage],'original base cage deformed by original armature; subdivision disabled; wire overlay; not evaluated smooth topology')
bpy.data.objects.remove(cage,do_unlink=True)
# Match the verified BW2 thumb-only isolation render camera and Workbench recipe.
with bpy.data.libraries.load(str(BW2),link=False) as (a,b):b.objects=['BW2_cam_oblique']
comparison_cam=b.objects[0];s.collection.objects.link(comparison_cam);comparison_cam.data.ortho_scale=.285
for o in s.objects:
    if o.type=='MESH':o.hide_render=o!=g
s.camera=comparison_cam
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.6,.6,.6);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.render.resolution_x=900;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
path=OUT/'C_matched_BW2_isolated_thumb_oblique.png';assert not path.exists();s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
outputs.append({'path':str(path),'sha256':sha(path),'frame':25,'camera_matrix':[list(row) for row in comparison_cam.matrix_world],'ortho_scale':comparison_cam.data.ortho_scale,'engine':s.render.engine,'studio_light':s.display.shading.studio_light,'studio_rotation':s.display.shading.studiolight_rotate_z,'kind':'Matched to verified BW2 isolated thumb: saved BW2 oblique camera, .285 scale, 900x1000, studio/single gray .6, cavity BOTH; other fingers OPEN'})
assert pose=={p.name:[list(row) for row in p.matrix_basis] for p in rig.pose.bones}
after={p:sha(Path(p)) for p in before};assert before==after
record={'source_hashes_before':before,'source_hashes_after':after,'source_unchanged':True,'pose_unchanged':True,'action':rig.animation_data.action.name,'lights_saved':lights,'images':outputs,'limits':'Thumb approach only; fingers2-5 OPEN. No complete grip or collision claim. No source saved. Posed base cage and evaluated smooth surfaces explicitly distinguished.'}
(OUT/'stills_metadata.json').write_text(json.dumps(record,indent=2)+'\n')
print('C_STILLS_COMPLETE '+json.dumps({'images':len(outputs),'source_unchanged':True}))

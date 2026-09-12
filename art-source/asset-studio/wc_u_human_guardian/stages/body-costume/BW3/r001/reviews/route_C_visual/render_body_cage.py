"""Expose underlying body's posed base cage and first web; no source saves."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;source=out.parents[1]/'thumb_route_C_final_method_input.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d';assert sha(source)==expected
s=bpy.context.scene;s.frame_set(25)
body=bpy.data.objects['BW3_Derived_Body'];rig=bpy.data.objects['BW3_Derived_Rig']
for o in s.objects:
    if o.type=='MESH':o.hide_render=True
cage=body.copy();cage.data=body.data.copy();cage.name='TEMP_C_BODY_POSED_BASE_CAGE';s.collection.objects.link(cage);cage.hide_render=False;cage.hide_set(False)
for mod in cage.modifiers:
    if mod.type=='SUBSURF':mod.levels=0;mod.render_levels=0
mat=bpy.data.materials.new('TEMP_BODY_CAGE_LINES');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.015,.015,.015,1)
cage.data.materials.append(mat);w=cage.modifiers.new('Actual underlying body cage edges','WIREFRAME');w.thickness=.00014;w.use_replace=False;w.offset=1;w.material_offset=len(cage.data.materials)-1
record={'source':str(source),'source_sha256':expected,'frame':25,'object':'BW3_Derived_Body','images':[],'note':'Actual MPFB-derived body base cage with unchanged armature pose and subdivision disabled; glove and fixture hidden. Not the outer glove cage.'}
for view in ['oblique','axial']:
    s.camera=bpy.data.objects['BW3_cam_'+view];p=out/('C_actual_BODY_posed_base_cage_'+view+'.png');assert not p.exists();s.render.filepath=str(p);bpy.ops.render.render(write_still=True);record['images'].append({'path':str(p),'sha256':sha(p),'camera_matrix':[list(row) for row in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale})
dg=bpy.context.evaluated_depsgraph_get();re=rig.evaluated_get(dg)
center=sum([re.matrix_world@re.pose.bones[n].head for n in ['finger1-1.R','finger1-2.R','finger2-1.R']],Vector())/3
original=bpy.data.objects['BW3_cam_oblique'];cam=original.copy();cam.data=original.data.copy();cam.name='TEMP_BODY_WEB_CLOSEUP';s.collection.objects.link(cam)
oldtarget=original.matrix_world.translation-original.matrix_world.to_3x3().col[2]*.5
cam.location=cam.location+center-oldtarget;cam.data.ortho_scale=.115;s.camera=cam
for label,ob in [('body_cage',cage),('body_evaluated',body)]:
    cage.hide_render=ob!=cage;body.hide_render=ob!=body
    p=out/('C_first_web_closeup_'+label+'.png');assert not p.exists();s.render.filepath=str(p);bpy.ops.render.render(write_still=True);record['images'].append({'path':str(p),'sha256':sha(p),'camera_matrix':[list(row) for row in cam.matrix_world],'ortho_scale':cam.data.ortho_scale,'scope':'new explicitly labeled closeup; same orientation, translated to mean thumb CMC/MCP and index MCP; no image warp'})
assert sha(source)==expected;record['source_unchanged']=True;record['blend_saves']=0;(out/'body_cage_metadata.json').write_text(json.dumps(record,indent=2)+'\n');print('C_BODY_CAGE_DONE')

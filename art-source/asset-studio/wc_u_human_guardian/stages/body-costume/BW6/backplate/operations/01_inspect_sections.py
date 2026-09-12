import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];source=R.parent/'armor/ada_bw6_torso_recut_neck.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
names=['BW6_BackPlate','BW6_Back_Neck_TurnedBorder','BW6_Back_Hem_TurnedBorder']
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'objects':{},'sections':{}}
for name in names:
 o=bpy.data.objects[name];out['objects'][name]={'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons],'matrix_world':[list(r) for r in o.matrix_world],'modifiers':[{'name':m.name,'type':m.type,'thickness':m.thickness if m.type=='SOLIDIFY' else None,'offset':m.offset if m.type=='SOLIDIFY' else None,'target':m.object.name if m.type=='ARMATURE' else None} for m in o.modifiers]}
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear();return t
for fr in (1,49,73):
 s.frame_set(fr);bpy.context.view_layer.update();surfaces={n:tree(bpy.data.objects[n]) for n in ['BW6_BackPlate','BW6_PaddedCoat_Tailored','BW6_BodyFit_Candidate']};rows=[]
 for z in [1.20,1.28,1.35,1.385,1.405,1.425,1.445,1.465,1.48]:
  for x in [-.15,-.12,-.09,-.06,-.03,0,.03,.06,.09,.12,.15]:
   item={'x_m':x,'z_m':z}
   for name,t in surfaces.items():
    hit=t.ray_cast(Vector((x,-.65,z)),Vector((0,1,0)),1.0);item[name]=list(hit[0]) if hit[0] is not None else None
   rows.append(item)
 out['sections'][str(fr)]=rows
s.frame_set(1)
for ob in s.objects:
 if ob.type=='MESH' and ob.name not in names+['BW6_PaddedCoat_Tailored']:ob.hide_render=True
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='OBJECT';s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=0;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
for name in names:bpy.data.objects[name].color=(.52,.55,.6,1)
bpy.data.objects['BW6_PaddedCoat_Tailored'].color=(.36,.17,.13,1)
for view in ['back','profile','three_quarter']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('baseline_pair_'+view+'.png'));bpy.ops.render.render(write_still=True)
(R/'records/baseline_sections.json').write_text(json.dumps(out,indent=2));print('BACKPLATE_INSPECTED',len(out['objects']['BW6_BackPlate']['vertices']))

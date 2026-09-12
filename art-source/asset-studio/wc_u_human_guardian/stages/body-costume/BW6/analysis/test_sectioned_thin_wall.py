"""Independent in-memory seam-wall study. Saves only JSON and diagnostic images."""
import bpy, ast, hashlib, json
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;BASE=R.parents[1];SOURCE=R.parent/'armor/ada_bw6_torso_sectioned_coat.blend'
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R/'inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];front=bpy.data.objects['BW6_FrontPlate']
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');arm=next(m for m in coat.modifiers if m.type=='ARMATURE')
out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_saved':False,'modifier_order':[m.type for m in coat.modifiers],'wall_properties':{n:solid.bl_rna.properties[n].description for n in ['thickness_vertex_group','vertex_group','thickness','offset']},'visible_coat_objects':[{'name':o.name,'hide_render':o.hide_render,'hide_viewport':o.hide_get(),'data':o.data.name} for o in s.objects if o.type=='MESH' and any(x in o.name.lower() for x in ['coat','collar'])],'stages':{},'pose_study':{}}
def rays(g):
 out=[]
 for x in [0,.08,.12]:
  for z in [1.22,1.30,1.38,1.42]:
   h=g[2].ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2)
   out.append({'x':x,'z':z,'front_y':h[0].y if h[0] is not None else None})
 return out
for label in ['base','evaluated','without_armature']:
 if label=='without_armature':arm.show_viewport=False;bpy.context.view_layer.update()
 gc=geom(coat,label=='base');out['stages'][label]={'rays':rays(gc),'max_y':float(gc[0][:,1].max()),'self':screen(gc,gc,True)}
arm.show_viewport=True;bpy.context.view_layer.update()
out['front_plate_rays']=rays(geom(front));out['body_rays']=rays(geom(body))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
vg=coat.vertex_groups.new(name='BW6_ANALYSIS_SEAM_WALL_DIAGNOSTIC')
weights=[]
for v in coat.data.vertices:
 p=coat.matrix_world@v.co;ax=abs(p.x);z=p.z
 neck=smooth((z-1.43)/.025)
 under=smooth((ax-.14)/.02)*smooth((.245-ax)/.02)*smooth((z-1.25)/.03)*smooth((1.42-z)/.03)
 w=1-max(neck,under);vg.add([v.index],w,'REPLACE');weights.append([v.index,w])
solid.vertex_group=vg.name;solid.thickness_vertex_group=.25
out['temporary_wall']={'group':vg.name,'factor':solid.thickness_vertex_group,'base_thickness_m':solid.thickness,'min_thickness_m':solid.thickness*.25,'weights':weights,'model_saved':False}
for fr in [1,20,49]:
 s.frame_set(fr);bpy.context.view_layer.update();gc=geom(coat)
 row={'self':screen(gc,gc,True),'body':screen(gc,geom(body)),'front_plate':screen(gc,geom(front))}
 out['pose_study'][str(fr)]=row
 print('THIN',fr,{k:{a:b for a,b in r.items() if a!='hits'} for k,r in row.items()},flush=True)
(R/'sectioned_thin_wall.json').write_text(json.dumps(out,indent=2),encoding='utf8')
s.frame_set(1);s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.cycles.samples=8;s.render.threads_mode='FIXED';s.render.threads=3
for o in s.objects:
 if o.type=='MESH':o.hide_render=o!=coat
s.render.filepath=str(R/'sectioned_thin_wall_coat_only.png');bpy.ops.render.render(write_still=True)
out['render']=str(R/'sectioned_thin_wall_coat_only.png');out['sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert out['sha256_after']==out['sha256']
(R/'sectioned_thin_wall.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('DONE source unchanged')

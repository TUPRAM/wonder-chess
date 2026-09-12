import bpy,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];source=R/args[0];prefix=args[1]
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
owned=json.loads(s['BW6_owned_visible_parts']);names=['BW6_BodyFit_Candidate','BW6_PaddedCoat_Tailored']+[n for n in owned if any(t in n for t in ['FrontPlate','BackPlate','SideReturn'])]
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frame':1,'units':'world meters','sections':{}}
for z in [1.18,1.31,1.445,1.50]:
 layers={}
 for n in dict.fromkeys(names):
  o=bpy.data.objects[n]
  if o.hide_render:continue
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];segments=[]
  for tri in m.loop_triangles:
   q=[v[i] for i in tri.vertices];cuts=[]
   for a,b in zip(q,q[1:]+q[:1]):
    if (a.z-z)*(b.z-z)<0:
     p=a.lerp(b,(z-a.z)/(b.z-a.z));cuts.append([p.x,p.y])
   if len(cuts)==2:segments.append(cuts)
  e.to_mesh_clear();layers[n]=segments
 out['sections'][str(z)]=layers
(R/'records'/(prefix+'_fit_sections.json')).write_text(json.dumps(out,indent=2));print('BW6_ACTUAL_FIT_SECTIONS_EXPORTED')

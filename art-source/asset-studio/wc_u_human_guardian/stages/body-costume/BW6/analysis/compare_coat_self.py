"""Source-by-source raw/evaluated same-frame screen, with exact raw face pairs."""
import bpy, ast, json, hashlib, collections
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;BASE=R.parents[1]
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R/'inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
sources=[('BW5_r003',BASE/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend','BW4_CONTEXT_BW1_CoatUpper_Continuous'),('BW6_c1',R.parent/'armor/ada_bw6_torso_correction1.blend','BW6_PaddedCoat_Tailored'),('BW6_interface',R.parent/'armor/ada_bw6_torso_interface_work.blend','BW6_PaddedCoat_Tailored')]
out={'scope':'Frame1 same-source raw cage and evaluated surface, nonadjacent transverse triangle test. Triangle pairs are not distinct defects. Raw polygon provenance is exact; evaluated source-face assignment is not inferred. No source saved.','sources':[]}
for tag,path,name in sources:
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);o=bpy.data.objects[name]
 rec={'tag':tag,'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'object':name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'stages':{}}
 for raw in [True,False]:
  g=geom(o,raw);result=screen(g,g,True)
  region=collections.Counter('lower_torso' if h['point'][2]<1.40 else 'neck_shoulder' if h['point'][2]<1.51 else 'collar_top' for h in result['hits'])
  result['z_regions']=dict(region)
  if raw:
   o.data.calc_loop_triangles();ts=o.data.loop_triangles
   faces=collections.Counter(ts[tid].polygon_index for h in result['hits'] for tid in h['triangles'])
   result['raw_offending_faces']=[{'face':i,'triangle_mentions':n,'vertices':list(o.data.polygons[i].vertices),'world':[list(o.matrix_world@o.data.vertices[j].co) for j in o.data.polygons[i].vertices]} for i,n in faces.most_common(20)]
   for h in result['hits']:h['raw_polygons']=[ts[tid].polygon_index for tid in h['triangles']]
  rec['stages']['raw' if raw else 'evaluated']=result
  print(tag,'raw' if raw else 'evaluated',{k:v for k,v in result.items() if k not in ['hits','raw_offending_faces']},flush=True)
 out['sources'].append(rec)
 (R/'coat_self_provenance.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('DONE all source files read-only')

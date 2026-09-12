"""Separate upper navy/plate overlap from low navy/coat contact. Read-only."""
import bpy, ast, hashlib, json
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;BASE=R.parents[1];SOURCE=R.parent/'armor/ada_bw6_torso_outside_work.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
for p,names in [(BASE/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R/'inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
navy=bpy.data.objects['BW6_NavyWaist'];front=bpy.data.objects['BW6_FrontPlate'];coat=bpy.data.objects['BW6_PaddedCoat_Tailored']
ns=[navy,front,coat];gs={n.name:geom(n) for n in ns}
out={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'frame':1,'source_saved':False,'navy_front':screen(gs[navy.name],gs[front.name]),'rays':[],'navy_cage':[[v.index,*list(navy.matrix_world@v.co)] for v in navy.data.vertices]}
for z in [1.18,1.19,1.20,1.21]:
 for x in [0,.025,.05,.075,.10,.125]:
  row={'x':x,'z':z}
  for n in ns:
   h=gs[n.name][2].ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2)
   row[n.name]=h[0].y if h[0] is not None else None
  out['rays'].append(row)
(R/'outside_navy_sections.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('NAVY_FRONT',{k:v for k,v in out['navy_front'].items() if k!='hits'})
for row in out['rays']:
 if row['BW6_NavyWaist'] is not None and row['BW6_FrontPlate'] is not None and row['BW6_NavyWaist']>row['BW6_FrontPlate']:print('NAVY_IN_FRONT',row)

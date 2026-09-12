import bpy,bmesh,json,ast
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_recut_neck.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];wall=next(m for m in coat.modifiers if m.type=='SOLIDIFY')
base=R.parents[1]
for p,names in [(base/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
print('SOLIDIFY',[(p.identifier,p.description) for p in wall.bl_rna.properties if 'clamp' in p.identifier or 'mode' in p.identifier],flush=True)
bm=bmesh.new();bm.from_mesh(coat.data);vs=[v for v in bm.verts if v.co.z>1.42]
bmesh.ops.remove_doubles(bm,verts=vs,dist=.000005);bmesh.ops.dissolve_degenerate(bm,edges=[e for e in bm.edges if all(v.co.z>1.42 for v in e.verts)],dist=.00001)
bm.to_mesh(coat.data);bm.free()
record={'cases':{}}
for label in ['simple_clamped','complex_constraints']:
 wall.thickness_clamp=.5;wall.use_thickness_angle_clamp=True
 if label=='complex_constraints':wall.solidify_mode='NON_MANIFOLD';wall.nonmanifold_thickness_mode='CONSTRAINTS'
 bpy.context.view_layer.update();g=geom(coat);record['cases'][label]={'self':screen(g,g,True),'body':screen(g,geom(bpy.data.objects['BW6_BodyFit_Candidate']))}
 print('WALL',label,{k:v['pairs'] for k,v in record['cases'][label].items()},flush=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(R/('ada_bw6_torso_'+label+'.blend')))
 s.cycles.samples=8;s.render.threads=4;s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.filepath=str(R/'captures'/('wall_'+label+'.png'));bpy.ops.render.render(write_still=True)
(R/'records/wall_construction_probe.json').write_text(json.dumps(record,indent=2));print('BW6_WALL_PROBE_COMPLETE')

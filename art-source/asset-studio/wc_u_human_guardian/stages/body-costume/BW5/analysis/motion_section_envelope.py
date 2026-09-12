import bpy,json,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent;S=R.parents[1]/'BW4/r001/armor';source=S/'ada_armor_checkpoint_FINAL_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];coat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous'];front=bpy.data.objects['BW4_Breastplate_ControlSurface']
data=json.loads((R/'bw4_sections_and_conflicts.json').read_text())
points=[(st['z_m'],r['x_m']) for st in data['stations'] for r in st['rays']]
results={str(p):[] for p in points}
for fr in range(1,98):
 s.frame_set(fr);bpy.context.view_layer.update();rest=rig.data.bones['spine01'].matrix_local;pose=rig.pose.bones['spine01'].matrix
 plate_frame=rig.matrix_world@pose@rest.inverted()@rig.matrix_world.inverted()@front.matrix_world;mi=plate_frame.inverted()
 ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();verts=[mi@ev.matrix_world@v.co for v in me.vertices];bvh=BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
 for z,x in points:
  hitf=bvh.ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2);hitb=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
  results[str((z,x))].append({'frame':fr,'front_y':float(hitf[0].y) if hitf[0] else None,'back_y':float(hitb[0].y) if hitb[0] else None})
 if fr%24==1:print('FRAME',fr,flush=True)
summary=[]
for st in data['stations']:
 for ray in st['rays']:
  values=results[str((st['z_m'],ray['x_m']))];f=[r for r in values if r['front_y'] is not None];b=[r for r in values if r['back_y'] is not None]
  old=ray['surface_y_hits_m'];p={'name':st['name'],'z_m':st['z_m'],'x_m':ray['x_m']}
  if f:
   m=max(f,key=lambda r:r['front_y']);p.update({'max_coat_front_y_m':m['front_y'],'front_frame':m['frame'],'valid_front_samples':len(f)})
   if old['front']:p['min_front_axial_gap_mm']=(min(old['front'])-m['front_y'])*1000
  if b:
   m=min(b,key=lambda r:r['back_y']);p.update({'min_coat_back_y_m':m['back_y'],'back_frame':m['frame'],'valid_back_samples':len(b)})
   if old['back']:p['min_back_axial_gap_mm']=(m['back_y']-max(old['back']))*1000
  summary.append(p)
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'All 97 integer frames of MPFB diagnostic. Coat evaluated in SAME-TIME rigid moving spine01 plate frame, +Y/-Y axial rays. Not global-world envelope, not local-normal clearance, not collision certification. A missing ray does not certify coverage.','summary':summary,'all_samples':results}
(R/'bw4_motion_section_envelope.json').write_text(json.dumps(out,indent=2));print(json.dumps(summary,indent=2),flush=True)

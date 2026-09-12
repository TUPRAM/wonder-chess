import bpy,json,hashlib,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent
S=R.parents[1]/'BW4/r001/armor'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=Path(args[0]) if args else S/'ada_armor_checkpoint_FINAL_ART_REVISE.blend'
prefix=args[1] if len(args)>1 else 'bw4'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig']
names={'body':'BW4_CONTEXT_BW1_IndexedBody','coat':'BW4_CONTEXT_BW1_CoatUpper_Continuous','front':'BW4_Breastplate_ControlSurface','back':'BW4_Backplate_ControlSurface'}
def geom(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
 v=np.array([ev.matrix_world@v.co for v in me.vertices]);tri=np.array([tuple(t.vertices) for t in me.loop_triangles]);ev.to_mesh_clear()
 return v,tri,BVHTree.FromPolygons([Vector(p) for p in v],tri,all_triangles=True)
G={k:geom(bpy.data.objects[n]) for k,n in names.items()}
def hits(g,x,z):
 _,_,b=g;origin=Vector((x,1,z));out=[]
 for _ in range(32):
  h=b.ray_cast(origin,Vector((0,-1,0)),2)
  if h[0] is None:break
  out.append(float(h[0].y));origin=h[0]+Vector((0,-.000005,0))
 return out
def section(g,z):
 v,tri,_=g;vv=v[tri];mask=(vv[:,:,2].min(axis=1)<=z)&(vv[:,:,2].max(axis=1)>=z);vv=vv[mask];lines=[]
 for t in vv:
  pts=[]
  for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:
   if (a[2]-z)*(b[2]-z)<0:pts.append((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2].tolist())
  if len(pts)==2:lines.append(pts)
 return lines
stations=[('waist',1.14),('lower_ribs',1.2225),('chest',1.305),('upper_chest',1.3875),('neck_base',1.47)]
records=[]
for label,z in stations:
 rays=[]
 for x in [0,.025,.05,.075,.10,.125,.15,.175]:
  h={k:hits(g,x,z) for k,g in G.items()};r={'x_m':x,'surface_y_hits_m':h}
  if h['coat'] and h['front']:r['front_inner_to_coat_gap_mm']=(min(h['front'])-max(h['coat']))*1000
  if h['coat'] and h['back']:r['back_inner_to_coat_gap_mm']=(min(h['coat'])-max(h['back']))*1000
  rays.append(r)
 records.append({'name':label,'z_m':z,'t':(z-1.14)/.33,'rays':rays,'section_lines_xy_m':{k:section(g,z) for k,g in G.items()}})
bone={b.name:{'head_world_m':list(rig.matrix_world@b.head_local),'tail_world_m':list(rig.matrix_world@b.tail_local)} for b in rig.data.bones if any(t in b.name for t in ['spine','neck','clavicle','shoulder'])}
cages={k:{'vertices_world_m':[list(bpy.data.objects[n].matrix_world@v.co) for v in bpy.data.objects[n].data.vertices],'modifiers':[{'name':m.name,'type':m.type,'thickness':getattr(m,'thickness',None),'offset':getattr(m,'offset',None),'use_even_offset':getattr(m,'use_even_offset',None)} for m in bpy.data.objects[n].modifiers],'matrix_world':[list(r) for r in bpy.data.objects[n].matrix_world]} for k,n in names.items() if k in ['front','back']}
old=json.loads((S/'records/all97_authoring_frame_surfaces.json').read_text());conflicts={}
for name in old['summary']:
 ff=next((f for f in old['frames'] if f['vs_coat'][name]['confirmed_transverse_pairs']),None)
 worst=max(old['frames'],key=lambda f:f['vs_coat'][name]['confirmed_transverse_pairs'])
 conflict=[]
 for label,fr in [('first',ff),('worst',worst)]:
  if fr is None or not fr['vs_coat'][name]['confirmed_transverse_pairs']:continue
  s.frame_set(fr['frame']);bpy.context.view_layer.update();ob=bpy.data.objects[name];mi=ob.matrix_world.inverted()
  # World object matrix alone is not sufficient for this armature-modified rigid mesh.
  owner=ob.get('owner_bone');rest=rig.data.bones[owner].matrix_local;posed=rig.pose.bones[owner].matrix
  deformed=rig.matrix_world@posed@rest.inverted()@rig.matrix_world.inverted()@ob.matrix_world
  conflict.append({'label':label,'frame':fr['frame'],'count':fr['vs_coat'][name]['confirmed_transverse_pairs'],'owner':owner,'rigid_deformed_mesh_matrix':[list(r) for r in deformed],'examples':[{'triangles':x['triangles'],'world_point_m':x['world_point_m'],'undeformed_mesh_local_point_m':list(deformed.inverted()@Vector(x['world_point_m']))} for x in fr['vs_coat'][name]['examples']]})
 conflicts[name]=conflict
out={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'units':'meters, source metric world +Y anterior, +Z up','section_plane_choice':'Provisional analysis landmarks waist z=1.14 to clavicle z=1.47, body/rig landmarks included for review. No model change. Rays at anterior +Y; all intersections retained, not a global bounding box.','bones':bone,'stations':records,'cages':cages,'historical_bw4_conflicts':conflicts,'historical_conflict_source':str(S/'ada_armor_checkpoint_FINAL_ART_REVISE.blend')}
(R/(prefix+'_sections_and_conflicts.json')).write_text(json.dumps(out,indent=2))
for st in records:
 print(st['name'],st['z_m'],[{k:v for k,v in r.items() if k!='surface_y_hits_m'} for r in st['rays']],flush=True)
print('BONES',json.dumps(bone),flush=True)
print('CONFLICTS',json.dumps(conflicts),flush=True)

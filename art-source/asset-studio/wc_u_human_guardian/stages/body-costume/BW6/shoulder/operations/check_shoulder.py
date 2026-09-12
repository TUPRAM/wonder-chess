import bpy,json,sys,ast,hashlib,itertools,math,numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
q=R.parents[1]/'BW2/r001/integrated-independent/audit_integrated_geometry.py';tree=ast.parse(q.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['segment_triangle','self_audit']],type_ignores=[]),str(q),'exec'),globals())
def geom(o,raw=False):
 if raw:me=o.data;mat=o.matrix_world;ev=None
 else:ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();mat=ev.matrix_world
 me.calc_loop_triangles();co=[mat@v.co for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles]
 if ev:ev.to_mesh_clear()
 return np.array(co),tri,BVHTree.FromPolygons(co,tri,all_triangles=True)
def cross(a,b):
 qa,ta,ba=a;qb,tb,bb=b;out=[]
 for ia,ib in ba.overlap(bb):
  aa=qa[list(ta[ia])];ab=qb[list(tb[ib])];pts=[]
  for one,two in [(aa,ab),(ab,aa)]:
   for i in range(3):
    p=segment_triangle(one[i],one[(i+1)%3],two)
    if p is not None:pts.append(p)
  if pts:out.append({'triangles':[ia,ib],'point_world_m':np.mean(pts,axis=0).tolist()})
 return {'count':len(out),'examples':out[:10]}
def load(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);return s
def lowered(s):
 s.frame_set(1)
 rig=bpy.data.objects['BW4_Armor_Independent_Rig'];rig.animation_data.action=None
 for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
 for side in ['R','L']:
  pb=rig.pose.bones['upperarm01.'+side];basis=rig.matrix_world@pb.bone.matrix_local;ax=(basis.to_3x3().inverted()@Vector((0,1,0))).normalized();pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion(ax,math.radians(32 if side=='R' else -32))
 if s.get('BW6_Relief_Representation')=='AUTHORED_97_FRAME_ACTION':
  h=bpy.data.objects['BW6_R_Cap_SecondaryHinge'];h.animation_data.action=None;h.rotation_euler=(0,math.radians(-8),0);h.location=(0,0,0)
 bpy.context.view_layer.update()
def audit(s,frames):
 coat=bpy.data.objects[s.get('BW6_SHOULDER_COAT','BW4_CONTEXT_BW1_CoatUpper_Continuous')];names=json.loads(s['BW6_SHOULDER_ACTIVE']);records=[]
 for fr in frames:
  if fr=='lowered':lowered(s)
  else:s.frame_set(int(fr),subframe=fr-int(fr));bpy.context.view_layer.update()
  gc=geom(coat);gs={n:geom(bpy.data.objects[n]) for n in names};raw={n:geom(bpy.data.objects[n],True) for n in names}
  r={'frame':fr,'evaluated_coat':{n:cross(gs[n],gc) for n in names},'raw_coat':{n:cross(raw[n],gc) for n in names},'plate_pairs':{a+' / '+b:cross(gs[a],gs[b]) for a,b in itertools.combinations(names,2)},'self':{n:{'raw':self_audit(raw[n][0],list(enumerate(raw[n][1]))),'evaluated':self_audit(gs[n][0],list(enumerate(gs[n][1])))} for n in names}}
  print('AUDIT',fr,{n:v['count'] for n,v in r['evaluated_coat'].items()},{n:{k:v['confirmed_nonadjacent_transverse_pairs'] for k,v in t.items()} for n,t in r['self'].items()},flush=True);records.append(r)
 return records
def render(s,label,cam='shoulder',pose=1,clay=False,cage=False):
 if pose=='lowered':lowered(s)
 else:s.frame_set(pose)
 s.render.engine='CYCLES' if clay else 'BLENDER_WORKBENCH';s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
 if clay:s.cycles.samples=12;s.cycles.use_denoising=True
 else:s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
 s.camera=bpy.data.objects['BW4_Camera_'+cam];s.render.filepath=str(R/'captures'/f'{label}.png')
 if cage:
  names=json.loads(s['BW6_SHOULDER_ACTIVE']);black=bpy.data.materials.new('TEMP_CageEdge');black.diffuse_color=(.003,.003,.003,1)
  for o in s.objects:
   if o.type=='MESH':o.hide_render=o.name not in names
  for n in names:
   o=bpy.data.objects[n];o.data.materials.append(black)
   for m in o.modifiers:m.show_render=False
   w=o.modifiers.new('Actual control cage edges','WIREFRAME');w.thickness=.0007;w.use_replace=False;w.use_even_offset=False;w.material_offset=1
 bpy.ops.render.render(write_still=True)
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:];src=R/args[0];label=args[1];s=load(src)
 frames=list(range(1,98))+[19.5,20.5,24.5,25.5,48.5,49.5,72.5,73.5,'lowered'] if len(args)>2 and args[2]=='all' else [1,20,28,49,54,73,97,'lowered']
 records=audit(s,frames);(R/'records'/f'{label}_audit.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'scope':'Finite noncoplanar transverse screen, excludes self pairs sharing vertices; not continuous collision proof or runtime check.','frames':records},indent=2))
 for cam,pose in [('shoulder',1),('front','lowered'),('shoulder','lowered'),('shoulder',49),('rear_three_quarter',49)]:s=load(src);render(s,f'{label}_{cam}_{pose}',cam,pose)
 s=load(src);render(s,f'{label}_cage',cage=True)

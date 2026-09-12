import bpy,bmesh,json,hashlib,math,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];SOURCE=R/'ada_bw6_side_return_initial.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];panel=bpy.data.objects['BW6_R_FittedSideReturn']
def bv(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[ev.matrix_world@v.co for v in me.vertices];f=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return BVHTree.FromPolygons(v,f)
bvh=bv(coat);p=R/'operations/02_construct_return.py';tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['coatx','point']],type_ignores=[]),str(p),'exec'),globals())
ts=[0,.025,.07,.15,.28,.43,.57,.72,.85,.93,.975,1];hs=[0,.035,.24,.53,.82,.965,1];sections=[]
for j,h in enumerate(hs):
 boundary=.157+.024*h;mid=.158+.012*h+.012*h*h;row=[]
 for t in ts:
  q=point(t,h);q.y+=.006*t**4;cx=coatx(q.y,q.z);sine=math.sin(math.pi*t)
  if cx is not None and sine>.12:mid=max(mid,(cx+.008-(1-sine)*boundary)/sine)
  row.append(q)
 for i,(t,q) in enumerate(zip(ts,row)):
  q.x=boundary*(1-math.sin(math.pi*t))+mid*math.sin(math.pi*t);panel.data.vertices[j*len(ts)+i].co=q
 sections.append({'h':h,'front_back_flange_x':boundary,'controlled_lateral_mid_x':mid})
panel.data.update();bpy.context.view_layer.update();carrier=bv(panel);strap_records=[]
for k,level in enumerate([.25,.72]):
 ob=bpy.data.objects['BW6_R_FittedSideStrap_'+str(k+1)];columns=[.035,.055,.12,.22,.34,.46,.57,.59]
 for j,dh in enumerate([-.050,-.042,.042,.050]):
  for i,t in enumerate(columns):
   q=point(t,level+dh);q.y+=.006*t**4;hit=carrier.ray_cast(Vector((1,q.y,q.z)),Vector((-1,0,0)),1)
   assert hit[0] is not None,'Declared strap point misses carrier'
   q=hit[0]+hit[1]*.0028;ob.data.vertices[j*len(columns)+i].co=q;strap_records.append({'object':ob.name,'vertex':j*len(columns)+i,'carrier_point_m':list(hit[0]),'normal':list(hit[1]),'offset_m':.0028})
 ob.data.update()
panel['correction1']='Each horizontal control section has one measured lateral crown instead of independent x projections; rear flange returns6mm toward torso. Straps seated on final evaluated carrier at declared parametric locations.'
out=R/'ada_bw6_side_return_correction1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));(R/'records/correction1.json').write_text(json.dumps({'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'candidate':str(out),'sections':sections,'strap_attachment_samples':strap_records,'method':panel['correction1']},indent=2))
s.cycles.samples=12;s.render.threads=3
for view in ['three_quarter','profile','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('r001_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('SIDE_RETURN_CORRECTION1_DONE')

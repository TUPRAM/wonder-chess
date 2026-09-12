import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
src=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];rig.data=rig.data.copy();rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name='BW6_Preserved97_Authoring_ONLY'
col=bpy.data.collections.new('BW6_TORSO_RECONSTRUCTION');s.collection.children.link(col)
oldcoat=bpy.data.objects['BW4_CONTEXT_BW1_CoatUpper_Continuous']
coat=oldcoat.copy();coat.data=oldcoat.data.copy();coat.name='BW6_PaddedCoat_Tailored';col.objects.link(coat)
oldcoat.hide_render=True;oldcoat.hide_set(True)
body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody']
def bvh(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear();return bv
bodybv=bvh(body)
def ray(bv,x,z,sign=1):
 h=bv.ray_cast(Vector((x,sign,z)),Vector((0,-sign,0)),2)
 return h[0].y if h[0] is not None else None
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
changes=[]
for v in coat.data.vertices:
 p=v.co.copy();z=p.z
 if 1.10<z<1.505 and abs(p.x)<.19:
  # Tailoring allowance, on the independent garment only. Preserve lateral sleeve.
  weight=smooth((z-1.10)/.09)*smooth((1.515-z)/.065)*smooth((.19-abs(p.x))/.035)
  target=ray(bodybv,p.x,z,1)
  if target is not None and p.y>0:
   y=target+.020
   v.co.y=p.y+(y-p.y)*weight
   changes.append({'vertex':v.index,'before':list(p),'after':list(v.co),'purpose':'tailored padded front,20mm nominal exterior allowance'})
# Remove the ragged source neckline band and replace it with a topological
# annular transition. Its outer loop is the actual one-ring boundary left by the cut.
bm=bmesh.new();bm.from_mesh(coat.data);bm.verts.ensure_lookup_table()
neck_ids=[48,49,50,51,444,176,544,539,540,538,542,543,1119,1121,1120,1115,1117,1116,1122,733,1013,601,600,599,598,1014,1109,1108,1107,1112,1113,1111,537,536,532,533,534,445]
neckset={bm.verts[i] for i in neck_ids};cutfaces={f for v in neckset for f in v.link_faces}
border=[e for e in bm.edges if len([f for f in e.link_faces if f in cutfaces])==1 and len(e.link_faces)==2]
adj={}
for e in border:
 for v in e.verts:adj.setdefault(v,[]).append(e.other_vert(v))
assert all(len(n)==2 for n in adj.values()),'Neck reconstruction needs a simple outer loop'
start=max(adj,key=lambda v:v.co.x);loop=[start];prev=None;cur=start
while True:
 nxt=next(n for n in adj[cur] if n!=prev)
 if nxt==start:break
 loop.append(nxt);prev,cur=cur,nxt
assert len(loop)==len(adj)
outer=[v.co.copy() for v in loop]
# Pick traversal from existing loop; distribute circumference monotonically.
area=sum(outer[i].x*outer[(i+1)%len(loop)].y-outer[(i+1)%len(loop)].x*outer[i].y for i in range(len(loop)))
sign=1 if area>0 else -1
theta=math.atan2(outer[0].y+.066,outer[0].x)
bmesh.ops.delete(bm,geom=list(cutfaces),context='FACES_ONLY')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
previous=loop;n=len(loop)
for j,t in enumerate([.38,.72,1.]):
 new=[]
 for i,p in enumerate(outer):
  a=theta+sign*2*math.pi*i/n
  target=Vector((.103*math.cos(a),-.062+.112*math.sin(a),1.479-.022*max(0,math.sin(a))))
  q=p.lerp(target,t);new.append(bm.verts.new(q))
 for i in range(n):k=(i+1)%n;bm.faces.new((previous[i],previous[k],new[k],new[i]))
 previous=new
# The collar continues from the same shared boundary, so there is no pasted ring.
for t in [.05,.35,.88,1.]:
 new=[]
 for i in range(n):
  a=theta+sign*2*math.pi*i/n
  lower=Vector((.103*math.cos(a),-.062+.112*math.sin(a),1.479-.022*max(0,math.sin(a))))
  top=Vector((.130*math.cos(a),-.049+.124*math.sin(a),1.557-.006*max(0,math.sin(a))))
  new.append(bm.verts.new(lower.lerp(top,t)))
 for i in range(n):k=(i+1)%n;bm.faces.new((previous[i],previous[k],new[k],new[i]))
 previous=new
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(coat.data);bm.free();coat.data.update()
# New collar vertices rigidly follow upper spine; existing garment groups remain.
for v in coat.data.vertices:
 if not v.groups:
  g=coat.vertex_groups.get('spine01') or coat.vertex_groups.new(name='spine01');g.add([v.index],1,'REPLACE')
coat['BW6_method']='Removed original ragged neckline faces; new connected annular shoulder-to-neck transition and flared collar. Front garment independently refitted to source body.'
bpy.context.view_layer.update()
for name in json.loads(s['BW5_owned_visible_parts'])+['BW4_CONTEXT_BW1_PaddedCollar','BW5_Tailored_Collar']:
 o=bpy.data.objects.get(name)
 if o:o.hide_render=True;o.hide_set(True)
owned=[coat]
def mesh(name,verts,faces,thick=.003,owner='spine01',smoothshade=True):
 me=bpy.data.meshes.new(name+'_ControlSurface');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(bpy.data.materials['BW4_Underlayer_Clay'])
 for f in me.polygons:f.use_smooth=smoothshade
 g=o.vertex_groups.new(name=owner);g.add(list(range(len(verts))),1,'REPLACE')
 # One level for rounded transitions; source cage carries all large planes.
 m=o.modifiers.new('Controlled surface','SUBSURF');m.levels=1;m.render_levels=1
 if thick:
  m=o.modifiers.new('Physical wall','SOLIDIFY');m.thickness=thick;m.offset=-1;m.use_even_offset=False
 m=o.modifiers.new('Rigid owner','ARMATURE');m.object=rig;o['owner_bone']=owner;owned.append(o);return o

# Purpose-built front/back/side rings: the lateral route is curved around the
# ribs instead of connecting front and rear by a chord through the coat.
u=[-1,-.985,-.88,-.7,-.46,-.22,-.055,0,.055,.22,.46,.7,.88,.985,1]
tvals=[0,.025,.15,.38,.54,.68,.82,.96,1]
zbase=[1.181,1.188,1.226,1.285,1.325,1.375,1.421,1.470,1.481]
w=[.169,.170,.171,.181,.193,.190,.167,.135,.132]
fp=[.123,.125,.136,.159,.163,.132,.103,.078,.073]
bp=[-.138,-.14,-.145,-.154,-.162,-.170,-.172,-.165,-.163]
fronts=[];backs=[]
for side in ['Front','Back']:
 vs=[];fs=[];front=side=='Front'
 for j,t in enumerate(tvals):
  for a in u:
   aa=abs(a);z=zbase[j]
   if front:
    z+=.017*aa*(1-t)**4
    z-=.045*(1-aa)**1.4*t**5
    y=fp[j]-.075*aa**1.8+.008*(1-aa)
   else:
    z+=.018*(1-aa)*(1-t)**4
    z-=.016*(1-aa)*t**5
    y=bp[j]+.042*aa**1.65
   vs.append((w[j]*a,y,z))
  if j:
   for i in range(len(u)-1):a=(j-1)*len(u)+i;fs.append((a,a+1,a+len(u)+1,a+len(u)))
 ob=mesh('BW6_'+side+'Plate',vs,fs,.0035)
 if front:fronts=vs
 else:backs=vs
 # Integrated turned borders are closed beveled rectangular sections.
 for label,indices in [('Neck',[8*len(u)+i for i in range(len(u))]),('Hem',list(range(len(u))))]:
  points=[Vector(vs[i]) for i in indices];rv=[];rf=[]
  for k,p in enumerate(points):
   tang=points[min(k+1,len(points)-1)]-points[max(0,k-1)];tang.normalize();normal=Vector((0,1 if front else -1,0));inside=tang.cross(normal).normalized()
   if (inside.z>0)!=(label=='Hem'):inside=-inside
   for d,dep in [(0,.001),(.008,.001),(.008,.004),(0,.004)]:rv.append(p+inside*d+normal*dep)
   if k:
    for q in range(4):rf.append(((k-1)*4+q,(k-1)*4+(q+1)%4,k*4+(q+1)%4,k*4+q))
  rf.extend([(3,2,1,0),tuple(range(len(rv)-4,len(rv)))])
  rim=mesh('BW6_'+side+'_'+label+'_TurnedBorder',rv,rf,0)
for sign in [-1,1]:
 vs=[];fs=[]
 for j in range(7):
  p=Vector(fronts[j*len(u)+(len(u)-1 if sign>0 else 0)]);q=Vector(backs[j*len(u)+(len(u)-1 if sign>0 else 0)])
  for k in range(9):
   t=k/8;r=p.lerp(q,t);r.x+=sign*.021*math.sin(math.pi*t);vs.append(r)
  if j:
   for k in range(8):a=(j-1)*9+k;fs.append((a,a+1,a+10,a+9))
 mesh('BW6_SideEnclosure_'+str(sign),vs,fs,.0025)

# Navy torso is one purposefully fitted fabric tube. It encloses body waist
# and overlaps under the plate, without inheriting the old belt's oversized rear radius.
vs=[];fs=[];N=48
for j,(z,rx,ry,cy) in enumerate([(1.071,.158,.113,-.003),(1.079,.156,.112,-.003),(1.12,.15,.111,-.003),(1.154,.152,.116,-.003),(1.204,.157,.125,-.003),(1.215,.159,.128,-.003)]):
 for i in range(N):a=2*math.pi*i/N;vs.append((rx*math.cos(a),cy+ry*math.sin(a),z))
 if j:
  for i in range(N):k=(i+1)%N;fs.append(((j-1)*N+i,(j-1)*N+k,j*N+k,j*N+i))
mesh('BW6_NavyWaist',vs,fs,.002,owner='spine03')
s['BW6_owned_visible_parts']=json.dumps([o.name for o in owned]);s['status']='BW6_CONSTRUCTION_PENDING_REVIEW';s['BW6_scope']='Independent plate/collar/padding/waist reconstruction. Body unmodified; old shoulders, bracers and lower costume contextual.'
s.camera=bpy.data.objects['BW4_Camera_three_quarter'];s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=12
(R/'records/initial_changes.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'garment_changes':changes,'neck_outer_loop_count':n,'body_edits':0,'new_parts':[o.name for o in owned]},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_torso_initial.blend'))
for v in ['front','profile','back','three_quarter']:
 s.camera=bpy.data.objects['BW4_Camera_'+v];s.render.filepath=str(R/'captures'/('initial_'+v+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_INITIAL_RENDERED')

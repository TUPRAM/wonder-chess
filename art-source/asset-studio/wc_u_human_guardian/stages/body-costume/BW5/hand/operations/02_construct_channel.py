"""BW5 initial: remove palm/root/web, build new outside-channel control surface.

Kept four distal CC0 glove pieces are bisected at one fixed construction plane.
The replacement palm, proximal sections and thumb have independent topology.
"""
import bpy,bmesh,json,math,hashlib,faulthandler
faulthandler.dump_traceback_later(25,repeat=True)
import numpy as np
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
OUT=Path(__file__).resolve().parents[1]; BW4=OUT.parents[1]/'BW4/r001'
bpy.ops.wm.open_mainfile(filepath=str(BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend'),load_ui=False,use_scripts=False)
s=bpy.context.scene;old=bpy.data.objects['BW4_ClosedGlove_Correction2']
rec=json.loads((OUT/'records/root_inspection.json').read_text());source=json.loads((BW4/'records/open_glove_geometry.json').read_text())
old.hide_render=True;old.hide_set(True)
old.name='BW5_Retained_BW4_FAILURE_HIDDEN'
V=[];F=[];regions={};distals={};source_map={}
def vert(p): V.append(tuple(p));return len(V)-1
def face(ids):
 if len(set(ids))>=3:F.append(list(ids))
def ring(coords):return [vert(p) for p in coords]
def bridge(a,b):
 assert len(a)==len(b),(len(a),len(b))
 for k in range(len(a)):face([a[k],a[(k+1)%len(a)],b[(k+1)%len(a)],b[k]])
def loop(bm):
 edges=[e for e in bm.edges if e.is_boundary];adj=defaultdict(list)
 for e in edges:
  a,b=e.verts;adj[a].append(b);adj[b].append(a)
 start=next(iter(adj));a=start;prev=None;result=[]
 for _ in range(1000):
  result.append(a);nxt=next(x for x in adj[a] if x!=prev);prev,a=a,nxt
  if a==start:break
 assert len(result)==len(adj),(len(result),len(adj))
 return result
def zipbridge(a,b):
 # Triangulated unequal-count transition with explicit ordered loop correspondence.
 na,nb=len(a),len(b);ia=ib=0
 while ia<na or ib<nb:
  ta=(ia+1)/na if ia<na else 2;tb=(ib+1)/nb if ib<nb else 2
  if abs(ta-tb)<1e-8:face([a[ia%na],a[(ia+1)%na],b[(ib+1)%nb],b[ib%nb]]);ia+=1;ib+=1
  elif ta<tb:face([a[ia%na],a[(ia+1)%na],b[ib%nb]]);ia+=1
  else:face([a[ia%na],b[(ib+1)%nb],b[ib%nb]]);ib+=1

# Predeclared source anatomy, before new contact scores: old source bone weights
# establish which distal surfaces are retained; evaluated indices are not copied.
theta=math.radians(28)
for n in (2,3,4,5):
 print('DISTAL_BEGIN',n,flush=True)
 bm=bmesh.new();lookup={}
 for ids in rec['parts'][str(n)]['faces']:
  seq=[]
  for i in ids:
   if i not in lookup:lookup[i]=bm.verts.new(rec['bw4_vertices'][i])
   seq.append(lookup[i])
  bm.faces.new(seq)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(0,.085,.032),plane_no=(0,math.sin(theta),-math.cos(theta)),clear_outer=True,clear_inner=False)
 for v in list(bm.verts):
  if not v.link_faces:bm.verts.remove(v)
 lp=loop(bm);center=sum((v.co for v in lp),Vector())/len(lp)
 # Cyclic order with positive X at angular zero, using radial inward as Z.
 radial=Vector((0,math.cos(theta),math.sin(theta)));xx=Vector((1,0,0))
 def ang(v):
  d=v.co-center;return math.atan2(d.dot(-radial),d.x)%(2*math.pi)
 lp=sorted(lp,key=ang)
 index={v:vert(v.co) for v in bm.verts}
 for f in bm.faces:face([index[v] for v in f.verts])
 boundary=[index[v] for v in lp]
 distals[n]={'boundary':boundary,'center':list(center),'count':len(lp)}
 regions[f'{n}_retained_distal']=[index[v] for v in bm.verts]
 source_map[str(n)]={'anatomy':'thumb,index,middle,ring,little'[0:0],'basis':'BW4 source finger weights, cut normal to declared 28 degree transverse guide','retained_vertices':len(index),'boundary_vertices':len(lp)}
 bm.free()
 print('DISTAL_END',n,flush=True)

# Deliberately flattened root cross sections, separately sized and staggered.
# Each root approaches the hilt along the lower outside face, then rounds the
# forward lower corner before joining the retained distal cage.
layout={2:(.027,.0095,.090,.0065,.0095),3:(.003,.010,.092,.006,.010),4:(-.019,.009,.090,.006,.0095),5:(-.039,.0077,.086,.006,.0085)}
rootloops={};rootangles={};route_record={}
for n,(xc,wx,yc,zc,wz) in layout.items():
 print('ROOT',n,flush=True)
 count=16;aa=[2*math.pi*k/count for k in range(count)]
 root=ring([(xc+wx*math.cos(a),yc,zc+wz*math.sin(a)) for a in aa]);rootloops[n]=root;rootangles[n]=aa
 # Polygonal bent proximal construction, not a rotation search or smoothing field.
 sections=[(yc,zc,0,1),(.101,.013,math.radians(31),1.00),(.108,.027,math.radians(72),.96),(.107,.040,math.radians(116),.94)]
 prev=root;route_record[str(n)]=[]
 for j,(y,z,turn,width) in enumerate(sections[1:],1):
  # Longitudinal direction turns from +Y to +Z; palmar inner side points
  # toward the empty grip channel and remains outside its octagonal boundary.
  nz=Vector((0,-math.sin(turn),math.cos(turn)))
  coords=[Vector((xc+wx*width*math.cos(a),y,z))+nz*(wz*math.sin(a)) for a in aa]
  nxt=ring(coords);bridge(prev,nxt);prev=nxt
  route_record[str(n)].append({'center_m':[xc,y,z],'inner_outer_cross_section_m':[list(p) for p in coords]})
 end=distals[n]['boundary'];endcenter=Vector(distals[n]['center'])
 # Match each contour by angle around its own longitudinal frame; do not bridge
 # across an arbitrary vertex ordering. Retained section is the final contour.
 zipbridge(prev,end)
 regions[f'{n}_new_root']=[i for a in [root,prev] for i in a]

# Connected palm surface. The front row follows separate finger opening halves;
# recessed interdigital valleys are true shared boundary edges, not pasted sheets.
topfront=[];bottomfront=[]
for ni,n in enumerate((5,4,3,2)):
 r=rootloops[n];half=len(r)//2
 top=[r[k] for k in range(half,-1,-1)]
 bottom=[r[k%len(r)] for k in range(half,len(r)+1)]
 if ni:
  prior=topfront[-1];nextid=top[0];p=(Vector(V[prior])+Vector(V[nextid]))*.5;p.y-=.010
  valley=vert(p);topfront.append(valley);bottomfront.append(valley)
 topfront+=top;bottomfront+=bottom
assert len(topfront)==len(bottomfront)
N=len(topfront);toprows=[];bottomrows=[]
print('PALM',N,flush=True)
for row,t in enumerate((0,.2,.45,.70,.86,1)):
 tr=[];br=[]
 for j,(ti,bi) in enumerate(zip(topfront,bottomfront)):
  if row==5:tr.append(ti);br.append(bi);continue
  xf=(V[ti][0]+V[bi][0])*.5
  width=.62+.38*math.sin(t*math.pi/2)
  x=xf*width;yf=(V[ti][1]+V[bi][1])*.5;y=.023+(yf-.023)*t
  lateral=abs(xf/.049)
  ztop=.016*(1-.33*lateral**2)-.004*t+.002*math.sin(t*math.pi)
  zbot=-.016*(1-.18*lateral**2)+.011*t
  if row==4:
   ztop=.5*ztop+.5*V[ti][2];zbot=.5*zbot+.5*V[bi][2]
  tr.append(vert((x,y,ztop)));br.append(vert((x,y,zbot)))
 toprows.append(tr);bottomrows.append(br)
for rows in [toprows,bottomrows]:
 for ra,rb in zip(rows,rows[1:]):
  for j in range(N-1):face([ra[j],ra[j+1],rb[j+1],rb[j]])
for j in (0,N-1):
 for k in range(5):face([toprows[k][j],toprows[k+1][j],bottomrows[k+1][j],bottomrows[k][j]])
# Palm/front gap edges share vertices and require no overlapping closing patch.
for j in range(N-1):
 if topfront[j]==bottomfront[j] and topfront[j+1]==bottomfront[j+1]:continue
 # Finger halves enclose openings. Inter-finger links already share endpoints.

# Preserve the exact 20-vertex source wrist opening and bridge it to the new palm.
from collections import Counter
counts=Counter(tuple(sorted((a,b))) for f in source['faces'] for a,b in zip(f,f[1:]+f[:1]))
wristids=sorted({i for e,c in counts.items() if c==1 for i in e})
wristcoords=[Vector(source['vertices_m'][i]) for i in wristids]
wristcoords.sort(key=lambda p:math.atan2(p.z,p.x)%(2*math.pi))
wrist=ring(wristcoords);prox=toprows[0]+list(reversed(bottomrows[0]))
prox.sort(key=lambda i:math.atan2(V[i][2],V[i][0])%(2*math.pi))
zipbridge(wrist,prox);regions['wrist_exact_source_opening']=wrist
print('WRIST',flush=True)

# Open a bounded thenar window in the newly built right palm and construct its
# rounded branch. This is new geometry: no old folded web remains beneath it.
right=N-1;holecorners=[toprows[1][right],toprows[2][right],toprows[3][right],bottomrows[3][right],bottomrows[2][right],bottomrows[1][right]]
remove=[]
for k in (1,2):remove.append(set([toprows[k][right],toprows[k+1][right],bottomrows[k+1][right],bottomrows[k][right]]))
F[:]=[f for f in F if set(f) not in remove]
# Root ring takes its actual boundary in order. Intermediate shaped rings retain
# a broad thenar volume and route thumb toward the back face of the fixed grip.
prev=holecorners
thumb_sections=[((.048,.045,.006),(.011,.015)),((.049,.048,.019),(.010,.013)),((.043,.055,.033),(.009,.012)),((.034,.064,.043),(.008,.010)),((.021,.066,.039),(.007,.009)),((.013,.067,.034),(.005,.006)),((.010,.067,.032),(.0025,.003))]
thumbids=[];lastdir=None
for k,(cc,rr) in enumerate(thumb_sections):
 c=Vector(cc);past=Vector(thumb_sections[max(0,k-1)][0]) if k else Vector((.035,.045,.005));future=Vector(thumb_sections[min(k+1,len(thumb_sections)-1)][0]);t=(future-past).normalized()
 u=Vector((0,1,0));u=(u-t*u.dot(t)).normalized();v=t.cross(u).normalized()
 aa=[2*math.pi*j/16 for j in range(16)]
 nxt=ring([c+u*(rr[0]*math.cos(a))+v*(rr[1]*math.sin(a)) for a in aa])
 # Actual branch ordering is explicit and audited below; unequal root transition.
 if len(prev)==len(nxt):bridge(prev,nxt)
 else:zipbridge(prev,nxt)
 prev=nxt;thumbids+=nxt
tip=vert((.0095,.067,.0315))
for k in range(len(prev)):face([prev[k],prev[(k+1)%len(prev)],tip])
regions['thumb_new_surface']=thumbids
print('THUMB',len(V),len(F),flush=True)

unique={};remap={};clean=[]
for i,p in enumerate(V):
 key=tuple(round(float(c),7) for c in p)
 if key not in unique:unique[key]=len(clean);clean.append(p)
 remap[i]=unique[key]
F=[[remap[i] for i in f] for f in F]
F=[list(dict.fromkeys(f)) for f in F if len(set(f))>=3]
me=bpy.data.meshes.new('BW5_Outside_Channel_Editable_Cage');me.from_pydata(clean,[],F);me.update()
bm=bmesh.new();bm.from_mesh(me);print('BM_READ',flush=True)
print('BM_DETERMINISTIC_COORDINATE_WELD',flush=True)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));print('BM_NORMALS',flush=True)
bm.to_mesh(me);bm.free();me.update();print('BM_WRITTEN',flush=True)
o=bpy.data.objects.new('BW5_ClosedGlove_Initial',me);s.collection.objects.link(o);o.color=(.55,.53,.50,1)
for p in me.polygons:p.use_smooth=True
sub=o.modifiers.new('Retained review subdivision 1','SUBSURF');sub.levels=1;sub.render_levels=1
o['method']='New palm, four outside-route proximal cages and rounded thumb branch; old proximal and web faces removed. Existing CC0 distal finger shapes retained beyond fixed bisect plane.'
o['status']='INITIAL_LOCAL_CONSTRUCTION_REVIEW_REQUIRED'
o['contact_mapping']='Anatomy predeclared from source finger-weight family; new pad scores not yet eligible until construction clears.'
s.name='BW5_HAND_OUTSIDE_CHANNEL_INITIAL';s['BW5_scope']='Fixed glove local construction only. No human approval or runtime acceptance.'
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
s.camera=bpy.data.objects['BW4_oblique']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_bw5_hand_initial.blend'))
for name in ('palm','dorsal','side','underside','oblique','axial'):
 s.camera=bpy.data.objects['BW4_'+name]
 s.render.filepath=str(OUT/'captures'/('initial_'+name+'.png'));bpy.ops.render.render(write_still=True)
 if name in ('palm','oblique','side','axial'):
  for ob in s.objects:
   if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
  s.render.filepath=str(OUT/'captures'/('initial_hilt_only_'+name+'.png'));bpy.ops.render.render(write_still=True)
  for ob in s.objects:
   if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
record={'source':str(BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend'),'source_sha256':hashlib.sha256((BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend').read_bytes()).hexdigest(),'attempt':'initial','new_vertices':len(me.vertices),'new_faces':len(me.polygons),'old_faces_retained':sum(len(rec['parts'][str(n)]['faces']) for n in (2,3,4,5)),'retained_distal':source_map,'proximal_sections':route_record,'old_to_new_evaluated_ids_reused':False,'handle_registration':'Unchanged BW4 selected hilt and rigid placement; 30x26 mm, 110 mm exposed, original guard/blade','representation':'Visible CC0 glove derivative, no underlying hand deletion or bare-hand repair claim','runtime':'NOT_RUN_LOCAL_GATE_REQUIRED'}
(OUT/'records/initial_construction.json').write_text(json.dumps(record,indent=2))
print('BW5_HAND_INITIAL',len(me.vertices),len(me.polygons),flush=True)

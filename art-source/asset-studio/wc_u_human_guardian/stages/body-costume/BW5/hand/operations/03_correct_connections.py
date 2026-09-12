"""BW5 bounded corrective construction: new outside-channel glove cage.

All failed BW4 palm/root/web and distal inner surfaces are replaced here.
The exact source wrist opening and equipment are retained.
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
# BW5 first substantive correction: every retained distal piece failed a full
# surface check at its inner face. Preserve them as source references, but replace
# their geometry in this candidate with new articulated, flattened control sections.
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
 sections=[(yc,zc,0,1),(.103,.010,math.radians(30),1.00),(.113,.029,math.radians(77),1.00),(.108,.050,math.radians(130),.99),(.088,.060,math.radians(182),.94),(.070+(n==5)*.006,.054,math.radians(226),.85),(.065+(n==5)*.008,.048,math.radians(250),.62),(.063+(n==5)*.009,.046,math.radians(250),.32)]
 prev=root;route_record[str(n)]=[];new_digit_ids=list(root)
 for j,(y,z,turn,width) in enumerate(sections[1:],1):
  nz=Vector((0,-math.sin(turn),math.cos(turn)))
  coords=[]
  for a in aa:
   cx=math.cos(a);sz=math.sin(a)
   # Broad pad and dorsal planes with rounded corners, not a round bevel strand.
   px=math.copysign(abs(cx)**.78,cx);pz=math.copysign(abs(sz)**.72,sz)
   coords.append(Vector((xc+wx*width*px,y,z))+nz*(wz*min(width,1)*pz))
  nxt=ring(coords);bridge(prev,nxt);prev=nxt;new_digit_ids+=nxt
  route_record[str(n)].append({'center_m':[xc,y,z],'inner_outer_cross_section_m':[list(p) for p in coords]})
 tip=vert((xc,sections[-1][0]-.0008,sections[-1][1]-.0008))
 for k in range(len(prev)):face([prev[k],prev[(k+1)%len(prev)],tip])
 regions[f'{n}_new_digit']=new_digit_ids
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
def angled_zip(a,b):
 pa=[math.atan2(V[i][2],V[i][0])%(2*math.pi) for i in a]
 pb=[math.atan2(V[i][2],V[i][0])%(2*math.pi) for i in b]
 ia=ib=0;na=len(a);nb=len(b)
 while ia<na or ib<nb:
  ta=pa[(ia+1)%na]+(2*math.pi if ia+1>=na else 0) if ia<na else 20
  tb=pb[(ib+1)%nb]+(2*math.pi if ib+1>=nb else 0) if ib<nb else 20
  if ta<tb:face([a[ia%na],a[(ia+1)%na],b[ib%nb]]);ia+=1
  else:face([a[ia%na],b[(ib+1)%nb],b[ib%nb]]);ib+=1
angled_zip(wrist,prox);regions['wrist_exact_source_opening']=wrist
print('WRIST',flush=True)

# Open a bounded thenar window in the newly built right palm and construct its
# rounded branch. This is new geometry: no old folded web remains beneath it.
right=N-1;holecorners=[toprows[1][right],toprows[2][right],toprows[3][right],bottomrows[3][right],bottomrows[2][right],bottomrows[1][right]]
remove=[]
for k in (1,2):remove.append(set([toprows[k][right],toprows[k+1][right],bottomrows[k+1][right],bottomrows[k][right]]))
F[:]=[f for f in F if set(f) not in remove]
# Root ring takes its actual boundary in order. Intermediate shaped rings retain
# a broad thenar volume and route thumb toward the back face of the fixed grip.
center=sum((Vector(V[i]) for i in holecorners),Vector())/len(holecorners)
# Explicit Y/Z angular correspondence removes the twisted root branch.
holecorners.sort(key=lambda i:math.atan2(V[i][2]-center.z,V[i][1]-center.y)%(2*math.pi))
prev=holecorners
thumb_sections=[((.046,.047,.006),(.012,.011)),((.044,.052,.018),(.010,.010)),((.037,.058,.029),(.009,.009)),((.026,.061,.033),(.008,.008)),((.017,.062,.032),(.006,.006)),((.012,.062,.030),(.003,.003))]
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
tip=vert((.011,.062,.0295))
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
o=bpy.data.objects.new('BW5_ClosedGlove_Correction1',me);s.collection.objects.link(o);o.color=(.55,.53,.50,1)
for p in me.polygons:p.use_smooth=True
sub=o.modifiers.new('Retained review subdivision 1','SUBSURF');sub.levels=1;sub.render_levels=1
o['method']='New palm, four outside-route proximal cages and rounded thumb branch; old proximal and web faces removed. Failed BW4 distal inner surfaces also replaced using broad-pad articulated control sections. Source wrist opening retained exactly.'
o['status']='INITIAL_LOCAL_CONSTRUCTION_REVIEW_REQUIRED'
o['contact_mapping']='Anatomy predeclared from source finger-weight family; new pad scores not yet eligible until construction clears.'
s.name='BW5_HAND_OUTSIDE_CHANNEL_CORRECTION1';s['BW5_scope']='Fixed glove local construction only. No human approval or runtime acceptance.'
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
s.camera=bpy.data.objects['BW4_oblique']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_bw5_hand_correction1.blend'))
for name in ('palm','dorsal','side','underside','oblique','axial'):
 s.camera=bpy.data.objects['BW4_'+name]
 s.render.filepath=str(OUT/'captures'/('correction1_'+name+'.png'));bpy.ops.render.render(write_still=True)
 if name in ('palm','oblique','side','axial'):
  for ob in s.objects:
   if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
  s.render.filepath=str(OUT/'captures'/('correction1_hilt_only_'+name+'.png'));bpy.ops.render.render(write_still=True)
  for ob in s.objects:
   if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
record={'source':str(BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend'),'source_sha256':hashlib.sha256((BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend').read_bytes()).hexdigest(),'attempt':'correction1','new_vertices':len(me.vertices),'new_faces':len(me.polygons),'old_faces_retained':0,'retained_distal':{},'anatomical_digit_construction':regions,'proximal_sections':route_record,'old_to_new_evaluated_ids_reused':False,'handle_registration':'Unchanged BW4 selected hilt and rigid placement; 30x26 mm, 110 mm exposed, original guard/blade','representation':'Visible CC0 glove derivative, no underlying hand deletion or bare-hand repair claim','runtime':'NOT_RUN_LOCAL_GATE_REQUIRED'}
(OUT/'records/correction1_construction.json').write_text(json.dumps(record,indent=2))
print('BW5_HAND_INITIAL',len(me.vertices),len(me.polygons),flush=True)

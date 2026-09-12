"""Second and final substantive correction: connected palm displacement field and local web cage reconstruction."""
import bpy,bmesh,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix
OUT=Path(__file__).resolve().parents[1]
d=json.loads((OUT/'records/open_glove_geometry.json').read_text());v0=np.array(d['vertices_m']);points={}
for n in range(1,6):
 points[n]=np.array([d['joints'][f'finger{n}-{j}.R']['head'] for j in (1,2,3)]+[d['joints'][f'finger{n}-3.R']['tail']])
def closest(v,pp):
 best=(1e9,None);acc=0
 for a,b in zip(pp,pp[1:]):
  ln=np.linalg.norm(b-a);t=(b-a)/ln;u=np.clip(np.dot(v-a,t),0,ln);q=a+t*u;score=np.dot(v-q,v-q)
  if score<best[0]:best=(score,(acc+u,q,t))
  acc+=ln
 return best[1]
def smooth_path(pp):
 # Centripetal-looking tangent-limited cubic interpolation, sampled by distance.
 seq=[]
 for i in range(len(pp)-1):
  a,b=pp[i],pp[i+1];m0=(b-pp[max(0,i-1)])/2 if i else b-a;m1=(pp[min(len(pp)-1,i+2)]-a)/2 if i<len(pp)-2 else b-a
  for t in np.linspace(0,1,81,endpoint=False):seq.append((2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*b+(t**3-t*t)*m1)
 seq.append(pp[-1]);seq=np.array(seq);dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(seq,axis=0),axis=1))];return seq,dist
thumbpp=np.array([[.025,.038,.006],[.050,.049,.029],[.051,.066,.052],[.020,.061,.027]])
thumbseq,thumbdist=smooth_path(thumbpp)
# Continuous parallel-transport thumb frames remove the earlier abrupt roll.
thumb_t=[];thumb_x=[];thumb_z=[]
old_t=Vector(points[1][1]-points[1][0]).normalized()
old_x=Vector((1,0,0));old_x=(old_x-old_t*old_x.dot(old_t)).normalized()
for k in range(len(thumbseq)):
 tt=Vector(thumbseq[min(k+1,len(thumbseq)-1)]-thumbseq[max(0,k-1)]).normalized()
 if k==0:xx=old_t.rotation_difference(tt) @ old_x
 else:xx=thumb_t[-1].rotation_difference(tt) @ thumb_x[-1]
 xx=(xx-tt*xx.dot(tt)).normalized();zz=xx.cross(tt).normalized()
 thumb_t.append(tt);thumb_x.append(xx);thumb_z.append(zz)
end=Vector((0,.024,.005));tt=thumb_t[-1];end=(end-tt*end.dot(tt)).normalized()
roll=math.atan2(tt.dot(thumb_z[-1].cross(end)),thumb_z[-1].dot(end))
for k in range(len(thumbseq)):
 a=max(0,min(1,(thumbdist[k]/thumbdist[-1]-.32)/.68));a=a*a*(3-2*a)
 q=Matrix.Rotation(roll*a,3,thumb_t[k]);thumb_x[k]=q @ thumb_x[k];thumb_z[k]=q @ thumb_z[k]
layout={2:(.027,.024,-65),3:(.003,.025,-66),4:(-.019,.0235,-65),5:(-.039,.021,-57)}
target=v0.copy();fixed=np.zeros(len(v0),bool);roles=[];predeclared={str(n):[] for n in range(1,6)}
for i,(v,w) in enumerate(zip(v0,d['weights'])):
 fam={n:sum(w.get(f'finger{n}-{j}.R',0) for j in (1,2,3)) for n in range(1,6)};n=max(fam,key=fam.get);roles.append(n)
 along,c,t=closest(v,points[n]);xx=np.array([1.,0,0]);xx-=t*np.dot(xx,t);xx/=np.linalg.norm(xx);zz=np.cross(xx,t);off=v-c;dx=np.dot(off,xx);dz=np.dot(off,zz)
 # Strong anatomical constraints only distal to each base. All short root
 # transitions share one field, so neighboring vertices cannot choose competing
 # whole-finger transforms as in the rejected initial construction.
 if fam[n]>.88 and along>(.028 if n==1 else .007):
  fixed[i]=True
  if n==1:
   oldlength=np.linalg.norm(np.diff(points[n],axis=0),axis=1).sum();a=along/oldlength*thumbdist[-1];ii=int(np.clip(np.searchsorted(thumbdist,a),1,len(thumbseq)-1));q=thumbseq[ii];nx=np.array(thumb_x[ii]);nz=np.array(thumb_z[ii]);target[i]=q+nx*dx+nz*dz
  else:
   xc,rad,start=layout[n];a=math.radians(start)+along/rad;nc=np.array([xc,.085+rad*math.cos(a),.032+rad*math.sin(a)]);nz=np.array([0,-math.cos(a),-math.sin(a)]);target[i]=nc+np.array([dx,0,0])+nz*dz
  if w.get(f'finger{n}-3.R',0)>.55 and dz>.002:predeclared[str(n)].append(i)
 elif v[1]<.026 or (v[1]<.048 and v[0]<.012) or (.012<v[0]<.036 and .031<v[1]<.060 and fam[1]<.7):
  fixed[i]=True;target[i,2]+=.005*math.exp(-((v[0]+.004)/.04)**2-((v[1]-.055)/.04)**2)
adj=[set() for _ in v0]
for f in d['faces']:
 for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
free=np.where(~fixed)[0];fi={v:i for i,v in enumerate(free)}
L=np.zeros((len(free),len(free)));rhs=np.zeros((len(free),3));delta=target-v0
for vi,row in fi.items():
 L[row,row]=1
 for nb in adj[vi]:
  w=1/len(adj[vi])
  if fixed[nb]:rhs[row]+=w*delta[nb]
  else:L[row,fi[nb]]-=w
delta[free]=np.linalg.solve(L,rhs);verts=v0+delta
bpy.ops.wm.open_mainfile(filepath=str(OUT/'ada_fixed_hand_initial.blend'),load_ui=False,use_scripts=False)
s=bpy.context.scene;o=bpy.data.objects['BW4_ClosedGlove_Initial'];oldmesh=o.data
me=bpy.data.meshes.new('BW4_Rebuilt_Connected_Base_Cage');me.from_pydata(verts.tolist(),[],d['faces']);me.update();o.data=me;o.name='BW4_ClosedGlove_Correction2'
o.vertex_groups.clear()
for n,ids in predeclared.items():vg=o.vertex_groups.new(name='CONTACT_'+n+'_source_pad');vg.add(ids,1,'REPLACE')
# Actual face replacement: insert local face centers and dissolve old shared
# web edges. This produces new transverse control edges instead of capping the
# thumb root with one planar n-gon. Shape remains tied to the continuous target.
bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table()
patch=[f for f in bm.faces if .020<sum(v0[v.index,0] for v in f.verts)/len(f.verts)<.051 and .043<sum(v0[v.index,1] for v in f.verts)/len(f.verts)<.087]
oldcount=len(patch);inside=[e for e in bm.edges if len(e.link_faces)==2 and all(f in patch for f in e.link_faces)]
bmesh.ops.poke(bm,faces=patch,offset=0,center_mode='MEAN_WEIGHTED')
if inside:bmesh.ops.dissolve_edges(bm,edges=inside,use_verts=False,use_face_split=False)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
for p in me.polygons:p.use_smooth=True
o['method']='Fixed source digit sections, continuously transported thumb surface frames and retained thenar support; local web rebuilt across original edges'
o['revision']='Second and final substantive correction; not a new attempt counter'
s['BW4_scope']='CORRECTION2_LOCAL_REVIEW_REQUIRED'
for name in ['palm','dorsal','side','underside','oblique','axial']:
 s.camera=bpy.data.objects['BW4_'+name]
 for ob in s.objects:
  if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
 s.render.filepath=str(OUT/'captures'/('correction2_'+name+'.png'));bpy.ops.render.render(write_still=True)
 if name in ['side','underside','oblique']:
  for ob in s.objects:
   if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
  s.render.filepath=str(OUT/'captures'/('correction2_'+name+'_hidden.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW4_oblique']
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
sub=o.modifiers[0];sub.show_render=False
w=o.modifiers.new('Actual cage','WIREFRAME');w.thickness=.00032;w.use_replace=False;s.render.filepath=str(OUT/'captures/correction2_cage.png');bpy.ops.render.render(write_still=True);o.modifiers.remove(w);sub.show_render=True
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_fixed_hand_correction2.blend'))
(OUT/'records/correction2.json').write_text(json.dumps({'fixed_vertices':int(fixed.sum()),'local_free_transition_vertices':len(free),'source_web_faces_replaced':oldcount,'candidate_vertices':len(me.vertices),'candidate_faces':len(me.polygons),'predeclared_contact_source_vertices':predeclared,'no_source_mesh_modified':True,'thumb_frame_roll_radians':roll,'substantive_revision':2},indent=2))
print('CORRECTION2',len(me.vertices),len(me.polygons),'REBUILT_WEB_FACES',oldcount)

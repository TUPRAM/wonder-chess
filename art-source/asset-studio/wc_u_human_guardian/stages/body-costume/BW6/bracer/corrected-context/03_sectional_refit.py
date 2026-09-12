import bpy,bmesh,json,math,hashlib,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent;SOURCE=R/'ada_bw6_bracers_actual_sleeve_initial.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig'];bpy.context.view_layer.update()
print('ACTION',rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,'NLA',[(t.name,t.mute) for t in rig.animation_data.nla_tracks] if rig.animation_data else [],flush=True)
world=[]
for n in ['BW4_CONTEXT_BW1_IndexedBody','BW6_PaddedCoat_Tailored','BW4_CONTEXT_BW1_Glove_Pair_SourceFit']:
 o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();world.extend([ev.matrix_world@v.co for v in m.vertices]);ev.to_mesh_clear()
frames=json.loads(s['BW6_correct_context_bracer_record']);records=[]
for rec in frames:
 side=rec['side'];W=Vector(rec['frame']['wrist']);A=Vector(rec['frame']['proximal']);D=Vector(rec['frame']['dorsal']);T=Vector(rec['frame']['transverse']);points=[]
 for v in world:
  q=v-W;t=q.dot(A);x=q.dot(D);y=q.dot(T)
  if -.05<t<.24 and x*x+y*y<.13**2:points.append((t,x,y))
 stations=[0,.02,.04,.06,.095,.135,.18];sections=[]
 for t in stations:
  pts=[(x,y) for u,x,y in points if abs(u-t)<.016];assert pts
  xmin,xmax=min(p[0] for p in pts),max(p[0] for p in pts);ymin,ymax=min(p[1] for p in pts),max(p[1] for p in pts);cx=(xmin+xmax)/2;cy=(ymin+ymax)/2;a=(xmax-xmin)/2+.004;b=(ymax-ymin)/2+.004
  factor=max(1,max(math.sqrt(((x-cx)/a)**2+((y-cy)/b)**2) for x,y in pts));a*=factor;b*=factor
  sections.append({'t':t,'center_d':cx,'center_t':cy,'radius_d':a,'radius_t':b,'surface_samples':len(pts),'fit_factor':factor})
 def at(t):
  if t<=stations[0]:return sections[0]
  if t>=stations[-1]:return sections[-1]
  i=next(i for i in range(len(stations)-1) if stations[i]<=t<=stations[i+1]);f=(t-stations[i])/(stations[i+1]-stations[i]);return {k:sections[i][k]*(1-f)+sections[i+1][k]*f for k in ['center_d','center_t','radius_d','radius_t']}
 def surface(t,angle,extra=0):
  p=at(t);c=math.cos(angle);d=math.sin(angle);return W+A*t+D*(p['center_d']+(p['radius_d']+extra)*c)+T*(p['center_t']+(p['radius_t']+extra)*d)
 for name in rec['owned']:
  o=bpy.data.objects[name]
  for v in o.data.vertices:
   q=v.co-W;t=q.dot(A);a=math.atan2(q.dot(T),q.dot(D));extra=0
   if name.endswith('DorsalShell'):extra=.0048
   elif 'ClosureStrap' in name:extra=.011
   p=surface(t,a,extra)
   if name.endswith('DorsalShell') and abs(a)<math.radians(70):p+=D*(.0045*max(0,1-abs(a)/math.radians(70)))
   v.co=p
  o.data.update()
 records.append({'side':side,'sections':sections,'method':'Controlled fitted ellipse for each axial section enclosing actual body/coat/glove surface sample bounds, carrier/lining offset4.8mm and straps11mm; existing cage and anatomical cuff weights retained.'})
s['BW6_correct_context_revision']='one correction: independent axial elliptical carriers replacing irregular radial patches'
out=R/'ada_bw6_bracers_actual_sleeve_correction1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));(R/'records/correction1.json').write_text(json.dumps({'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'candidate':str(out),'sections':records},indent=2))
s.cycles.samples=12;s.render.threads=3
for view in ['three_quarter','profile']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('correction1_actual_context_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('SECTIONAL_CORRECTION1_DONE')

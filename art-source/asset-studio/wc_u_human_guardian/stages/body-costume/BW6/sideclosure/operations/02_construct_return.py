import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];SOURCE=R.parent/'armor/ada_bw6_upper_combined_r001.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];front=bpy.data.objects['BW6_FrontPlate'];back=bpy.data.objects['BW6_BackPlate'];old=bpy.data.objects['BW6_SideEnclosure_1']
protected={o.name:hashlib.sha256(str([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in o.data.vertices]).encode()).hexdigest() for o in [front,back,coat,bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody']]}
ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bvh=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
def coatx(y,z):
 # Torso-interior ray; stops before the neighboring arm and records genuine misses.
 h=bvh.ray_cast(Vector((0,y,z)),Vector((1,0,0)),.235)
 return h[0].x if h[0] is not None and .04<h[0].x<.23 else None
col=bpy.data.collections.new('BW6_RIGHT_SIDE_RETURN_STUDY');s.collection.children.link(col)
owned=[];samples=[]
def point(t,h):
 zb=1.202*(1-t)+1.187*t+.002*math.sin(math.pi*t)
 zt=1.352*(1-t)+1.321*t-.033*math.sin(math.pi*t)
 z=zb+(zt-zb)*h
 yf=.066+(.102-.066)*h;yb=-.098+(-.132+.098)*h;y=yf*(1-t)+yb*t
 xf=.157+(.181-.157)*h;xb=.157+(.181-.157)*h
 boundary=xf*(1-t)+xb*t;cx=coatx(y,z);target=(cx+.010) if cx is not None else boundary
 blend=math.sin(math.pi*t)**.60;x=boundary*(1-blend)+target*blend
 return Vector((x,y,z))
def create(name,vs,fs,mat,wall=.0022):
 me=bpy.data.meshes.new(name+'_EditableSurface');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));score=sum(f.normal.x*f.calc_area() for f in bm.faces)
 if score<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();me.materials.append(mat);o=bpy.data.objects.new(name,me);col.objects.link(o)
 for f in me.polygons:f.use_smooth=True
 m=o.modifiers.new('Fitted side control flow','SUBSURF');m.levels=1;m.render_levels=1
 m=o.modifiers.new('Outside side plate wall','SOLIDIFY');m.thickness=wall;m.offset=1;m.use_even_offset=False
 m=o.modifiers.new('Restrained edge roll','BEVEL');m.width=.0008;m.segments=2;m.limit_method='ANGLE';m.angle_limit=.65
 g=o.vertex_groups.new(name='spine01');g.add(list(range(len(vs))),1,'REPLACE');m=o.modifiers.new('Single rigid torso owner','ARMATURE');m.object=rig;o['owner_bone']='spine01';owned.append(o);return o
ts=[0,.025,.07,.15,.28,.43,.57,.72,.85,.93,.975,1];hs=[0,.035,.24,.53,.82,.965,1];vs=[];fs=[]
for j,h in enumerate(hs):
 for t in ts:
  p=point(t,h);vs.append(tuple(p));samples.append({'t':t,'height_fraction':h,'point_m':list(p),'coat_x_m':coatx(p.y,p.z)})
 if j:
  for i in range(len(ts)-1):a=(j-1)*len(ts)+i;fs.append((a,a+1,a+len(ts)+1,a+len(ts)))
panel=create('BW6_R_FittedSideReturn',vs,fs,old.data.materials[0]);panel['construction']='Purpose-built curved return, front/back flanges tucked inward12mm, independently fitted torso-side interior rays, ordered dipped armhole boundary. Main plates unchanged.'
for k,level in enumerate([.25,.72]):
 vv=[];ff=[];columns=[.035,.055,.12,.22,.34,.46,.57,.59]
 for j,dh in enumerate([-.050,-.042,.042,.050]):
  for t in columns:
   p=point(t,level+dh);p.x+=.0045;vv.append(tuple(p))
  if j:
   for i in range(len(columns)-1):a=(j-1)*len(columns)+i;ff.append((a,a+1,a+len(columns)+1,a+len(columns)))
 oldstrap=bpy.data.objects['BW6_Side_LeatherClosure_1_'+str(k)];create('BW6_R_FittedSideStrap_'+str(k+1),vv,ff,oldstrap.data.materials[0],.0014)
hidden=[]
for nm in ['BW6_SideEnclosure_1','BW6_Side_LeatherClosure_1_0','BW6_Side_LeatherClosure_1_1']:
 o=bpy.data.objects[nm];o.hide_render=True;o.hide_set(True);hidden.append(nm)
s['BW6_side_return_owned']=json.dumps([o.name for o in owned]);s['BW6_side_return_replaced_context']=json.dumps(hidden)
out=R/'ada_bw6_side_return_initial.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
assert protected=={n:hashlib.sha256(str([(tuple(v.co),[(g.group,g.weight) for g in v.groups]) for v in bpy.data.objects[n].data.vertices]).encode()).hexdigest() for n in protected}
(R/'records/initial_construction.json').write_text(json.dumps({'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'protected_geometry_weight_hashes':protected,'candidate':str(out),'owned':[o.name for o in owned],'hidden_old_context':hidden,'samples':samples,'method':panel['construction']},indent=2))
s.cycles.samples=12;s.render.threads=3
for view in ['three_quarter','profile','front']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('initial_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('SIDE_RETURN_INITIAL_DONE')

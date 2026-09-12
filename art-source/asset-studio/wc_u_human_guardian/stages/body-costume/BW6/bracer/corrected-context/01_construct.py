import bpy,bmesh,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent;B=R.parent;SOURCE=B.parent/'armor/ada_bw6_upper_integrated_r002.blend'
for d in ['records','captures']: (R/d).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];body=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];glove=bpy.data.objects['BW4_CONTEXT_BW1_Glove_Pair_SourceFit']
def worldgeom(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[tuple(e.matrix_world@v.co) for v in m.vertices];e.to_mesh_clear();return v
context_before={o.name:{'matrix':[list(r) for r in o.matrix_world],'world_sha256':hashlib.sha256(str(worldgeom(o)).encode()).hexdigest(),'count':len(worldgeom(o)),'parent':o.parent.name if o.parent else None} for o in [body,coat,glove]}
col=bpy.data.collections.new('BW6_CORRECT_CONTEXT_BRACER');s.collection.children.link(col)
owned=[]
p=B/'operations/02_construct.py';tree=ast.parse(p.read_text());functions=['bvh','radial','create','grid_surface']
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in functions],type_ignores=[]),str(p),'exec'),globals())
leather=bpy.data.objects['BW6_R_Bracer_LeatherCuffAndLining'].data.materials[0];steel=bpy.data.objects['BW6_R_Bracer_DorsalShell'].data.materials[0]
records=[]
for side in ['R','L']:
 W=rig.matrix_world@rig.data.bones['wrist.'+side].head_local;E=rig.matrix_world@rig.data.bones['lowerarm01.'+side].head_local;A=(E-W).normalized()
 D=Vector((.7502737045*(1 if side=='R' else -1),.0453408845,.6595708132));D=(D-A*D.dot(A)).normalized();T=A.cross(D).normalized()
 bvs={'body':bvh(body),'padded_sleeve':bvh(coat),'unchanged_glove':bvh(glove)}
 def underlying(t,a):return max(radial(t,a).values(),default=.027)
 def field(t,a):return max(underlying(t+dt,a+da) for dt in [-.004,0,.004] for da in [-.08,0,.08])+.006+.0025*max(0,math.cos(a))**6
 sideowned=[];start=len(owned)
 angles=[-118,-116,-101,-83,-61,-37,-15,-4,0,4,15,37,61,83,101,116,118]
 shell=grid_surface('BW6_Fit_'+side+'_Bracer_DorsalShell',[.026,.028,.054,.095,.139,.174,.177],angles,field,steel,.0024,.0008,1)
 for v in shell.data.vertices:
  q=v.co-W;t=q.dot(A);rad=q-A*t;a=math.atan2(rad.dot(T),rad.dot(D))
  if abs(a)<math.radians(70):v.co+=D*(.0045*max(0,1-abs(a)/math.radians(70)))
 crease=shell.data.attributes.new('crease_edge','FLOAT','EDGE')
 for e in shell.data.edges:
  if all(i%17==8 for i in e.vertices):crease.data[e.index].value=.62
 def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
 def lining_radius(t,a):return field(t,a)-(.0015+.002*smooth((t-.008)/.018))
 lining=grid_surface('BW6_Fit_'+side+'_Bracer_LeatherCuffAndLining',[.001,.003,.008,.014,.021,.026,.035,.06,.095,.135,.173,.177],list(range(-180,181,12)),lining_radius,leather,.0012,.0004,1)
 bm=bmesh.new();bm.from_mesh(lining.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(lining.data);bm.free()
 for k,t in enumerate([.06,.145]):grid_surface('BW6_Fit_'+side+'_Bracer_ClosureStrap_'+str(k+1),[t-.007,t-.006,t+.006,t+.007],list(range(94,267,8)),lambda u,a:field(u,a)+.0042,leather,.0017,.00045,1)
 for o in owned[start:]:
  for group in o.vertex_groups:group.name=group.name.replace('.R','.'+side)
  o['owner_bone']='lowerarm02.'+side;o['setup']='Fitted in root r002 source scene using its existing evaluated coat, no copied context transform'
 # The cuffs receive local anatomical weights below43mm, using unchanged actual source body/glove.
 sources=[]
 for src in [body,glove]:
  ev=src.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles];weights=[{src.vertex_groups[g.group].name:g.weight for g in v.groups if src.vertex_groups[g.group].name in rig.data.bones} for v in me.vertices];sources.append({'name':src.name,'vs':vs,'tri':tri,'weights':weights,'bvh':BVHTree.FromPolygons(vs,tri,all_triangles=True)});ev.to_mesh_clear()
 p=B/'operations/08_cuff_weight_transition.py';tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bary'],type_ignores=[]),str(p),'exec'),globals())
 maps=[]
 for v in lining.data.vertices:
  q=v.co-W;t=q.dot(A)
  if t>.043:continue
  d=(q-A*t).normalized();axis=W+A*t;hits=[]
  for ss in sources:
   hit=ss['bvh'].ray_cast(axis+d*.14,-d,.16)
   if hit[0] is not None and (hit[0]-axis).dot(d)>.002:hits.append(((hit[0]-axis).dot(d),ss,hit))
  if not hits:continue
  _,ss,hit=max(hits,key=lambda x:x[0]);ids=ss['tri'][hit[2]];bc=bary(hit[0],*[ss['vs'][i] for i in ids]);new={}
  for vi,f in zip(ids,bc):
   for g,w in ss['weights'][vi].items():new[g]=new.get(g,0)+w*f
  total=sum(new.values());new={g:w/total for g,w in new.items()} if total else {'lowerarm02.'+side:1};blend=smooth((.043-t)/.012);new={g:w*blend for g,w in new.items()};new['lowerarm02.'+side]=new.get('lowerarm02.'+side,0)+1-blend
  for g in lining.vertex_groups:g.remove([v.index])
  for g,w in new.items():group=lining.vertex_groups.get(g) or lining.vertex_groups.new(name=g);group.add([v.index],w,'REPLACE')
  maps.append({'vertex':v.index,'source':ss['name'],'triangle':ids,'barycentric':bc,'weights':new})
 records.append({'side':side,'frame':{'wrist':list(W),'proximal':list(A),'dorsal':list(D),'transverse':list(T)},'sections':[{'t_m':t,'rays':[{'angle':a,'layers':radial(t,math.radians(a))} for a in range(-180,180,15)]} for t in [.012,.025,.04,.06,.09,.12,.15,.18]],'cuff_maps':maps,'owned':[o.name for o in owned[start:]]})
for o in s.objects:
 if o.type=='MESH' and o.name.startswith(('BW6_R_Bracer_','BW6_L_Bracer_')):o.hide_render=True;o.hide_set(True)
bpy.context.view_layer.update()
context_after={o.name:hashlib.sha256(str(worldgeom(o)).encode()).hexdigest() for o in [body,coat,glove]};assert all(context_before[n]['world_sha256']==h for n,h in context_after.items())
s['BW6_correct_context_bracer_owned']=json.dumps([o.name for o in owned]);s['BW6_correct_context_bracer_record']=json.dumps(records)
out=R/'ada_bw6_bracers_actual_sleeve_initial.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/initial_fit.json').write_text(json.dumps({'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'candidate':str(out),'context_verified_unchanged':context_before,'sides':records},indent=2))
s.cycles.samples=12;s.render.threads=3
for view in ['three_quarter','profile']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('initial_actual_context_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('CORRECT_CONTEXT_INITIAL_DONE')

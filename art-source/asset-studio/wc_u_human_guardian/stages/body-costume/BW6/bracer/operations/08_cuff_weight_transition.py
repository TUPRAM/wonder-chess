import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];source=R/'ada_bw6_bracer_correction1.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW6_Bracer_Independent_Rig'];lining=bpy.data.objects['BW6_R_Bracer_LeatherCuffAndLining'];F=json.loads(s['BW6_bracer_frame']);W=Vector(F['wrist']);A=Vector(F['proximal']);D=Vector(F['dorsal']);T=Vector(F['transverse'])
sources=[]
for nm in ['BW6_Bracer_CONTEXT_IndexedBody','BW6_Bracer_CONTEXT_Glove_Pair_SourceFit']:
 o=bpy.data.objects[nm];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
 vs=[ev.matrix_world@v.co for v in me.vertices];tri=[tuple(t.vertices) for t in me.loop_triangles]
 weights=[{o.vertex_groups[g.group].name:g.weight for g in v.groups if o.vertex_groups[g.group].name in rig.data.bones} for v in me.vertices]
 sources.append({'name':nm,'vs':vs,'tri':tri,'weights':weights,'bvh':BVHTree.FromPolygons(vs,tri,all_triangles=True)});ev.to_mesh_clear()
def bary(p,a,b,c):
 v0=b-a;v1=c-a;v2=p-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-15:return [1,0,0]
 v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;vals=[max(0,1-v-w),max(0,v),max(0,w)];return [x/sum(vals) for x in vals]
changes=[]
for v in lining.data.vertices:
 q=v.co-W;t=q.dot(A)
 if t>.043:continue
 d=(q-A*t).normalized();axis=W+A*t;hits=[]
 for source0 in sources:
  hit=source0['bvh'].ray_cast(axis+d*.14,-d,.16)
  if hit[0] is not None and (hit[0]-axis).dot(d)>.002:hits.append((float((hit[0]-axis).dot(d)),source0,hit))
 if not hits:continue
 _,src,hit=max(hits,key=lambda x:x[0]);ids=src['tri'][hit[2]];bc=bary(hit[0],*[src['vs'][i] for i in ids]);new={}
 for vi,factor in zip(ids,bc):
  for g,w in src['weights'][vi].items():new[g]=new.get(g,0)+w*factor
 total=sum(new.values());new={g:w/total for g,w in new.items()} if total else {'lowerarm02.R':1}
 old={lining.vertex_groups[g.group].name:g.weight for g in v.groups}
 # Source corresponds locally by radial section; transition smoothly back to the rigid forearm liner.
 blend=max(0,min(1,(.043-t)/.012));blend=blend*blend*(3-2*blend)
 new={g:new.get(g,0)*blend for g in new};new['lowerarm02.R']=new.get('lowerarm02.R',0)+1-blend
 for g in lining.vertex_groups:g.remove([v.index])
 for g,w in new.items():
  group=lining.vertex_groups.get(g) or lining.vertex_groups.new(name=g);group.add([v.index],w,'REPLACE')
 changes.append({'vertex':v.index,'axial_t_m':t,'source_object':src['name'],'evaluated_rest_triangle':list(ids),'barycentric':bc,'before':old,'after':new})
lining['owner_bone']='Localized source-corresponding wrist/forearm weights; rigid lowerarm02.R above43mm proximal'
lining['correction2']='Replaced arbitrary wrist-weight ramp with evaluated-rest radial anatomical correspondence to unchanged glove/body. Geometry and source meshes unchanged.'
s['revision']='initial plus two substantive corrections; second is local cuff deformation ownership'
out=R/'ada_bw6_bracer_correction2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'records/correction2_weight_correspondence.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate':str(out),'space':'Source-bound frame1 evaluated rest world surfaces, only local group weights transferred; no world vertices pasted into armature/key data. Radial section constrained to same wrist region.','changes':changes},indent=2));print('CUFF_WEIGHT_CORRECTION2',len(changes))

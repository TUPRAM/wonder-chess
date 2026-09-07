"""Bounded saved-Ada facial fit and fused hand sculpture; keeps all animation curves."""
import argparse,hashlib,json,math,shutil,sys,runpy
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,use_clip
from author_alpha import Geometry,make_mesh,export_fbx_raw
from normalized_fbx import export_normalized_copy
UID='wc_u_human_guardian';SOURCE=ROOT/f'art-source/heroes/{UID}/{UID}.blend';EXPORT=ROOT/f'exports/heroes/{UID}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def colors(ob):
 d={}
 for p in ob.data.polygons:
  uv=ob.data.uv_layers.active.data[p.loop_start].uv
  for i in p.vertices:d[i]=int(uv.x*4)+4*int(uv.y*4)
 return d
def delete(ob,indices):
 bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(indices)],context='VERTS');bm.to_mesh(ob.data);bm.free()
def join(target,extra):
 bpy.ops.object.select_all(action='DESELECT');target.hide_set(False);extra.hide_set(False);target.select_set(True);extra.select_set(True);bpy.context.view_layer.objects.active=target;bpy.ops.object.join();return bpy.context.object
def cleanup(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));seen=set();remove=[]
 for f in bm.faces:
  key=tuple(sorted(tuple(round(x,5) for x in v.co) for v in f.verts))
  if key in seen or f.calc_area()<1e-8:remove.append(f)
  else:seen.add(key)
 if remove:bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
 bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
def render(out):
 scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
 for label,location,target,size in [('front',(0,5,1.45),(0,0,.97),2.5),('side',(5,0,1.45),(0,0,.97),2.5),('back',(0,-5,1.45),(0,0,.97),2.5),('three-quarter',(3,5,2.7),(0,0,.97),2.5),('face',(0,4,1.75),(0,.02,1.635),.55),('face-three-quarter',(2.5,4,1.83),(0,.02,1.635),.58),('sword-grip',(-2,4,1.4),(-.61,.21,.73),.6),('shield-rear',(2,-4,1.4),(.57,.25,1),.75)]:
  scene.camera.data.ortho_scale=size;scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
def candidate(report):
 report.mkdir(parents=True,exist_ok=False);m=json.loads((EXPORT/'export_manifest.json').read_text());assert m['source_revision']==8 and sha(SOURCE)==m['source_sha256'];shutil.copy2(SOURCE,report/'before.blend');shutil.copy2(EXPORT/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-polish.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(SOURCE));arm=bpy.data.objects['Armature'];saved=invariants(arm);use_clip(arm,'Idle');mesh=bpy.data.objects['SK_'+UID];body=bpy.data.objects['BODY_SK_'+UID];u=next(x for x in json.loads((ROOT/'data/units.json').read_text())['units'] if x['id']==UID);h=u['height_m'];mat=mesh.data.materials[0]
 head=next(c for c in components(mesh) if c['groups']==['head'] and c['count']==112 and c['center_m'][2]>1.6);headset=set(head['indices']);verts=[v.co.copy() for v in mesh.data.vertices];faces=[list(p.vertices) for p in mesh.data.polygons if set(p.vertices)<=headset];bvh=BVHTree.FromPolygons(verts,faces)
 def surface(x,z):
  hit=bvh.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0]
  assert hit is not None,(x,z)
  return hit.y
 g=Geometry()
 def add(v,f,col,bone='head'):g.add([tuple(q/h for q in p) for p in v],f,col,bone)
 def disc(cx,cz,rx,rz,col,relief,steps=16):
  v=[(cx,surface(cx,cz)+relief,cz)]
  for ring in range(1,5):
   r=ring/4
   for i in range(steps):
    a=i*2*math.pi/steps;x=cx+rx*r*math.cos(a);z=cz+rz*r*math.sin(a);v.append((x,surface(x,z)+relief*(1-.15*r),z))
  faces=[(0,i+1,(i+1)%steps+1) for i in range(steps)]
  for ring in range(3):
   start=1+ring*steps
   faces.extend((start+i,start+(i+1)%steps,start+steps+(i+1)%steps,start+steps+i) for i in range(steps))
  add(v,faces,col)
 def strip(points,width,col,relief):
  v=[]
  for x,z in points:
   for dz in (-width/2,width/2):v.append((x,surface(x,z+dz)+relief,z+dz))
  add(v,[(i,i+1,i+3,i+2) for i in range(0,len(v)-2,2)],col)
 for s in (-1,1):
  cx=s*.0645;cz=1.6535;disc(cx,cz,.027,.010,8,.002)
  disc(cx,cz,.0082,.0088,9,.0033);disc(cx-.0022,cz+.0028,.0015,.0016,8,.004)
  upper=[(cx+.028*math.cos(a),cz+.0106*math.sin(a)) for a in [i*math.pi/12 for i in range(13)]]
  lower=[(cx+.027*math.cos(a),cz-.010*math.sin(a)) for a in [i*math.pi/12 for i in range(13)]]
  strip(upper,.0028,6,.003);strip(lower,.0018,14,.0018)
  # A broad squared brow remains Ada's identity; fit relief onto the face.
  strip([(cx-.033,1.677),(cx-.016,1.680),(cx+.018,1.680),(cx+.033,1.677)],.0090,7,.0035)
 rows=[(1.672,.010,.001),(1.646,.014,.011),(1.615,.024,.030),(1.599,.020,.007)]
 nv=[]
 for z,w,dep in rows:
  for t in (-1,-.52,0,.52,1):
   x=t*w;nv.append((x,surface(x,z)+dep*(1-abs(t)**1.65)-.0006,z))
 add(nv,[(j*5+i,j*5+i+1,(j+1)*5+i+1,(j+1)*5+i) for j in range(3) for i in range(4)],6)
 lip=[(-.041,1.558),(-.022,1.555),(0,1.554),(.022,1.555),(.041,1.558)]
 strip([(x,z+.0024) for x,z in lip],.0040,6,.0010);strip(lip,.0018,5,.0020);strip([(x,z-.0026) for x,z in lip],.0038,14,.0013)
 # Existing component anatomy and attachment points stay; replace only the visible facial detail islands.
 for ob in (mesh,body):
  col=colors(ob);remove=set()
  for c in components(ob):
   if c['groups']==['head'] and (c['count']==5 or c['count'] in (4,6) and col[c['indices'][0]] in (8,9) or c['count']==15 and col[c['indices'][0]] in (7,14)):remove.update(c['indices'])
  delete(ob,remove)
 face=make_mesh(g,u,arm,mat);face.name='Ada_Fitted_Facial_Details';facecopy=face.copy();facecopy.data=face.data.copy();bpy.data.collections['BODY'].objects.link(facecopy);body=join(body,facecopy);body.hide_render=True;body.hide_set(True);mesh=join(mesh,face)
 # Local hand sculpture fuses the old palm into wrapped fingers; no overlapping loose spheres remain.
 sculpted=[]
 for side,s in [('r',-1),('l',1)]:
  parts=components(mesh);palm=next(c for c in parts if c['groups']==['hand_'+side] and c['count']==70);indices=set(palm['indices']);hand=Geometry();oldverts=[];mapping={}
  for index in palm['indices']:
   v=mesh.data.vertices[index].co.copy();v.x=s*.5824+(v.x-s*.5824)*.90;top=max(0,min(1,(v.z-.804)/.04));v.y=.083+(v.y-.1001)*(.64+.36*top);v.z=.762+(v.z-.76076)*(.77+.23*top);mapping[index]=len(oldverts);oldverts.append(tuple(v/h))
  hand.add(oldverts,[tuple(mapping[i] for i in p.vertices) for p in mesh.data.polygons if set(p.vertices)<=indices],6,'hand_'+side)
  if side=='r':
   for j,z in enumerate((.714,.738,.762,.786)):
    pts=[(-.5824+.047*math.cos(a),.1001+.044*math.sin(a),z) for a in [math.radians(165-i*145/10) for i in range(11)]];hand.tube([tuple(q/h for q in p) for p in pts],[r/h for r in ([.0105,.012,.013,.013,.013,.013,.013,.013,.012,.011,.0095])],6,'hand_r',10)
   pts=[(-.529,.088,.812),(-.538,.134,.808),(-.563,.152,.791)];hand.tube([tuple(q/h for q in p) for p in pts],[.020/h,.018/h,.013/h],6,'hand_r',12)
  else:
   for x in (.548,.571,.594,.617):
    pts=[(x,.140+.044*math.cos(a),.766+.045*math.sin(a)) for a in [math.radians(135+i*235/14) for i in range(15)]];hand.tube([tuple(q/h for q in p) for p in pts],[.012/h]*len(pts),6,'hand_l',10)
   pts=[(.535,.080,.813),(.526,.125,.803),(.548,.169,.785)];hand.tube([tuple(q/h for q in p) for p in pts],[.019/h,.018/h,.013/h],6,'hand_l',12)
  extra=make_mesh(hand,u,arm,mat);extra.name='Ada_Fused_Grip_'+side
  for mod in list(extra.modifiers):extra.modifiers.remove(mod)
  bpy.ops.object.select_all(action='DESELECT');extra.select_set(True);bpy.context.view_layer.objects.active=extra;extra.data.remesh_voxel_size=.0035;extra.data.remesh_voxel_adaptivity=0;result=bpy.ops.object.voxel_remesh();assert 'FINISHED' in result
  smooth=extra.modifiers.new('Sculpt_surface_relax','SMOOTH');smooth.factor=.28;smooth.iterations=2;bpy.ops.object.modifier_apply(modifier=smooth.name);dec=extra.modifiers.new('Sculpt_faceted_finish','DECIMATE');dec.ratio=.46;bpy.ops.object.modifier_apply(modifier=dec.name)
  extra.vertex_groups.clear();group=extra.vertex_groups.new(name='hand_'+side);group.add(list(range(len(extra.data.vertices))),1,'REPLACE')
  for layer in list(extra.data.uv_layers):extra.data.uv_layers.remove(layer)
  uv=extra.data.uv_layers.new(name=mesh.data.uv_layers.active.name)
  for p in extra.data.polygons:
   p.use_smooth=True;p.material_index=0
   for i in p.loop_indices:uv.data[i].uv=(.625,.375)
  for ob in (mesh,body):
   remove={i for c in components(ob) if c['groups']==['hand_'+side] and c['count'] in (70,40) for i in c['indices']};assert len(remove)==110;delete(ob,remove)
  copy=extra.copy();copy.data=extra.data.copy();bpy.data.collections['BODY'].objects.link(copy);body=join(body,copy);body.hide_render=True;body.hide_set(True);mesh=join(mesh,extra);sculpted.append({'side':side,'voxel_size_m':.0035,'surface_relax_iterations':2,'deform_bone':'hand_'+side})
 cleanup(mesh);assert len(mesh.data.uv_layers)==1 and len(mesh.data.materials)==1;assert invariants(arm)==saved;use_clip(arm,'Idle');bpy.ops.wm.save_as_mainfile(filepath=str(report/'ada-source9-candidate.blend'),check_existing=False);render(report);assert sha(SOURCE)==m['source_sha256'];(report/'candidate-result.json').write_text(json.dumps({'status':'ACTUAL_CANDIDATE_RENDERED_NOT_PUBLISHED','source_before_sha256':m['source_sha256'],'candidate_sha256':sha(report/'ada-source9-candidate.blend'),'preserved_invariants':saved,'hand_sculpture':sculpted,'changes':['Face-fitted shallow round irises and eyelids','Fitted squared brows','Low-relief tapered nose integrated at face boundary','Fitted restrained lip contour','Old palms retained as foundation and fused into wrapped fingers with opposing thumbs'],'not_changed':['Existing head shell, ears, short braid','Coat, tabard, armor, shield, sword','All seven animation curves and rest skeleton']},indent=2)+'\n');print('WC_ADA_GALLERY_POLISH_CANDIDATE_RENDERED',flush=True)
def publish(report):
 (report/'executed-publish.py').write_bytes(Path(__file__).read_bytes())
 info=json.loads((report/'candidate-result.json').read_text());m=json.loads((report/'before-export-manifest.json').read_text());assert sha(SOURCE)==info['source_before_sha256'];candidate=report/'ada-source9-candidate.blend';assert sha(candidate)==info['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(candidate));arm=bpy.data.objects['Armature'];assert invariants(arm)==info['preserved_invariants'];mesh=bpy.data.objects['SK_'+UID];assert len(mesh.data.uv_layers)==1 and len(mesh.data.materials)==1;saved_args=sys.argv
 try:
  sys.argv=['inspect_scene.py','--','--collection','EXPORT','--require-skin','--output',str(report/'candidate-structure.json')];runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
  sys.argv=['audit_motion.py','--','--unit',UID,'--output',str(report/'candidate-motion-invariants.json')];runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
 finally:sys.argv=saved_args
 assert not json.loads((report/'candidate-structure.json').read_text())['errors'];assert not json.loads((report/'candidate-motion-invariants.json').read_text())['errors'];arm.data.pose_position='REST';staging=report/'normalized-export';staging.mkdir(exist_ok=False);lods=[]
 for level,ratio in ((1,.5),(2,.25)):
  bpy.data.objects.remove(bpy.data.objects[f'SK_{UID}_LOD{level}'],do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{UID}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);cleanup(lod);export_normalized_copy(staging/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending current Unreal review'});lod.hide_render=True;lod.hide_set(True)
 export_normalized_copy(staging/('SK_'+UID+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE';use_clip(arm,'Idle');scene=bpy.context.scene;scene.camera.data.ortho_scale=2.5;scene.camera.location=(3,5,2.7);scene.camera.rotation_euler=(Vector((0,0,.97))-scene.camera.location).to_track_quat('-Z','Y').to_euler();assert invariants(arm)==info['preserved_invariants'];bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),check_existing=False)
 for path in staging.glob('*.fbx'):shutil.copy2(path,EXPORT/path.name)
 shutil.copy2(EXPORT/'portrait.png',report/'before-portrait.png');shutil.copy2(report/'three-quarter.png',EXPORT/'portrait.png');m.update({'status':'update24_gallery_polish_exported_pending_Unreal_reimport_and_visual_acceptance','source_revision':9,'geometry_source_revision':8,'animation_revision':8,'source_sha256':sha(SOURCE),'triangles':len(mesh.data.loop_triangles),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-polish.py'),'update_export_script_sha256':sha(report/'executed-publish.py'),'update_refinement_evidence':str(report),'files':{p.name:sha(p) for p in EXPORT.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(EXPORT/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'published-result.json').write_text(json.dumps({'status':'SOURCE9_EXPORTED_PENDING_FRESH_VERIFICATION','source_sha256':sha(SOURCE),'manifest_sha256':sha(EXPORT/'export_manifest.json'),'triangles':m['triangles'],'lods':lods,'preserved_invariants':info['preserved_invariants']},indent=2)+'\n');print('WC_ADA_SOURCE9_PUBLISHED_FOR_VERIFICATION',flush=True)
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);publish(a.report.resolve()) if a.publish else candidate(a.report.resolve())

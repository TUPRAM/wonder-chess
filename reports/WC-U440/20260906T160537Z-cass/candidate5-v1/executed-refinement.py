"""Fit only Cass's saved eye/brow details to his actual head shell; preserve all clips."""
import argparse,hashlib,json,math,shutil,sys,runpy
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,use_clip
from author_alpha import Geometry,make_mesh,export_fbx_raw
from normalized_fbx import export_normalized_copy
UID='wc_u_human_warrior';SOURCE=ROOT/f'art-source/heroes/{UID}/{UID}.blend';OUT=ROOT/f'exports/heroes/{UID}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def color_map(ob):
 colors={}
 for p in ob.data.polygons:
  uv=ob.data.uv_layers.active.data[p.loop_start].uv
  for i in p.vertices:colors[i]=int(uv.x*4)+4*int(uv.y*4)
 return colors
def cleanup(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));seen=set();remove=[]
 for f in bm.faces:
  key=tuple(sorted(tuple(round(x,5) for x in v.co) for v in f.verts))
  if key in seen or f.calc_area()<1e-8:remove.append(f)
  else:seen.add(key)
 if remove:bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
 bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
def candidate(report):
 report.mkdir(parents=True,exist_ok=False);m=json.loads((OUT/'export_manifest.json').read_text());assert m['source_revision']==4 and sha(SOURCE)==m['source_sha256'];shutil.copy2(SOURCE,report/'before.blend');shutil.copy2(OUT/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-refinement.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(SOURCE));arm=bpy.data.objects['Armature'];saved=invariants(arm);use_clip(arm,'Idle',unit_id=UID);mesh=bpy.data.objects['SK_'+UID];mat=mesh.data.materials[0];u=next(x for x in json.loads((ROOT/'data/units.json').read_text())['units'] if x['id']==UID);h=u['height_m'];col=color_map(mesh);head=next(c for c in components(mesh) if c['groups']==['head'] and c['count']==140 and col[c['indices'][0]]==6);indices=set(head['indices']);bvh=BVHTree.FromPolygons([v.co.copy() for v in mesh.data.vertices],[list(p.vertices) for p in mesh.data.polygons if set(p.vertices)<=indices])
 def surface(x,z):
  p=bvh.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0];assert p is not None;return p.y
 g=Geometry()
 def add(v,f,c):g.add([tuple(x/h for x in p) for p in v],f,c,'head')
 def disc(cx,cz,rx,rz,col,depth):
  n=24;v=[(cx,surface(cx,cz)+depth,cz)]
  for ring in range(1,5):
   r=ring/4
   for i in range(n):
    a=i*2*math.pi/n;x=cx+rx*r*math.cos(a);z=cz+rz*r*math.sin(a);v.append((x,surface(x,z)+depth*(1-.15*r),z))
  f=[(0,i+1,(i+1)%n+1) for i in range(n)]
  for ring in range(3):
   q=1+ring*n;f.extend((q+i,q+(i+1)%n,q+n+(i+1)%n,q+n+i) for i in range(n))
  add(v,f,col)
 def lid(cx,cz,upper):
  v=[]
  for i in range(17):
   a=i*math.pi/16;x=cx+.033*math.cos(a);z=cz+(.0115 if upper else -.011)*math.sin(a)
   for dz in (-.0012,.0012):v.append((x,surface(x,z+dz)+.0028,z+dz))
  add(v,[(j,j+1,j+3,j+2) for j in range(0,len(v)-2,2)],6)
 for s in (-1,1):
  cx=s*.0663;cz=1.6889;disc(cx,cz,.033,.0115,8,.0022);disc(cx,cz,.010,.0103,9,.0037);disc(cx-.0027,cz+.0035,.0016,.0017,15,.0045);lid(cx,cz,True);lid(cx,cz,False)
 changed=[]
 for ob in (mesh,*list(bpy.data.collections['BODY'].objects)):
  if ob.type!='MESH':continue
  colors=color_map(ob);remove=set()
  for c in components(ob):
   if c['groups']!=['head']:continue
   palette=colors[c['indices'][0]]
   if palette in (8,9,15) and 1.66<c['center_m'][2]<1.71:remove.update(c['indices'])
   if c['count'] in (18,12) and palette in (7,1) and c['center_m'][2]>1.72:
    cy=c['center_m'][1]
    for i in c['indices']:
     v=ob.data.vertices[i];v.co.y=surface(v.co.x,v.co.z)+.003+(v.co.y-cy)*.10
    changed.append({'object':ob.name,'brow_or_streak_vertices_surface_fitted':c['count']})
  if remove:
   bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(remove)],context='VERTS');bm.to_mesh(ob.data);bm.free();changed.append({'object':ob.name,'old_eye_vertices_replaced':len(remove)})
 extra=make_mesh(g,u,arm,mat);extra.name='Cass_Fitted_Eyes';part=extra.copy();part.data=extra.data.copy();bpy.data.collections['BODY'].objects.link(part);part.hide_render=True;part.hide_set(True);bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);extra.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();mesh=bpy.context.object;cleanup(mesh);assert len(mesh.data.uv_layers)==len(mesh.data.materials)==1;assert invariants(arm)==saved;use_clip(arm,'Idle',unit_id=UID);bpy.ops.wm.save_as_mainfile(filepath=str(report/'cass-source5-candidate.blend'),check_existing=False)
 scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768
 for name,loc,target,size in [('face',(0,4,1.85),(0,.02,1.73),.62),('face-three-quarter',(2.5,4,1.95),(0,.02,1.73),.62),('front',(0,4,1.8),(0,0,h*.54),h*1.42),('side',(4,0,1.8),(0,0,h*.54),h*1.42),('back',(0,-4,1.8),(0,0,h*.54),h*1.42),('three-quarter',(3,5,2.7),(0,0,h*.54),h*1.42)]:
  scene.camera.data.ortho_scale=size;scene.camera.location=loc;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(name+'.png'));bpy.ops.render.render(write_still=True)
 assert sha(SOURCE)==m['source_sha256'];(report/'candidate-result.json').write_text(json.dumps({'status':'ACTUAL_CASS_CANDIDATE_RENDERED_NOT_PUBLISHED','source_before_sha256':m['source_sha256'],'candidate_sha256':sha(report/'cass-source5-candidate.blend'),'preserved_invariants':saved,'changes':changed,'preserved':['Head shell, nose, mouth, ears, hair and brow streak shape','All costume and equipment meshes','All seven action curves and rest skeleton']},indent=2)+'\n');print('WC_CASS_FACE_CANDIDATE_RENDERED',flush=True)
def publish(report):
 (report/'executed-publish.py').write_bytes(Path(__file__).read_bytes());info=json.loads((report/'candidate-result.json').read_text());m=json.loads((report/'before-export-manifest.json').read_text());assert sha(SOURCE)==info['source_before_sha256'];candidate=report/'cass-source5-candidate.blend';assert sha(candidate)==info['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(candidate));arm=bpy.data.objects['Armature'];assert invariants(arm)==info['preserved_invariants'];mesh=bpy.data.objects['SK_'+UID];saved=sys.argv
 try:
  sys.argv=['inspect_scene.py','--','--collection','EXPORT','--require-skin','--output',str(report/'candidate-structure.json')];runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
  sys.argv=['audit_motion.py','--','--unit',UID,'--output',str(report/'candidate-motion.json')];runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
 finally:sys.argv=saved
 assert not json.loads((report/'candidate-structure.json').read_text())['errors'];assert not json.loads((report/'candidate-motion.json').read_text())['errors'];arm.data.pose_position='REST';staging=report/'normalized-export';staging.mkdir(exist_ok=False);lods=[]
 for level,ratio in ((1,.5),(2,.25)):
  bpy.data.objects.remove(bpy.data.objects[f'SK_{UID}_LOD{level}'],do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{UID}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);cleanup(lod);export_normalized_copy(staging/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
 export_normalized_copy(staging/('SK_'+UID+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE';use_clip(arm,'Idle',unit_id=UID);scene=bpy.context.scene;scene.camera.data.ortho_scale=m['height_m']*1.42;scene.camera.location=(3,5,2.7);scene.camera.rotation_euler=(Vector((0,0,m['height_m']*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();assert invariants(arm)==info['preserved_invariants'];bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),check_existing=False)
 for p in staging.glob('*.fbx'):shutil.copy2(p,OUT/p.name)
 shutil.copy2(OUT/'portrait.png',report/'before-portrait.png');shutil.copy2(report/'three-quarter.png',OUT/'portrait.png');m.update({'source_revision':5,'geometry_source_revision':5,'source_sha256':sha(SOURCE),'triangles':len(mesh.data.loop_triangles),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-refinement.py'),'update_export_script_sha256':sha(report/'executed-publish.py'),'update_refinement_evidence':str(report),'files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='export_manifest.json'}});(OUT/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'published-result.json').write_text(json.dumps({'status':'CASS_SOURCE5_EXPORTED_PENDING_FRESH_VERIFICATION','source_sha256':sha(SOURCE),'manifest_sha256':sha(OUT/'export_manifest.json'),'triangles':m['triangles'],'lods':lods},indent=2)+'\n');print('WC_CASS_SOURCE5_EXPORTED',flush=True)
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);publish(a.report.resolve()) if a.publish else candidate(a.report.resolve())

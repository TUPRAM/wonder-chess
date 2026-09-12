import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];baseline=R.parent/'armor/ada_bw6_torso_recut_neck.blend';expected='c9db4556de382b5a7670c38f060d1b0648c8aa6e02db0c9c65f5a6c08a33ae04'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(baseline)==expected
def raw(o):return {'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons],'weights':[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],'world':[list(r) for r in o.matrix_world]}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def pose(rig):return {'world':[list(r) for r in rig.matrix_world],'rest':{b.name:[list(r) for r in b.matrix_local] for b in rig.data.bones},'pose':{b.name:[list(r) for r in b.matrix] for b in rig.pose.bones}}
bpy.ops.wm.open_mainfile(filepath=str(baseline),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
protected=['BW6_PaddedCoat_Tailored','BW6_BodyFit_Candidate','BW6_FrontPlate','BW6_NavyWaist','BW6_LeatherBelt','BW6_SideEnclosure_-1','BW6_SideEnclosure_1'];before={n:digest(raw(bpy.data.objects[n])) for n in protected}
camera={o.name:{'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'ortho':o.data.ortho_scale,'lens':o.data.lens} for o in s.objects if o.type=='CAMERA'}
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];poses={}
for fr in [1,20,49,73,97]:s.frame_set(fr);poses[fr]=digest(pose(rig))
originalback=json.loads((R/'records/baseline_sections.json').read_text())['objects']['BW6_BackPlate']['vertices']
result={'baseline':str(baseline),'baseline_sha256':expected,'native_reopen':[],'scope':'Candidate backplate only; no canonical or source changes','rig_pose_frames':[1,20,49,73,97]}
for name in ['ada_bw6_backplate_work.blend','ada_bw6_backplate_checkpoint_REVIEW.blend']:
 p=R/name;beforefile=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);o=bpy.data.objects['BW6_BackPlate_Rebuilt'];rig=bpy.data.objects['BW6_Backplate_Independent_Rig']
 same={n:digest(raw(bpy.data.objects[n]))==h for n,h in before.items()};cams={n:{'matrix':[list(r) for r in bpy.data.objects[n].matrix_world],'type':bpy.data.objects[n].data.type,'ortho':bpy.data.objects[n].data.ortho_scale,'lens':bpy.data.objects[n].data.lens}==v for n,v in camera.items()};poseok={}
 for fr,h in poses.items():s.frame_set(fr);poseok[fr]=digest(pose(rig))==h
 s.frame_set(1);bm=bmesh.new();bm.from_mesh(o.data);top={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_nonboundary':sum(not e.is_manifold and not e.is_boundary for e in bm.edges),'loose_vertices':sum(not v.link_faces for v in bm.verts),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces)};bm.free()
 hemerror=max((o.data.vertices[i].co-Vector(originalback[i])).length for i in range(15));item={'file':str(p),'sha256':beforefile,'mesh_hash':digest(raw(o)),'independent_mesh':o.data.users==1 and o.data.library is None,'independent_rig_data':rig.data.users==1 and rig.data.library is None,'independent_action_data':rig.animation_data.action.users==1 and rig.animation_data.action.library is None,'unchanged_protected_geometry_weights_world':same,'unchanged_cameras':cams,'unchanged_rig_rest_and_sampled_pose':poseok,'topology':top,'exact_original_hem_boundary_max_error_m':hemerror,'center_hem_up_m':o.data.vertices[7].co.z-o.data.vertices[0].co.z,'coat_solidify':[{'thickness':m.thickness,'offset':m.offset,'even':m.use_even_offset} for m in bpy.data.objects['BW6_PaddedCoat_Tailored'].modifiers if m.type=='SOLIDIFY'],'modifiers':[{'type':m.type,'thickness':m.thickness if m.type=='SOLIDIFY' else None,'owner':m.object.name if m.type=='ARMATURE' else None} for m in o.modifiers]}
 assert all(same.values()) and all(cams.values()) and all(poseok.values()) and hemerror<1e-7 and item['independent_mesh'];assert sha(p)==beforefile;result['native_reopen'].append(item)
assert len({x['mesh_hash'] for x in result['native_reopen']})==1;assert sha(baseline)==expected
# Real evaluated posterior sections and body/coat/shell ray distances.
def geometry(ob):
 e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();q=[e.matrix_world@v.co for v in m.vertices];tri=[tuple(t.vertices) for t in m.loop_triangles];e.to_mesh_clear();return q,tri
def cut(q,tri,z):
 lines=[]
 for ids in tri:
  hits=[]
  for a,b in zip(ids,ids[1:]+ids[:1]):
   p,r=q[a],q[b];da=p.z-z;db=r.z-z
   if da*db<0:
    h=p+(r-p)*(da/(da-db))
    if not any((h-x).length<1e-8 for x in hits):hits.append(h)
  if len(hits)==2 and all(p.y<-.03 and abs(p.x)<.21 for p in hits):lines.append(hits)
 return lines
def lines(name,segments,col):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=.00065;c.bevel_resolution=1
 for a,b in segments:sp=c.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
 ob=bpy.data.objects.new(name,c);s.collection.objects.link(ob);ob.color=(*col,1);return ob
layernames=['BW6_BodyFit_Candidate','BW6_PaddedCoat_Tailored','BW6_BackPlate_Rebuilt'];colors=[(.27,.63,.9),(.93,.65,.2),(.82,.86,.9)]
s.frame_set(49);g={n:geometry(bpy.data.objects[n]) for n in layernames};trees={n:BVHTree.FromPolygons(q,tri,all_triangles=True) for n,(q,tri) in g.items()};rays=[]
for z in [1.385,1.405,1.425,1.445,1.465]:
 for x in [-.12,-.09,-.06,0,.06,.09,.12]:
  row={'x_m':x,'z_m':z}
  for n,t in trees.items():
   hit=t.ray_cast(Vector((x,-.65,z)),Vector((0,1,0)),1.0);row[n]=list(hit[0]) if hit[0] is not None else None
   if n=='BW6_BackPlate_Rebuilt' and hit[0] is not None:
    second=t.ray_cast(hit[0]+Vector((0,.00001,0)),Vector((0,1,0)),.025);row['backplate_inner']=list(second[0]) if second[0] is not None else None
  if row.get('backplate_inner') and row['BW6_PaddedCoat_Tailored']:row['inner_to_coat_posterior_y_gap_m']=row['BW6_PaddedCoat_Tailored'][1]-row['backplate_inner'][1]
  rays.append(row)
for ob in s.objects:
 if ob.type=='MESH':ob.hide_render=True
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='OBJECT';s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100
cd=bpy.data.cameras.new('BW6_Backplate_PosteriorSection');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=.45;s.camera=cam;sections=[]
for z in [1.405,1.445,1.465]:
 objs=[];record={'z_m':z,'frame':49,'posterior_only_y_below_m':-.03,'x_bounds_m':[-.21,.21],'layers':{}}
 for n,col in zip(layernames,colors):
  seg=cut(*g[n],z);record['layers'][n]=[[list(a),list(b)] for a,b in seg];objs.append(lines(n+'_ActualSection',seg,col))
 aim=Vector((0,-.12,z));cam.location=aim+Vector((0,0,2));cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();p=R/'captures'/f'actual_posterior_section_z{z:.3f}_f49.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);record.update(path=str(p),sha256=sha(p));sections.append(record)
 for ob in objs:bpy.data.objects.remove(ob,do_unlink=True)
result['posterior_sections']={'source_sha256':result['native_reopen'][-1]['sha256'],'layers':dict(zip(layernames,colors)),'rays':rays,'sections':sections};(R/'records/reopen_preservation_sections.json').write_text(json.dumps(result,indent=2));print('BACKPLATE_REOPEN_PRESERVATION_SECTIONS_OK')

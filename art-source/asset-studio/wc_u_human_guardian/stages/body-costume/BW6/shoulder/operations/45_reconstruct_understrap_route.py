import bpy,sys,json,math,bmesh,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_r003_combined_review.blend');col=bpy.data.collections.new('BW6_SHOULDER_UNDERSTRAPS_SECTIONED');s.collection.children.link(col);bas=json.loads((R/'records/initial_construction.json').read_text());a=Vector(bas['anchor_world_m']);axis=Vector(bas['basis']['axis']);front=Vector(bas['basis']['front']);out=Vector(bas['basis']['out']);parts=[bpy.data.objects['BW6_Pauldron_R_'+n] for n in ['Cap','Lame1','Lame2']];g={o.name:ck.geom(o) for o in parts};mat=bpy.data.materials.new('BW6_Leather_SectionedSupport');mat.diffuse_color=(.19,.105,.052,1);names=[];record=[]
for side,angle in [('Rear',-35),('Front',35)]:
 t=math.radians(angle);rad=front*math.sin(t)+out*math.cos(t);tan=front*math.cos(t)-out*math.sin(t);vs=[];stations=[]
 for u in [.028,.044,.060,.075,.090,.105,.120,.132,.142,.152,.162,.174]:
  origin=a+axis*u;hits=[]
  for n,geom in g.items():
   hit,normal,tri,d=geom[2].ray_cast(origin,rad,.25)
   if hit is not None:hits.append((d,n))
  if not hits:raise RuntimeError('No armor underside at section '+str((side,u)))
  radius,target=min(hits);center=origin+rad*(radius-.003);vs.extend([center-tan*.006,center+tan*.006]);stations.append({'axis_m':u,'radius_m':radius,'limiting_plate':target,'center_m':list(center),'owner':parts[0].name if u<=.044 else parts[1].name})
 me=bpy.data.meshes.new('BW6_Sectioned_'+side+'_Understrap');me.from_pydata(vs,[],[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(stations)-1)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new('BW6_R_Understrap_'+side,me);col.objects.link(o);me.materials.append(mat)
 for target in [parts[0],parts[1]]:
  indices=[v for i,station in enumerate(stations) if station['owner']==target.name for v in [2*i,2*i+1]];h=o.modifiers.new('Bound section stations to '+target.name,'HOOK');h.object=target;h.matrix_inverse=target.matrix_world.inverted();h.vertex_indices_set(indices);h.falloff_type='NONE'
 sub=o.modifiers.new('Flexible section interpolation','SUBSURF');sub.levels=2;sub.render_levels=2;sub.boundary_smooth='PRESERVE_CORNERS';wall=o.modifiers.new('2mm leather','SOLIDIFY');wall.thickness=.002;wall.offset=0;wall.use_even_offset=False;names.append(o.name);record.append({'object':o.name,'width_m':.012,'stations':stations,'method':'Rest sections ray toward armor interior; route3mm inward from innermost actual steel face. Independent Hook stations, no per-frame projection or metal deformation.'})
s['BW6_SHOULDER_SUPPORT_STUDY']=json.dumps(names);source=R/'ada_bw6_shoulder_understrap_sectioned.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source));(R/'records/understrap_sectioned_construction.json').write_text(json.dumps(record,indent=2))
for f in [1,49,73,'lowered']:
 sc=ck.load(source);ck.render(sc,'understrap_sectioned_shoulder_'+str(f),pose=f)

import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
source=R/'ada_bw6_shoulder_shared_support_recut.blend';s=ck.load(source);cap=bpy.data.objects['BW6_Pauldron_R_Cap'];l1=bpy.data.objects['BW6_Pauldron_R_Lame1'];l2=bpy.data.objects['BW6_Pauldron_R_Lame2'];rest={o.name:cap.matrix_world.inverted()@o.matrix_world for o in [l1,l2]};records=[]
for fr in list(range(1,98))+['lowered']:
 if fr=='lowered':ck.lowered(s)
 else:s.frame_set(fr);bpy.context.view_layer.update()
 record={'frame':fr,'parts':{},'cap_inner_eave_to_first_lame_mm':[]}
 for o in [l1,l2]:
  q=cap.matrix_world.inverted()@o.matrix_world;indices=[0,6,12];travel=[((q@o.data.vertices[i].co)-(rest[o.name]@o.data.vertices[i].co)).length*1000 for i in indices];singular=np.linalg.svd(np.array(o.matrix_world.to_3x3()),compute_uv=False).tolist();record['parts'][o.name]={'attachment_control_vertices':indices,'relative_slot_travel_from_rest_mm':travel,'world_transform_singular_values':singular,'relative_matrix':list(map(list,q))}
 geom=ck.geom(l1)
 for j in range(13):
  v=cap.data.vertices[78+j];pt=cap.matrix_world@v.co-(cap.matrix_world.to_3x3()@v.normal).normalized()*.003;hit,n,t,d=geom[2].find_nearest(pt);record['cap_inner_eave_to_first_lame_mm'].append(d*1000)
 records.append(record)
maxtravel={o.name:max(max(r['parts'][o.name]['relative_slot_travel_from_rest_mm']) for r in records) for o in [l1,l2]};maxscale=max(abs(v-1) for r in records for p in r['parts'].values() for v in p['world_transform_singular_values']);summary={'maximum_sampled_attachment_travel_mm':maxtravel,'maximum_transform_scale_deviation':maxscale,'sampled_gap_range_mm':[min(min(r['cap_inner_eave_to_first_lame_mm']) for r in records),max(max(r['cap_inner_eave_to_first_lame_mm']) for r in records)]};print(summary);(R/'records/shared_support_attachment_metrics.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'definition':'Three preselected proximal cage points relative to cap rest frame. Travel is a proposed strap/slot allowance, not a physically modeled strap validation. Eave nearest distances do not prove edge coverage.','summary':summary,'frames':records},indent=2))
s=ck.load(source);r=ck.audit(s,[i+.5 for i in range(54,89)]);(R/'records/shared_support_critical_halves.json').write_text(json.dumps({'source':str(source),'frames':r},indent=2))

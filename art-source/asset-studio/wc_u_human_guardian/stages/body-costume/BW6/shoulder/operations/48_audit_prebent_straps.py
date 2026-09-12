import bpy,sys,json,itertools,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
source=R/'ada_bw6_shoulder_understrap_prebent.blend';s=ck.load(source);names=json.loads(s['BW6_SHOULDER_SUPPORT_STUDY']);metal=json.loads(s['BW6_SHOULDER_ACTIVE']);coat='BW6_PaddedCoat_Tailored';body='BW6_BodyFit_Candidate';records=[]
for fr in list(range(1,98))+[i+.5 for i in range(68,89)]+['lowered']:
 if fr=='lowered':ck.lowered(s)
 else:s.frame_set(int(fr),subframe=fr-int(fr));bpy.context.view_layer.update()
 others={n:ck.geom(bpy.data.objects[n]) for n in metal+[coat,body]};gs={n:ck.geom(bpy.data.objects[n]) for n in names};r={'frame':fr,'straps':{}}
 for n in names:
  o=bpy.data.objects[n];mods=[m for m in o.modifiers if m.type!='HOOK'];saved=[m.show_viewport for m in mods]
  for m in mods:m.show_viewport=False
  bpy.context.view_layer.update();raw=ck.geom(o);centers=[(raw[0][2*i]+raw[0][2*i+1])*.5 for i in range(len(raw[0])//2)];length=sum(float(np.linalg.norm(centers[i+1]-centers[i])) for i in range(len(centers)-1))
  for m,show in zip(mods,saved):m.show_viewport=show
  bpy.context.view_layer.update();r['straps'][n]={'length_m':length,'posed_cage_self':ck.self_audit(raw[0],list(enumerate(raw[1]))),'evaluated_self':ck.self_audit(gs[n][0],list(enumerate(gs[n][1]))),'crossings':{target:ck.cross(gs[n],g) for target,g in others.items()}}
 records.append(r);print('STRAP',fr,{n:{t:x['count'] for t,x in a['crossings'].items()} for n,a in r['straps'].items()},flush=True)
(R/'records/understrap_prebent_audit.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'119 sampled poses. All crossings reported; no terminal overlap automatically excluded. Native hooks then2subdivision and2mmwall. Nonadjacent transverse checks do not classify coplanar/tangent/containment.','frames':records},indent=2))

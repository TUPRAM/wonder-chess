from pathlib import Path
script=Path(__file__).parent/'audit_route_B.py'
exec(compile(script.read_text().split('started = time.perf_counter()')[0],str(script),'exec'),globals())
from mathutils import Vector

def sample(frame,indices):
    scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get();rr=rig.evaluated_get(dg);F=rr.matrix_world@rr.pose.bones['wrist.R'].matrix@relative
    ev=glove.evaluated_get(dg);me=ev.to_mesh();T=F.inverted()@ev.matrix_world;normalT=T.to_3x3().inverted().transposed()
    padnormal=sum([(normalT@me.vertices[i].normal).normalized() for i in rec['patches']['1']['indices']],Vector()).normalized()
    distal=rr.pose.bones['finger1-3.R'];head=F.inverted()@rr.matrix_world@distal.head;tail=F.inverted()@rr.matrix_world@distal.tail;direction=tail-head
    data=[]
    for i in indices:
        v=me.vertices[i];p=T@v.co;n=(normalT@v.normal).normalized()
        weights={glove.vertex_groups[a.group].name:float(a.weight) for a in v.groups if glove.vertex_groups[a.group].name in deform and a.weight>1e-7}
        data.append({'evaluated_vertex':i,'hand_m':list(p),'normal_hand':list(n),'normal_dot_mean_declared_thumb_pad_normal':n.dot(padnormal),'distal_phalanx_longitudinal_fraction':(p-head).dot(direction)/direction.length_squared,'deform_weights':weights})
    ev.to_mesh_clear();return {'frame':frame,'mean_thumb_pad_normal':list(padnormal),'vertices':data,'thumb_euler_degrees':{n:[math.degrees(x) for x in rig.pose.bones[n].rotation_euler] for n in ['finger1-1.R','finger1-2.R','finger1-3.R']}}
ids=[1645,3856,8429,6156]
record={'source_sha256':EXPECTED,'selection':'First-entry triangle vertices1645,3856,8429 and endpoint minimum6156, identified from prior collision query. Fixed IDs inspected atOPEN andfailure. No new contact patch.','samples':[sample(f,ids) for f in [1,20.5,25]]}
record['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert record['source_sha256_after']==EXPECTED
(OUT/'first_surface_ownership.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record),flush=True)

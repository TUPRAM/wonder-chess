import bpy,json,time
import numpy as np
from pathlib import Path
out=Path(__file__).parent;scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene
objects=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith('BW1_Context') and o.name!='BW1_IndexedBody']
report={'source':'ada_body_costume_checkpoint_r002_ART_REVISE.blend','status':'RUNNING','frame_count':169,'objects':[o.name for o in objects],'thresholds':{'world':'abs(X)>1.4m or abs(Y)>1.4m or Z>2.2m or Z<−0.3m, or nonfinite','temporal':'a corresponding evaluated vertex moves >0.12m between adjacent 24fps frames; flags require interpretation'},'extreme_vertex_events':[],'temporal_flags':[],'object_summaries':{}}
last={};maxsteps={o.name:0 for o in objects}
for frame in range(1,170):
    scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        ev=obj.evaluated_get(dg);mesh=ev.to_mesh();coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape((-1,3));mat=np.array(obj.matrix_world,dtype=float);world=coords@mat[:3,:3].T+mat[:3,3]
        finite=np.isfinite(world).all(axis=1);bad=(np.abs(world[:,0])>1.4)|(np.abs(world[:,1])>1.4)|(world[:,2]>2.2)|(world[:,2]<-.3)|(~finite);inds=np.flatnonzero(bad)
        if len(inds):report['extreme_vertex_events'].append({'frame':frame,'object':obj.name,'count':len(inds),'indices':inds[:6].tolist(),'positions':world[inds[:6]].tolist()})
        if obj.name in last and len(last[obj.name])==len(world):
            delta=np.linalg.norm(world-last[obj.name],axis=1);index=int(np.argmax(delta));peak=float(delta[index]);maxsteps[obj.name]=max(maxsteps[obj.name],peak)
            if peak>.12:report['temporal_flags'].append({'frame':frame,'object':obj.name,'max_step_m':peak,'index':index,'current_world':world[index].tolist(),'previous_world':last[obj.name][index].tolist()})
        last[obj.name]=world.copy();ev.to_mesh_clear()
    if frame%24==0:print('AUDIT_FRAME',frame,flush=True)
for obj in objects:
    report['object_summaries'][obj.name]={'max_adjacent_frame_vertex_step_m':maxsteps[obj.name],'solidify':[{'name':m.name,'thickness':m.thickness,'use_even_offset':m.use_even_offset,'clamp':m.thickness_clamp} for m in obj.modifiers if m.type=='SOLIDIFY']}
report['status']='COMPLETE';report['limits']='Finite/bounds and temporal screening only; not cloth/body intersection clearance or artistic acceptance. No scene or file mutation saved.'
(out/'clothing_temporal_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({'extreme_events':len(report['extreme_vertex_events']),'temporal_flags':report['temporal_flags']}),flush=True)

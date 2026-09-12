import bpy,json,time
import numpy as np
from pathlib import Path
out=Path(__file__).parent;scene=bpy.data.scenes['BW1_BODY_COSTUME'];bpy.context.window.scene=scene
obj=bpy.data.objects['BW1_Leggings'];arm=next(m for m in obj.modifiers if m.type=='ARMATURE');sub=next(m for m in obj.modifiers if m.type=='SUBSURF');solid=next(m for m in obj.modifiers if m.type=='SOLIDIFY')
def values():
    return {name:getattr(solid,name) for name in ('thickness','offset','use_even_offset','thickness_clamp','use_thickness_angle_clamp','solidify_mode','nonmanifold_thickness_mode','use_rim')}
original=values();enabled={m.name:m.show_viewport for m in obj.modifiers}
def stats(frame):
    scene.frame_set(frame);bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape((-1,3));mat=np.array(obj.matrix_world,dtype=float);world=coords@mat[:3,:3].T+mat[:3,3]
    finite=np.isfinite(world).all(axis=1);bad=(np.abs(world[:,0])>1.4)|(np.abs(world[:,1])>1.4)|(world[:,2]>2.2)|(world[:,2]<-.3)|(~finite)
    inds=np.flatnonzero(bad);result={'frame':frame,'vertices':len(mesh.vertices),'min_world':world.min(axis=0).tolist(),'max_world':world.max(axis=0).tolist(),'outlier_count':len(inds),'outlier_indices':inds[:8].tolist(),'outlier_samples':world[inds[:8]].tolist()};ev.to_mesh_clear();return result
stages={}
for label,states in [('raw',(False,False,False)),('armature',(True,False,False)),('armature_subdivision',(True,True,False)),('full_original',(True,True,True))]:
    arm.show_viewport,sub.show_viewport,solid.show_viewport=states
    stages[label]=stats(129)
report={'status':'RUNNING','source':'Frozen checkpoint; no .blend save','original_solidify':original,'rna_ranges':{name:{'min':solid.bl_rna.properties[name].hard_min,'max':solid.bl_rna.properties[name].hard_max} for name in ('thickness','offset','thickness_clamp')},'frame129_stages':stages,'sweeps':{}}
print('ISOLATION',json.dumps(report),flush=True)
configs=[('original',original),('even_offset_false',{**original,'use_even_offset':False}),('clamp_half',{**original,'thickness_clamp':.5}),('clamp_half_angle',{**original,'thickness_clamp':.5,'use_thickness_angle_clamp':True})]
for label,config in configs:
    arm.show_viewport=sub.show_viewport=solid.show_viewport=True
    for name,value in config.items():setattr(solid,name,value)
    results=[stats(frame) for frame in range(1,170)]
    failed=[r for r in results if r['outlier_count']]
    report['sweeps'][label]={'settings':config,'frames':169,'outlier_frames':[r['frame'] for r in failed],'max_outlier_count':max(r['outlier_count'] for r in results),'results':results}
    print('SWEEP',label,'outliers',[r['frame'] for r in failed],flush=True)
    (out/'leggings_modifier_isolation.json').write_text(json.dumps(report,indent=2))
report['status']='COMPLETE';report['limits']='Bounds and vertex finiteness only. Does not prove cloth/body clearance or uniform thickness. Geometry changes from the candidate modifiers were not saved.'
(out/'leggings_modifier_isolation.json').write_text(json.dumps(report,indent=2))
print('ISOLATION_DONE',flush=True)

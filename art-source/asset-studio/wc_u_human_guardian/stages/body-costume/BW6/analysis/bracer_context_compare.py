import bpy,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parent.parent
def mesh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=np.array([e.matrix_world@p.co for p in m.vertices]);e.to_mesh_clear();return v
def data(path,scene,coat,rig):
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);s=bpy.data.scenes[scene];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
 names=[coat,'BW6_R_Bracer_DorsalShell'];g={n:mesh(bpy.data.objects[n]) for n in names};r=bpy.data.objects[rig]
 return {'path':str(path),'action':r.animation_data.action.name,'geometry':g,'bones':{p.name:np.array(r.matrix_world@p.matrix) for p in r.pose.bones},'mods':{n:[{'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render,'target':m.object.name if m.type=='ARMATURE' else None} for m in bpy.data.objects[n].modifiers] for n in names},'matrices':{n:[list(v) for v in bpy.data.objects[n].matrix_world] for n in names}}
a=data(R/'bracer/ada_bw6_bracer_checkpoint_r002_REVIEW_CANDIDATE.blend','BW6_RIGHT_BRACER_AUTHORING_ONLY','BW6_Bracer_CONTEXT_CoatUpper_Continuous','BW6_Bracer_Independent_Rig')
b=data(R/'armor/ada_bw6_upper_integrated_r002.blend','BW4_ARMOR_LOCAL_AUTHORING_ONLY','BW4_CONTEXT_BW1_CoatUpper_Continuous','BW4_Armor_Independent_Rig')
current=mesh(bpy.data.objects['BW6_PaddedCoat_Tailored'])
out={};out['sources']=[{k:v for k,v in d.items() if k not in ['geometry','bones']} for d in [a,b]]
out['bone_matrix_differences']={n:float(np.max(np.abs(v-b['bones'][n]))) for n,v in a['bones'].items() if np.max(np.abs(v-b['bones'][n]))>1e-7}
for label,aa,bb in [('source_coat',a['geometry']['BW6_Bracer_CONTEXT_CoatUpper_Continuous'],b['geometry']['BW4_CONTEXT_BW1_CoatUpper_Continuous']),('bracer',a['geometry']['BW6_R_Bracer_DorsalShell'],b['geometry']['BW6_R_Bracer_DorsalShell'])]:
 out[label]={'counts':[len(aa),len(bb)],'max_indexed_delta':float(np.max(np.linalg.norm(aa-bb,axis=1))) if aa.shape==bb.shape else None,'bounds':[[aa.min(0).tolist(),aa.max(0).tolist()],[bb.min(0).tolist(),bb.max(0).tolist()]]}
# Exact source world vertex check plus radial section samples distinguishes
# a context-transform error from a shell wholly contained by the garment.
w=np.array(bpy.data.objects['BW4_Armor_Independent_Rig'].matrix_world@bpy.data.objects['BW4_Armor_Independent_Rig'].data.bones['wrist.R'].head_local);el=np.array(bpy.data.objects['BW4_Armor_Independent_Rig'].matrix_world@bpy.data.objects['BW4_Armor_Independent_Rig'].data.bones['lowerarm01.R'].head_local);axis=(el-w)/np.linalg.norm(el-w)
out['forearm_sections']=[]
for t in [.04,.08,.12,.16]:
 row={'t_m':t}
 for name,v in [('source_coat',a['geometry']['BW6_Bracer_CONTEXT_CoatUpper_Continuous']),('root_original',b['geometry']['BW4_CONTEXT_BW1_CoatUpper_Continuous']),('current_coat',current),('bracer',b['geometry']['BW6_R_Bracer_DorsalShell'])]:
  delta=v-w;ts=delta@axis;rad=np.linalg.norm(delta-ts[:,None]*axis,axis=1);sel=(abs(ts-t)<.01)&(rad<.2);row[name]={'count':int(sel.sum()),'radius_range':([float(rad[sel].min()),float(rad[sel].max())] if sel.any() else None)}
 out['forearm_sections'].append(row)
(R/'analysis/bracer_context_compare.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

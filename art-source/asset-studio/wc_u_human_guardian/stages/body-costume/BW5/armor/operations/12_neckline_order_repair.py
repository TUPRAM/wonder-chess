import bpy,json,ast,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R/'ada_bw5_armor_checkpoint_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(old),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
changes=[]
for name,N,pre in [('BW4_Breastplate_ControlSurface',19,'Front'),('BW4_Backplate_ControlSurface',11,'Back')]:
    ob=bpy.data.objects[name];before=[v.co.copy() for v in ob.data.vertices]
    for row,t in [(7,.4),(8,.8)]:
        for i in range(N):
            idx=row*N+i;ob.data.vertices[idx].co=before[6*N+i].lerp(before[9*N+i],t)
            changes.append({'object':name,'vertex':idx,'before':list(before[idx]),'after':list(ob.data.vertices[idx].co)})
    ob.data.update();ob['BW5_integrity_repair']='Interior neckline rows reconstructed in monotonic order between retained row6 and unchanged opening row9. No outer boundary, hem, width, or primary chest changes.'
    for side,col in [('L',0),('R',N-1)]:
        rim=bpy.data.objects[f'BW4_{pre}_Side_{side}_Return']
        for row in [7,8]:
            delta=ob.data.vertices[row*N+col].co-before[row*N+col]
            for i in [2*row,2*row+1]:rim.data.vertices[i].co+=delta
        rim.data.update()
s['BW5_iteration']='Initial and two torso form corrections retained; final verification repaired reversed interior neckline row order only. Previous failed checkpoint preserved; no new broad form pass.'
s['status']='ART_REVISE';s.camera=bpy.data.objects['BW4_Camera_three_quarter']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_armor_work.blend'))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'),copy=True)
(R/'records/neckline_order_repair.json').write_text(json.dumps({'source':str(old),'sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'reason':'Self query found reversed interior neckline rows; preserve visual outer boundaries and primary plate choices while repairing validity. This does not clear silhouette/fit/attachment/art gates.','changed_control_points':changes},indent=2))
print('NECKLINE_ORDER_REPAIRED',flush=True)

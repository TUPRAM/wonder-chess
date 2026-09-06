"""Read the executed Blender files and verify revision reimport rest poses."""
import bpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids']
records=[];errors=[]
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    return {b.name:{'parent':b.parent.name if b.parent else None,'matrix':list(v for row in b.matrix_local for v in row),
                    'head':list(b.head_local),'tail':list(b.tail_local)} for b in arm.data.bones}
for uid in ids:
    current=root/f'art-source/heroes/{uid}/{uid}.blend';previous=Path(str(current)+'1')
    now=snapshot(current)
    record={'unit_id':uid,'current_source':str(current.relative_to(root)),'bones':now}
    if previous.is_file():
        before=snapshot(previous)
        changes=[]
        if set(now)!=set(before):changes.append('bone_names')
        for name,bone in now.items():
            other=before.get(name)
            if other is None:continue
            if bone['parent']!=other['parent']:changes.append(name+':parent')
            for key in ('matrix','head','tail'):
                if max(abs(a-b) for a,b in zip(bone[key],other[key]))>1e-6:changes.append(name+':'+key)
        record.update({'previous_source':str(previous.relative_to(root)),'rest_pose_changes':changes})
        if changes:errors.append(f'{uid}: rest skeleton changed {changes}')
    else:errors.append(f'{uid}: no preceding saved source available')
    records.append(record)
report={'status':'failed' if errors else 'twelve_current_rest_skeletons_equal_preceding_saved_revision','records':records,'errors':errors,
        'boundary':'source-space matrices/hierarchy only; Unreal reimport verification is separate'}
(root/'reports/WC-330/rest-skeleton-parity.json').write_text(json.dumps(report,indent=2)+'\n')
print('WC_REST_SKELETON_PARITY',report['status'],errors,flush=True)
if errors:raise RuntimeError('Rest-skeleton preservation check failed')

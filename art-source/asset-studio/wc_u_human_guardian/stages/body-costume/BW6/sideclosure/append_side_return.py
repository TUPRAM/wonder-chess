"""Append the three reviewed right-side surfaces to an explicit existing MPFB rig.

Does not save, hide existing parts, replace main plates, or apply a source action.
The caller must review the returned old-part allowlist before hiding that context.
"""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def append_side_return(target_rig,target_scene,collection_name='BW6_SIDE_RETURN_APPEND_CANDIDATE'):
    rec=json.loads((ROOT/'records/verification.json').read_text());source=Path(rec['checkpoint']);names=rec['owned']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=rec['sha256']:raise ValueError('Frozen source changed')
    if target_rig.type!='ARMATURE' or 'spine01' not in target_rig.data.bones:raise ValueError('Expected explicit compatible torso rig')
    if bpy.data.collections.get(collection_name) or any(bpy.data.objects.get(n) for n in names):raise ValueError('Candidate already exists; inspect before retry')
    bpy.context.view_layer.update()
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):
        if not all(n in src.objects for n in names):raise ValueError('Source allowlist mismatch')
        dst.objects=names.copy()
    objects=dst.objects
    for o in objects:
        if o.parent:raise ValueError('Unexpected object parent')
        arms=[m for m in o.modifiers if m.type=='ARMATURE']
        if len(arms)!=1:raise ValueError('Unexpected armature setup')
        original=arms[0].object
        if original.parent or original.constraints:raise ValueError('Unexpected source rig dependencies')
        a=original.matrix_basis@original.data.bones['spine01'].matrix_local;b=target_rig.matrix_world@target_rig.data.bones['spine01'].matrix_local
        if max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))>2e-5:raise ValueError('Torso bind-space mismatch')
        arms[0].object=target_rig;o['BW6_frozen_source_sha256']=rec['sha256']
    c=bpy.data.collections.new(collection_name);target_scene.collection.children.link(c)
    for o in objects:c.objects.link(o);o.hide_render=False;o.hide_set(False)
    return {'objects':[o.name for o in objects],'old_context_to_review':['BW6_SideEnclosure_1','BW6_Side_LeatherClosure_1_0','BW6_Side_LeatherClosure_1_1'],'target_rig':target_rig.name,'source_sha256':rec['sha256'],'action_applied':False}

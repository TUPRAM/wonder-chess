"""Append only the eight owned bracer surfaces to an explicitly supplied MPFB rig.

Run inside Blender. This does not save, replace an existing object, import either
diagnostic action, or establish compatibility with the game's 27-bone skeleton.
"""
from pathlib import Path
import hashlib,json
import bpy

ROOT=Path(__file__).resolve().parent

def append_bracers(target_rig, target_scene, collection_name='BW6_BRACERS_APPEND_CANDIDATE'):
    if target_rig.type!='ARMATURE':raise ValueError('An explicit armature target is required')
    bpy.context.view_layer.update()
    if bpy.data.collections.get(collection_name):raise ValueError('Collection exists; inspect before retrying')
    records=[json.loads((folder/'records/verification.json').read_text()) for folder in (ROOT,ROOT/'left')]
    specs=[]
    for rec in records:
        path=Path(rec['checkpoint'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=rec['sha256']:raise ValueError('Frozen source changed')
        names=[n for n in (rec.get('save_reopen_mesh_signatures') or rec['signatures']) if n.startswith(('BW6_R_Bracer_','BW6_L_Bracer_'))]
        if len(names)!=4:raise ValueError('Unexpected part allowlist')
        if any(bpy.data.objects.get(n) for n in names):raise ValueError('Owned name already exists; inspect rather than duplicate')
        specs.append((path,names,rec['sha256']))
    staged=[]
    try:
        for path,names,sha in specs:
            with bpy.data.libraries.load(str(path),link=False) as (available,loaded):
                if not all(n in available.objects for n in names):raise ValueError('Part missing in source')
                loaded.objects=names
            for o in loaded.objects:
                staged.append(o)
                arms=[m for m in o.modifiers if m.type=='ARMATURE']
                if len(arms)!=1:raise ValueError('Expected one armature modifier')
                src_rig=arms[0].object
                if src_rig.parent or src_rig.constraints:raise ValueError('Unexpected source rig object transform dependencies')
                # The appended dependency is not linked into a view layer, so
                # matrix_world may not have been evaluated. This source is an
                # unparented, unconstrained rig: its stored basis is its world.
                source_world=src_rig.matrix_basis
                for g in o.vertex_groups:
                    if g.name not in target_rig.data.bones:raise ValueError('Target bone absent: '+g.name)
                    expected=source_world@src_rig.data.bones[g.name].matrix_local
                    actual=target_rig.matrix_world@target_rig.data.bones[g.name].matrix_local
                    delta=max(abs(expected[i][j]-actual[i][j]) for i in range(4) for j in range(4))
                    if delta>2e-5:raise ValueError('Bind-space mismatch '+g.name+'; explicit refit required')
                arms[0].object=target_rig
                o['BW6_frozen_source_sha256']=sha
                o['BW6_import_scope']='Geometry only; source diagnostic action not applied; target motion must be checked'
        collection=bpy.data.collections.new(collection_name);target_scene.collection.children.link(collection)
        for o in staged:collection.objects.link(o);o.hide_render=False;o.hide_set(False)
        return {'collection':collection.name,'objects':[o.name for o in staged],'target_rig':target_rig.name,'target_action_unchanged':True,'sources':[{'path':str(p),'sha256':h} for p,_,h in specs]}
    except Exception:
        # These are only newly appended, still-unlinked candidate objects.
        for o in staged:
            if not o.users_collection:bpy.data.objects.remove(o)
        raise

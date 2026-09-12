"""Append the explicit finite authoring proof for isolated integration/review only."""
from pathlib import Path
import bpy,json

def append_bw6_shoulder(scene, rig):
    source=Path(__file__).resolve().parents[1]/'ada_bw6_shoulder_checkpoint_r002_LOCAL_REVIEW.blend'
    parts=['BW6_Pauldron_R_'+n for n in ['Cap','Lame1','Lame2']]
    helpers=[n+'_Suspension' for n in parts]+['BW6_R_Arm_RestDelta','BW6_R_Shoulder_RestDelta','BW6_R_Cap_StrapPivot','BW6_R_Cap_SecondaryHinge']
    names=parts+helpers
    if any(n in bpy.data.objects for n in names):
        raise RuntimeError('Shoulder candidate name collision; explicit removal/selection is required.')
    with bpy.data.libraries.load(str(source),link=False) as (available,requested):
        if not set(names).issubset(available.objects):raise RuntimeError('Incomplete frozen candidate.')
        requested.objects=names
    collection=bpy.data.collections.new('BW6_SHOULDER_LOCAL_PROOF_CONTEXT');scene.collection.children.link(collection)
    for obj in requested.objects:
        collection.objects.link(obj)
        for c in obj.constraints:
            if hasattr(c,'target') and c.target and c.target.type=='ARMATURE':c.target=rig
        if obj.animation_data:
            for fcurve in obj.animation_data.drivers:
                for variable in fcurve.driver.variables:
                    for target in variable.targets:
                        if isinstance(target.id,bpy.types.Object) and target.id.type=='ARMATURE':target.id=rig
    for obj in scene.objects:
        if obj.name.startswith('BW4_Pauldron_R'):obj.hide_render=True;obj.hide_set(True)
    scene['BW6_SHOULDER_ACTIVE']=json.dumps(parts)
    scene['BW6_SHOULDER_HELPERS']=json.dumps(helpers)
    scene['BW6_SHOULDER_STATUS']='LOCAL_AUTHORING_PROOF_REVIEW_NOT_APPROVED'
    scene['BW6_Relief_Representation']='AUTHORED_97_FRAME_ACTION'
    scene['BW6_LOWERED_SUPPORT_POSE']=json.dumps({'secondary_hinge_degrees':[0,-8,0],'strap_allowance_m':0})
    bpy.context.view_layer.update()
    return {'parts':parts,'helpers':helpers,'status':scene['BW6_SHOULDER_STATUS'],'source':str(source)}

def apply_lowered_support_pose():
    """Temporary companion to the exact verified +/-32deg anatomical lowered pose."""
    import math
    helper=bpy.data.objects['BW6_R_Cap_SecondaryHinge']
    previous_action=helper.animation_data.action
    helper.animation_data.action=None
    helper.rotation_euler=(0,math.radians(-8),0)
    helper.location=(0,0,0)
    bpy.context.view_layer.update()
    return previous_action

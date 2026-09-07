"""Fresh actual Blender readback of the sole modified animation FBX."""
import hashlib,json,math
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'sylas-Attack-readback.json'
assert not OUT.exists()
uid='wc_u_elf_rogue';folder=ROOT/f'exports/heroes/{uid}'
m=json.loads((folder/'export_manifest.json').read_text());fbx=folder/f'AN_{uid}_Attack.fbx'
assert hashlib.sha256(fbx.read_bytes()).hexdigest()==m['files'][fbx.name]
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=60;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=True,anim_offset=0)
arms=[o for o in scene.objects if o.type=='ARMATURE'];assert len(arms)==1
arm=arms[0];assert len(arm.data.bones)==m['bones'];assert len(bpy.data.actions)==1
action=bpy.data.actions[0];expected=m['clips']['Attack']['frames'];assert list(action.frame_range)==expected,(list(action.frame_range),expected)
arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];frames=[]
for frame in range(expected[0],expected[1]+1):
    scene.frame_set(frame)
    assert all(math.isfinite(c) for bone in arm.pose.bones for row in bone.matrix for c in row)
    frames.append({'frame':frame,'left_upperarm_rotation_quaternion':list(arm.pose.bones['upperarm_l'].matrix.to_quaternion()),'right_upperarm_rotation_quaternion':list(arm.pose.bones['upperarm_r'].matrix.to_quaternion())})
assert len({tuple(round(x,5) for x in f['left_upperarm_rotation_quaternion']) for f in frames})>5
OUT.write_text(json.dumps({'status':'PASS_ACTUAL_SINGLE_ANIMATION_FBX_IMPORT','unit_id':uid,'source_revision':m['source_revision'],'animation_revision':m['animation_revision'],'fbx_sha256':m['files'][fbx.name],'blender_version':bpy.app.version_string,'fps':scene.render.fps,'frames':expected,'frames_evaluated':len(frames),'bones':len(arm.data.bones),'samples':frames,'limits':['Verifies imported animation range, finite pose and changing off-hand curve; not rendered continuous review','One composite right strike and left recovery guard, not successive alternating attack integration','No Unreal import or combat timing claim']},indent=2)+'\n');print('WC_SYLAS_ATTACK_FBX_READBACK_PASS')

"""Read canonical source animation in memory; never save the source or call the live session."""
import bpy
import json
import math
from pathlib import Path

OUT = Path(r'C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/reviews/current_move_measurements.json')
action = bpy.data.actions.get('AN_wc_u_human_guardian_Move')
assert action is not None
rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
assert len(rigs) == 1, [(r.name, len(r.data.bones)) for r in rigs]
rig = rigs[0]
rig.animation_data_create()
rig.animation_data.action = action
if action.slots:
    rig.animation_data.action_slot = action.slots[0]
for track in rig.animation_data.nla_tracks:
    track.mute = True
scene = bpy.context.scene
start, end = map(float, action.frame_range)
bone_names = [b.name for b in rig.pose.bones]
joint_names = [n for n in bone_names if any(s in n.lower() for s in ('thigh', 'shin', 'calf', 'foot', 'ankle', 'toe', 'upperleg', 'lowerleg', 'pelvis'))]
samples = []
for index in range(round((end-start)*8)+1):
    frame = start + index/8
    scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
    bpy.context.view_layer.update()
    sample = {'frame': frame, 'bones': {}}
    for name in joint_names:
        bone = rig.pose.bones[name]
        sample['bones'][name] = {
            'basis_euler_xyz_degrees': [math.degrees(x) for x in bone.matrix_basis.to_euler('XYZ')],
            'pose_head_armature_space': list(bone.head),
            'pose_tail_armature_space': list(bone.tail),
        }
    samples.append(sample)
summaries = {}
for name in joint_names:
    axes = {}
    for i,axis in enumerate('XYZ'):
        values = [s['bones'][name]['basis_euler_xyz_degrees'][i] for s in samples]
        axes[axis] = {'min_degrees': min(values), 'max_degrees': max(values),
                      'min_frame': samples[values.index(min(values))]['frame'],
                      'max_frame': samples[values.index(max(values))]['frame']}
    summaries[name] = {'rest_head': list(rig.data.bones[name].head_local),
                       'rest_tail': list(rig.data.bones[name].tail_local),
                       'parent': rig.data.bones[name].parent.name if rig.data.bones[name].parent else None,
                       'rotation_mode': rig.pose.bones[name].rotation_mode,
                       'constraints': [{'name':c.name,'type':c.type,'influence':c.influence} for c in rig.pose.bones[name].constraints],
                       'basis_euler_ranges': axes}
out = {
    'status': 'READ_ONLY_SOURCE_MEASUREMENT_NOT_MPFB_RETARGET_OR_RUNTIME_TEST',
    'source_file': bpy.data.filepath, 'blender_version': bpy.app.version_string,
    'source_scene_fps': scene.render.fps, 'source_scene_fps_base': scene.render.fps_base,
    'action': action.name, 'frames': [start,end],
    'clip_duration_seconds': (end-start)*scene.render.fps_base/scene.render.fps,
    'sample_interval_frames': 0.125, 'samples_count': len(samples),
    'rig': rig.name, 'rig_bone_count': len(rig.data.bones), 'all_bones': bone_names,
    'measured_joints': summaries, 'samples': samples,
    'source_saved': False, 'live_session_accessed': False,
}
OUT.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k != 'samples'},indent=2))

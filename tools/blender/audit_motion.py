"""Sample the actual deformed Blender mesh on 50ms intervals; not visual approval."""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy

p=argparse.ArgumentParser();p.add_argument('--unit',required=True);p.add_argument('--output',required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/f'exports/heroes/{args.unit}/export_manifest.json').read_text())
arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+args.unit];sc=bpy.context.scene
groups={v.index:v.name for v in mesh.vertex_groups}
sole_indices=[v.index for v in mesh.data.vertices if v.co.z<.035*manifest['height_m'] and any(groups.get(g.group,'').startswith('foot_') and g.weight>.8 for g in v.groups)]
if not sole_indices:raise RuntimeError('No authored sole vertices bound to foot bones')
records=[];errors=[]
saved_action=arm.animation_data.action;saved_frame=sc.frame_current
for clip,spec in manifest['clips'].items():
    action=bpy.data.actions.get(spec['action'])
    if not action:errors.append(f'{clip}: missing action');continue
    arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    minimum=math.inf;maximum=-math.inf;max_root=0;max_scale_error=0;count=0
    for frame in sorted(set(range(spec['frames'][0],spec['frames'][1]+1,3))|{spec['frames'][1]}):
        sc.frame_set(frame);bpy.context.view_layer.update()
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());deformed=evaluated.to_mesh()
        try:sole_z=min((evaluated.matrix_world@deformed.vertices[i].co).z for i in sole_indices)
        finally:evaluated.to_mesh_clear()
        if not math.isfinite(sole_z):errors.append(f'{clip}: nonfinite deformation at frame {frame}')
        minimum=min(minimum,sole_z);maximum=max(maximum,sole_z);count+=1
        max_root=max(max_root,arm.pose.bones['root'].location.length)
        max_scale_error=max(max_scale_error,max(abs(v-1) for b in arm.pose.bones for v in b.scale))
    record={'clip':clip,'samples':count,'minimum_support_sole_z_m':minimum,'maximum_support_sole_z_m':maximum,
            'max_root_translation_m':max_root,'max_pose_scale_error':max_scale_error}
    if max_root>1e-6 or max_scale_error>1e-6:errors.append(f'{clip}: root translation or scale drift')
    if minimum<-.025:errors.append(f'{clip}: foot penetrates floor by {-minimum:.4f}m')
    if maximum>.045:errors.append(f'{clip}: both feet rise {maximum:.4f}m above floor')
    records.append(record)
arm.animation_data.action=saved_action;arm.animation_data.action_slot=saved_action.slots[0];sc.frame_set(saved_frame)
report={'status':'failed' if errors else 'sampled_motion_invariants_passed','unit_id':args.unit,'blender_version':bpy.app.version_string,
        'sampling':'actual deformed mesh every 3 frames at 60fps','clips':records,'errors':errors,
        'not_checked':['continuous visual quality','weapon/costume clipping','semantic gesture review','Unreal retarget/import','runtime move-speed synchronization']}
Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if errors:raise RuntimeError('Actual motion invariants failed; inspect report')

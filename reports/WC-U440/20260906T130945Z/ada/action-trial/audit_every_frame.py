"""Inspect all authored frames of the three changed actions, independent of renders."""
import hashlib, json, math
from pathlib import Path
import bpy

ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent; UID='wc_u_human_guardian'
source=ROOT/f'art-source/heroes/{UID}/{UID}.blend'
manifest=json.loads((ROOT/f'exports/heroes/{UID}/export_manifest.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source))
arm=bpy.data.objects['Armature']; mesh=bpy.data.objects['SK_'+UID]
groups={v.index:v.name for v in mesh.vertex_groups}
soles=[v.index for v in mesh.data.vertices if v.co.z<.035*manifest['height_m'] and any(groups[g.group].startswith('foot_') and g.weight>.8 for g in v.groups)]
assert soles
records=[]; errors=[]
for clip in ('Attack','Hit','Victory'):
    spec=manifest['clips'][clip]; action=bpy.data.actions[spec['action']]
    arm.animation_data.action=action; arm.animation_data.action_slot=action.slots[0]
    widths=[]; clearances=[]; floors=[]; roots=[]; scales=[]
    for frame in range(spec['frames'][0],spec['frames'][1]+1):
        bpy.context.scene.frame_set(frame); bpy.context.view_layer.update()
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()); deformed=evaluated.to_mesh()
        try:
            coordinates=[evaluated.matrix_world@v.co for v in deformed.vertices]
            assert all(math.isfinite(axis) for vertex in coordinates for axis in vertex)
            widths.append(max(v.x for v in coordinates)-min(v.x for v in coordinates))
            clearances.append(min(coordinates[i].z for i in list(range(1121,1127))+list(range(1194,1200)))-max(coordinates[i].z for i in range(2097,2517)))
            floors.append(min(coordinates[i].z for i in soles))
        finally: evaluated.to_mesh_clear()
        roots.append(arm.pose.bones['root'].location.length)
        scales.append(max(abs(axis-1) for bone in arm.pose.bones for axis in bone.scale))
    record={'clip':clip,'frames_checked':len(widths),'max_width_m':max(widths),
            'minimum_eye_above_shield_m':min(clearances),'minimum_support_sole_z_m':min(floors),
            'maximum_support_sole_z_m':max(floors),'max_root_translation_m':max(roots),
            'max_pose_scale_error':max(scales)}
    records.append(record)
    if max(widths)>2: errors.append(clip+': width exceeds 2m cell')
    if clip in ('Hit','Victory') and min(clearances)<.035: errors.append(clip+': shield eye clearance too small')
    if min(floors)<-.025 or max(floors)>.045: errors.append(clip+': support sole outside floor tolerance')
    if max(roots)>1e-6 or max(scales)>1e-6: errors.append(clip+': root or scale drift')
report={'status':'ALL_AUTHORED_FRAME_METRICS_PASS' if not errors else 'FAIL',
        'source_sha256':manifest['source_sha256'],'blender_version':bpy.app.version_string,
        'sampling':'Every integer frame at authored 60fps, including endpoints',
        'frames_checked':sum(r['frames_checked'] for r in records),'clips':records,'errors':errors,
        'limits':['Not continuous visual acceptance','Does not certify equipment intersections','Unreal animation compression and rendering not checked']}
(OUT/'full-frame-motion-metrics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
if errors: raise RuntimeError('Full-frame motion metrics failed')

"""Read-only BW4 actual hilt geometry and bone-space extraction."""
import bpy
import hashlib
import json
from pathlib import Path
import runpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
audit_path = OUT / 'actual_game_grip_source_audit.json'
scope = ({'report':json.loads(audit_path.read_text()),'before':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()}
         if audit_path.exists() else runpy.run_path(str(OUT / 'inspect_game_grips.py')))
rig = bpy.data.objects['Armature']
obj = bpy.data.objects['EQUIPMENT_SK_wc_u_human_guardian']
body = bpy.data.objects['BODY_SK_wc_u_human_guardian']
mat = lambda m: [list(row) for row in m]
hand_rest_world = rig.matrix_world @ rig.data.bones['hand_r'].matrix_local
inverse = hand_rest_world.inverted()
parts = scope['report']['meshes'][obj.name]['single_hand_weighted_components']
records = []
for part in parts:
    if part['groups'] != ['hand_r']:
        continue
    ids = part['indices']
    indexmap = {old: new for new, old in enumerate(ids)}
    points = [obj.matrix_world @ obj.data.vertices[i].co for i in ids]
    faces = [[indexmap[i] for i in p.vertices] for p in obj.data.polygons if all(i in indexmap for i in p.vertices)]
    lo = [min(v[i] for v in points) for i in range(3)]
    hi = [max(v[i] for v in points) for i in range(3)]
    dims = [b-a for a,b in zip(lo,hi)]
    name = 'handle' if len(ids) == 16 and dims[2] > .19 else 'blade' if len(ids) == 20 else 'guard'
    records.append({'identified_part':name,'original_vertex_ids':ids,'vertex_count':len(ids),
                    'faces':faces,'world_vertices_m':[list(v) for v in points],
                    'hand_bind_vertices_m':[list(inverse@v) for v in points],
                    'bounds_world_min_m':lo,'bounds_world_max_m':hi,'bounds_dimensions_m':dims,
                    'material_indices':[p.material_index for p in obj.data.polygons if all(i in indexmap for i in p.vertices)]})

report = {'status':'READ_ONLY_SOURCE_CONTRACT_NOT_NEW_CANDIDATE_OR_ENGINE_VERIFICATION',
          'source':bpy.data.filepath,'source_sha256':scope['before'],
          'unit_settings':{'system':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length},
          'equipment_object':obj.name,'equipment_world_matrix':mat(obj.matrix_world),
          'rig_world_matrix':mat(rig.matrix_world),'hand_r_rest_world':mat(hand_rest_world),
          'hand_r_head_world':list(rig.matrix_world@rig.data.bones['hand_r'].head_local),
          'hand_r_tail_world':list(rig.matrix_world@rig.data.bones['hand_r'].tail_local),
          'lowerarm_r_rest_world':mat(rig.matrix_world@rig.data.bones['lowerarm_r'].matrix_local),
          'weapon_r_rest_world':mat(rig.matrix_world@rig.data.bones['weapon_r'].matrix_local),
          'sword_components':records,
          'all_equipment_single_hand_components':parts,
          'body_right_hand_islands':[p for p in scope['report']['meshes'][body.name]['single_hand_weighted_components'] if p['groups']==['hand_r']],
          'pommel_observation':'No separate fourth right-hand weighted equipment island; existing right-hand equipment has handle, guard and blade only.',
          'source_saved':False,'live_session_accessed':False}
assert len(records)==3
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==scope['before']
(OUT/'actual_hilt_and_bind.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('BW4_HILT_EXTRACTED',json.dumps({p['identified_part']:{'verts':p['vertex_count'],'dims_mm':[v*1000 for v in p['bounds_dimensions_m']]} for p in records}))

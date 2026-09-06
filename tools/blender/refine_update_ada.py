"""Incremental Ada source refinement; never rebuild the hero or change shared rigs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
UID = 'wc_u_human_guardian'
SOURCE = ROOT / 'art-source/heroes' / UID / (UID + '.blend')
EXPORT = ROOT / 'exports/heroes' / UID


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def invariants(arm):
    actions = {}
    for action in bpy.data.actions:
        actions[action.name] = [
            [curve.data_path, curve.array_index,
             [[list(k.co), list(k.handle_left), list(k.handle_right), k.interpolation]
              for k in curve.keyframe_points]]
            for layer in action.layers for strip in layer.strips
            for bag in strip.channelbags for curve in bag.fcurves]
    return {
        'rest_skeleton_sha256': digest({b.name: {
            'matrix': [list(row) for row in b.matrix_local],
            'parent': b.parent.name if b.parent else None,
        } for b in arm.data.bones}),
        'actions_sha256': digest(actions),
        'action_names': sorted(actions),
        'unit_scale_m': bpy.context.scene.unit_settings.scale_length,
        'fps': bpy.context.scene.render.fps,
    }


def mesh_geometry_digest():
    return digest({ob.name: {
        'vertices': [list(v.co) for v in ob.data.vertices],
        'faces': [list(p.vertices) for p in ob.data.polygons],
        'weights': [[(g.group, g.weight) for g in v.groups] for v in ob.data.vertices],
        'uv': [[list(v.uv) for v in layer.data] for layer in ob.data.uv_layers],
    } for ob in bpy.data.objects if ob.type == 'MESH'})


def action_curve_digest(action):
    return digest([[curve.data_path, curve.array_index,
                    [[list(k.co), list(k.handle_left), list(k.handle_right), k.interpolation]
                     for k in curve.keyframe_points]]
                   for layer in action.layers for strip in layer.strips
                   for bag in strip.channelbags for curve in bag.fcurves])


def components(mesh):
    adjacency = [[] for _ in mesh.data.vertices]
    for edge in mesh.data.edges:
        a, b = edge.vertices
        adjacency[a].append(b)
        adjacency[b].append(a)
    remaining = set(range(len(adjacency)))
    result = []
    while remaining:
        stack = [min(remaining)]
        found = []
        remaining.remove(stack[0])
        while stack:
            current = stack.pop()
            found.append(current)
            for other in adjacency[current]:
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
        vertices = [mesh.data.vertices[i] for i in found]
        lo = [min(v.co[i] for v in vertices) for i in range(3)]
        hi = [max(v.co[i] for v in vertices) for i in range(3)]
        groups = sorted({mesh.vertex_groups[g.group].name for v in vertices for g in v.groups})
        result.append({'first_vertex': min(found), 'count': len(found),
                       'bounds_min_m': lo, 'bounds_max_m': hi,
                       'center_m': [(a+b)/2 for a,b in zip(lo,hi)],
                       'groups': groups, 'indices': sorted(found)})
    return result


def use_clip(arm, clip, frame=1, unit_id=UID):
    action = bpy.data.actions[f'AN_{unit_id}_{clip}']
    arm.animation_data.action = action
    arm.animation_data.action_slot = action.slots[0]
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()


def render_views(out, prefix):
    scene = bpy.context.scene
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.cycles.samples = 16
    camera = scene.camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 2.5
    views = {'front': (0,5,1.45), 'side': (5,0,1.45),
             'back': (0,-5,1.45), 'three-quarter': (3,5,2.7)}
    paths = []
    for name, location in views.items():
        camera.location = location
        camera.rotation_euler = (Vector((0,0,.97))-camera.location).to_track_quat('-Z','Y').to_euler()
        path = out / f'{prefix}-{name}.png'
        if path.exists():
            raise RuntimeError(f'Existing evidence must be preserved: {path}')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(str(path))
    return paths


def refine_equipment(mesh):
    """Reshape existing closed islands, retaining UVs, weights and identity."""
    parts = components(mesh)
    plates = [p for p in parts if p['groups'] == ['hand_l'] and p['count'] == 28
              and p['bounds_max_m'][2]-p['bounds_min_m'][2] > .9]
    grips = [p for p in parts if p['groups'] == ['hand_l'] and p['count'] == 32
             and .2 < p['center_m'][1] < .25]
    handles = [p for p in parts if p['groups'] == ['hand_r'] and p['count'] == 16
               and .19 < p['bounds_max_m'][2]-p['bounds_min_m'][2] < .22]
    blades = [p for p in parts if p['groups'] == ['hand_r'] and p['count'] == 20
              and .5 < p['bounds_max_m'][2]-p['bounds_min_m'][2] < .6]
    if not (len(plates) == 2 and len(grips) == len(handles) == len(blades) == 1):
        raise RuntimeError(f'{mesh.name}: saved equipment islands do not match inspected revision')
    shield_parts = plates + [p for p in parts if p['groups'] == ['hand_l']
                             and p['bounds_min_m'][1] > .39]
    changed = set()
    for part in shield_parts:
        for index in part['indices']:
            vertex = mesh.data.vertices[index]
            # Bow the whole existing shell and mounted crest together. Flatten
            # the disk along depth to read as a shallow sun, not a second gem.
            if part['count'] == 112:
                vertex.co.y = .41314 + (vertex.co.y-.41314)*.45
            if part['count'] == 150:
                vertex.co.y = .4110 + (vertex.co.y-.41678)*.72
            lateral = min(1.0, abs(vertex.co.x-.5824)/.31)
            vertex.co.y += .032*(1-lateral*lateral)
            changed.add(index)
    grip = grips[0]
    indices = grip['indices']
    for ring in range(4):
        verts = [mesh.data.vertices[i] for i in indices[ring*8:(ring+1)*8]]
        center = sum((v.co for v in verts), Vector())/8
        offset = Vector((0,.027 if ring in (0,3) else -.040,0))
        for vertex in verts:
            vertex.co = center + (vertex.co-center)*1.2 + offset
            changed.add(vertex.index)
    handle = handles[0]
    center = Vector(handle['center_m'])
    for index in handle['indices']:
        vertex = mesh.data.vertices[index]
        vertex.co.x = center.x+(vertex.co.x-center.x)*1.18
        vertex.co.y = center.y+(vertex.co.y-center.y)*1.18
        vertex.co.z += .008
        changed.add(index)
    blade = blades[0]
    for index in blade['indices']:
        vertex = mesh.data.vertices[index]
        vertex.co.x = -.5824+(vertex.co.x+.5824)*1.10
        changed.add(index)
    mesh.data.update()
    return {'object':mesh.name, 'changed_vertices':len(changed),
            'topology_unchanged':True, 'shield_shell_bow_m':.032,
            'inner_grip_rearward_m':.040, 'grip_radius_factor':1.2,
            'sword_handle_radius_factor':1.18, 'blade_width_factor':1.1}


def refine_face(mesh):
    parts = [p for p in components(mesh) if p['groups'] == ['head']]
    face = [p for p in parts if p['count']==112 and p['center_m'][2]>1.6]
    nose = [p for p in parts if p['count']==5]
    brows = [p for p in parts if p['count']==15 and p['center_m'][2]>1.65]
    mouths = [p for p in parts if p['count']==15 and p['center_m'][2]<1.6]
    hair = [p for p in parts if p['count']==120]
    if (len(face),len(nose),len(brows),len(mouths),len(hair)) != (1,1,2,1,1):
        raise RuntimeError(f'{mesh.name}: saved facial islands differ from inspected source')
    changed = set()
    for index in face[0]['indices']:
        vertex = mesh.data.vertices[index]
        if vertex.co.z<1.60:
            influence = max(0,min(1,(1.60-vertex.co.z)/.093))
            vertex.co.x *= 1-.12*influence
            changed.add(index)
    for index in nose[0]['indices']:
        vertex = mesh.data.vertices[index]
        vertex.co.x *= .89
        vertex.co.y = .14014+(vertex.co.y-.14014)*.73
        changed.add(index)
    for part in brows:
        center = Vector(part['center_m'])
        for index in part['indices']:
            vertex = mesh.data.vertices[index]
            vertex.co.x = center.x+(vertex.co.x-center.x)*.94
            vertex.co.y = center.y+(vertex.co.y-center.y)*.72
            vertex.co.z = center.z+(vertex.co.z-center.z)*.58-.009
            changed.add(index)
    mouth = mouths[0]
    for index in mouth['indices']:
        vertex = mesh.data.vertices[index]
        vertex.co.x *= .9
        vertex.co.z += .004+.002*min(1,abs(vertex.co.x)/.049)
        changed.add(index)
    for index in hair[0]['indices']:
        vertex = mesh.data.vertices[index]
        if vertex.co.z<1.73 and abs(vertex.co.x)>.095:
            influence = min(1,(abs(vertex.co.x)-.095)/.048)
            vertex.co.z -= .025*influence
            vertex.co.y += .009*influence
            changed.add(index)
    mesh.data.update()
    return {'object':mesh.name, 'changed_facial_vertices':len(changed),
            'topology_unchanged':True, 'nose_depth_factor':.73,
            'brow_thickness_factor':.58, 'jaw_softening_max_factor':.88,
            'existing_braid_and_materials_preserved':True}


def refine(out, before_hash):
    arm = bpy.data.objects['Armature']
    before = invariants(arm)
    candidate = out / 'ada-update24-revision7.blend'
    if candidate.exists():
        raise RuntimeError('Refinement evidence exists; use a fresh run for another revision')
    shutil.copy2(SOURCE, out / 'before-source.blend')
    shutil.copy2(EXPORT / 'export_manifest.json', out / 'before-export-manifest.json')
    changes = []
    for name in ['SK_'+UID, 'EQUIPMENT_SK_'+UID, 'BODY_SK_'+UID]:
        mesh = bpy.data.objects[name]
        weights = [[(g.group,g.weight) for g in v.groups] for v in mesh.data.vertices]
        uv = [[list(v.uv) for v in layer.data] for layer in mesh.data.uv_layers]
        faces = [list(face.vertices) for face in mesh.data.polygons]
        if not name.startswith('BODY_'):
            changes.append(refine_equipment(mesh))
        if not name.startswith('EQUIPMENT_'):
            changes.append(refine_face(mesh))
        assert weights == [[(g.group,g.weight) for g in v.groups] for v in mesh.data.vertices]
        assert uv == [[list(v.uv) for v in layer.data] for layer in mesh.data.uv_layers]
        assert faces == [list(face.vertices) for face in mesh.data.polygons]
    assert invariants(arm) == before
    use_clip(arm,'Idle')
    bpy.ops.wm.save_as_mainfile(filepath=str(candidate),check_existing=False)
    renders = render_views(out,'after')
    assert invariants(arm) == before and sha(SOURCE) == before_hash
    report = {'status':'REFINED_SOURCE_RENDERED_UNREAL_REIMPORT_PENDING',
              'source_before_sha256':before_hash, 'candidate':str(candidate),
              'candidate_sha256':sha(candidate), 'changes':changes,
              'preserved_invariants':before, 'renders':renders,
              'limits':['Existing animations preserved, continuous review still required',
                        'LODs not yet regenerated', 'Unreal import and gameplay review not run']}
    (out/'refinement.json').write_text(json.dumps(report,indent=2)+'\n')
    print('WC_ADA_INCREMENTAL_REFINEMENT_RENDERED '+str(candidate),flush=True)


def motion(out):
    arm = bpy.data.objects['Armature']
    scene = bpy.context.scene
    saved_arguments = sys.argv
    try:
        sys.argv = ['audit_motion.py','--','--unit',UID,'--output',str(out/'motion-invariants.json')]
        runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
        sys.argv = ['inspect_scene.py','--','--collection','EXPORT',
                    '--output',str(out/'structure-inspection.json'),'--require-skin']
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
    finally:
        sys.argv = saved_arguments
    scene.render.resolution_x = scene.render.resolution_y = 384
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.cycles.samples = 4
    scene.camera.data.ortho_scale = 3.15
    scene.camera.location = (3,5,2.7)
    scene.camera.rotation_euler = (Vector((0,0,1.15))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    manifest = json.loads((EXPORT/'export_manifest.json').read_text())
    clips = []
    for name,spec in manifest['clips'].items():
        folder = out/'motion-frames'/name
        if folder.exists():
            raise RuntimeError('Existing motion evidence must be preserved')
        folder.mkdir(parents=True)
        start,end = spec['frames']
        frames = list(range(start,end,3))
        for index,frame in enumerate(frames):
            use_clip(arm,name,frame)
            scene.render.filepath = str(folder/f'{index:04d}.png')
            bpy.ops.render.render(write_still=True)
        clips.append({'clip':name,'source_fps':60,'sample_step_frames':3,
                      'playback_fps':20,'duration_ms':(end-start)*1000//60,
                      'frame_count':len(frames),'source_frames':frames,
                      'frames_directory':str(folder)})
        print('WC_ADA_MOTION_RENDERED '+name,flush=True)
    (out/'motion-sequences.json').write_text(json.dumps({
        'status':'ACTUAL_RENDERED_NORMAL_SPEED_REVIEW_SEQUENCES',
        'render_size':[384,384], 'clips':clips,
        'limits':['20fps visual sampling of preserved 60fps source',
                  'Unreal playback, crowd occlusion and sound alignment not verified',
                  'Sequence rendering does not by itself certify visual acceptance']},indent=2)+'\n')


def export_revision(out, unit_id=UID, refinement_script=None):
    UID = unit_id
    SOURCE = ROOT/'art-source/heroes'/UID/(UID+'.blend')
    EXPORT = ROOT/'exports/heroes'/UID
    refinement_script = Path(refinement_script) if refinement_script else Path(__file__)
    sys.path.insert(0,str(ROOT/'tools/blender'))
    from author_alpha import export_fbx_raw
    from normalized_fbx import export_normalized_copy
    profile_path = ROOT/'tools/blender/profiles/fbx_skeletal_cm_v1.json'
    profile = json.loads(profile_path.read_text())
    if profile['calibration_status'] != 'measured_pass':
        raise RuntimeError('Measured centimeter-copy profile is required')
    refined = json.loads((out/'refinement.json').read_text())
    before = json.loads((out/'before-export-manifest.json').read_text())
    if sha(SOURCE) != refined['source_before_sha256']:
        raise RuntimeError('Production source changed during refinement; do not overwrite it')
    for check in ('motion-invariants.json','structure-inspection.json'):
        result = json.loads((out/check).read_text())
        if result.get('errors'):
            raise RuntimeError(f'Cannot promote source with failed {check}')
    arm = bpy.data.objects['Armature']
    mesh = bpy.data.objects['SK_'+UID]
    invariant = invariants(arm)
    if invariant != refined.get('verified_candidate_invariants', refined['preserved_invariants']):
        raise RuntimeError('Candidate no longer preserves the verified skeleton/actions')
    lod_records = []
    collection = bpy.data.collections.get('LOD_SOURCE')
    if collection is None:
        collection = bpy.data.collections.new('LOD_SOURCE')
        bpy.context.scene.collection.children.link(collection)
    arm.data.pose_position = 'REST'
    for level,ratio in ((1,.5),(2,.25)):
        name = f'SK_{UID}_LOD{level}'
        old = bpy.data.objects.get(name)
        if old:
            old_data = old.data
            bpy.data.objects.remove(old,do_unlink=True)
            if old_data.users==0:
                bpy.data.meshes.remove(old_data)
        lod = mesh.copy()
        lod.data = mesh.data.copy()
        lod.name = name
        collection.objects.link(lod)
        bpy.ops.object.select_all(action='DESELECT')
        lod.hide_set(False)
        lod.select_set(True)
        bpy.context.view_layer.objects.active = lod
        modifier = lod.modifiers.new('WC_SilhouetteReduction','DECIMATE')
        modifier.ratio = ratio
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        lod.data.calc_loop_triangles()
        lod_records.append({'lod':level,'triangles':len(lod.data.loop_triangles),
                            'ratio_target':ratio,'visual_acceptance':'pending current Unreal review'})
        lod.hide_render = True
        lod.hide_set(True)
    arm.data.pose_position = 'POSE'
    use_clip(arm,'Idle',unit_id=UID)
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 121
    revision_source = SOURCE.with_name(UID+'_revision7.blend')
    if revision_source.exists():
        raise RuntimeError('Revision7 source already exists; do not replace history')
    bpy.ops.wm.save_as_mainfile(filepath=str(revision_source),check_existing=False)
    staged = out/'normalized-export'
    staged.mkdir()
    export_normalized_copy(staged/f'SK_{UID}.fbx',[arm,mesh],False,export_fbx_raw)
    for level in (1,2):
        lod = bpy.data.objects[f'SK_{UID}_LOD{level}']
        export_normalized_copy(staged/f'SK_{UID}_LOD{level}.fbx',[arm,lod],False,export_fbx_raw)
    scene = bpy.context.scene
    for clip,spec in before['clips'].items():
        use_clip(arm,clip,unit_id=UID)
        scene.frame_start,scene.frame_end = spec['frames']
        export_normalized_copy(staged/f'AN_{UID}_{clip}.fbx',[arm],True,export_fbx_raw)
    if invariants(arm) != invariant:
        raise RuntimeError('Normalized export changed authoring invariants')
    if len(list(staged.glob('*.fbx'))) != 10:
        raise RuntimeError('Incomplete measured export set')
    shutil.copy2(out/'after-three-quarter.png',staged/'portrait.png')
    mesh.data.calc_loop_triangles()
    manifest = before.copy()
    manifest.update(status='update24_refined_rendered_exported_pending_Unreal_reimport_and_visual_acceptance',
                    source_revision=7, geometry_source_revision=7,
                    source_sha256=sha(revision_source), units_source_sha256=sha(ROOT/'data/units.json'),
                    triangles=len(mesh.data.loop_triangles), lods=lod_records,
                    update_refinement_script_sha256=sha(refinement_script),
                    update_export_script_sha256=sha(Path(__file__)),
                    update_refinement_evidence=out.relative_to(ROOT).as_posix(),
                    fbx_profile=profile_path.relative_to(ROOT).as_posix(),
                    open_reviews=['Current Unreal source revision/reimport',
                                  'Continuous in-engine seven-clip review',
                                  'Crowded-board shield occlusion',
                                  'LOD silhouette review','Skill release/audio alignment',
                                  'Final facial and costume art acceptance'])
    if refined.get('changed_clips'):
        manifest['animation_revision'] = 7
        manifest['animation_update_evidence'] = out.relative_to(ROOT).as_posix()
        for clip in refined['changed_clips']:
            manifest['clips'][clip['clip']]['maximum_support_reach_clamp_m'] = clip['maximum_support_reach_clamp_m']
            manifest['clips'][clip['clip']]['support_hand_bake_samples'] = clip['frames_baked']
    manifest['files'] = {p.name:sha(staged/p.name if (staged/p.name).exists() else p) for p in sorted(EXPORT.iterdir())
                         if p.is_file() and p.name!='export_manifest.json'}
    (staged/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Validate the full staged set and metadata before touching published files.
    for file in staged.iterdir():
        if file.is_file():
            shutil.copy2(file,EXPORT/file.name)
    shutil.copy2(revision_source,SOURCE)
    (out/'export-result.json').write_text(json.dumps({
        'status':'EXPORTED_ENGINE_REIMPORT_PENDING','source':str(SOURCE),
        'source_sha256':sha(SOURCE),'revision_source':str(revision_source),
        'mesh_exports':3,'animation_exports':7,'portrait':str(EXPORT/'portrait.png'),
        'manifest':str(EXPORT/'export_manifest.json'), 'manifest_sha256':sha(EXPORT/'export_manifest.json'),
        'candidate_invariants_preserved':True,
        'animations_modified_by_refinement':[clip['clip'] for clip in refined.get('changed_clips',[])],
        'lods':lod_records,
        'fbx_profile':profile_path.relative_to(ROOT).as_posix()},indent=2)+'\n')
    print('WC_UPDATE24_NORMALIZED_EXPORT_COMPLETE '+UID,flush=True)


def export_action_revision(out):
    """Promote the reviewed three-action trial without touching mesh exports."""
    sys.path.insert(0, str(ROOT/'tools/blender'))
    from author_alpha import export_fbx_raw
    from normalized_fbx import export_normalized_copy
    result = json.loads((out/'result.json').read_text())
    candidate = Path(result['candidate'])
    if sha(SOURCE) != result['published_source_sha256'] or sha(candidate) != result['candidate_sha256']:
        raise RuntimeError('Published source or reviewed trial changed; refuse stale promotion')
    if json.loads((out/'motion-invariants.json').read_text()).get('errors'):
        raise RuntimeError('Motion invariant failure blocks export')
    before = json.loads((EXPORT/'export_manifest.json').read_text())
    if before['source_revision'] != 7 or before['geometry_source_revision'] != 7:
        raise RuntimeError('Expected reviewed geometry revision7')
    profile = ROOT/'tools/blender/profiles/fbx_skeletal_cm_v1.json'
    if json.loads(profile.read_text())['calibration_status'] != 'measured_pass':
        raise RuntimeError('Measured profile required')
    arm = bpy.data.objects['Armature']
    old_rest = invariants(arm)['rest_skeleton_sha256']
    old_geometry = mesh_geometry_digest()
    unchanged = {name: action_curve_digest(bpy.data.actions[f'AN_{UID}_{name}'])
                 for name in result['unchanged_clips']}
    bpy.ops.wm.open_mainfile(filepath=str(candidate))
    arm = bpy.data.objects['Armature']
    if mesh_geometry_digest() != old_geometry or invariants(arm)['rest_skeleton_sha256'] != old_rest:
        raise RuntimeError('Action-only candidate changed geometry or rest skeleton')
    for name, expected in unchanged.items():
        if action_curve_digest(bpy.data.actions[f'AN_{UID}_{name}']) != expected:
            raise RuntimeError(f'Unrequested clip modification: {name}')
    revision_source = SOURCE.with_name(UID+'_revision8.blend')
    stage = out/'normalized-export'
    if revision_source.exists() or stage.exists():
        raise RuntimeError('Revision8 or export evidence exists; preserve it')
    stage.mkdir()
    shutil.copy2(EXPORT/'export_manifest.json', out/'before-export-manifest.json')
    use_clip(arm, 'Idle')
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = before['clips']['Idle']['frames']
    bpy.ops.wm.save_as_mainfile(filepath=str(revision_source), check_existing=False)
    preserved = invariants(arm)
    changed_files = []
    for record in result['changed_clips']:
        name = record['clip']
        if record['frames'] != before['clips'][name]['frames'] or record['release_frame'] != before['clips'][name]['release_frame']:
            raise RuntimeError('Timing changed from canonical clip contract')
        use_clip(arm, name)
        bpy.context.scene.frame_start, bpy.context.scene.frame_end = record['frames']
        target = stage/f'AN_{UID}_{name}.fbx'
        export_normalized_copy(target, [arm], True, export_fbx_raw)
        changed_files.append(target.name)
    if len(changed_files) != 3 or any(not (stage/name).is_file() for name in changed_files):
        raise RuntimeError('Incomplete action export set')
    if invariants(arm) != preserved or mesh_geometry_digest() != old_geometry:
        raise RuntimeError('Export changed source invariants')
    manifest = before.copy()
    manifest.update(source_revision=8, animation_revision=8,
                    source_sha256=sha(revision_source),
                    status='update24_motion_refined_exported_pending_Unreal_reimport_and_visual_acceptance',
                    animation_update_script_sha256=sha(out/'prepare_actions.py'),
                    animation_update_export_script_sha256=sha(Path(__file__)),
                    animation_update_evidence=out.relative_to(ROOT).as_posix())
    for record in result['changed_clips']:
        spec = manifest['clips'][record['clip']]
        spec['support_hand_bake_samples'] = len(range(spec['frames'][0], spec['frames'][1]+1, 3))
        spec['maximum_support_reach_clamp_m'] = record['max_reach_clamp_m']
        spec['sampled_width_m'] = record['max_width_m']
        spec['minimum_eye_above_shield_m'] = record['minimum_eye_above_shield_m']
    manifest['files'] = {name:sha(stage/name if name in changed_files else EXPORT/name)
                         for name in before['files']}
    unchanged_files = [name for name in before['files'] if name not in changed_files]
    if any(manifest['files'][name] != before['files'][name] for name in unchanged_files):
        raise RuntimeError('An unrequested export changed')
    staged_manifest = stage/'export_manifest.json'
    staged_manifest.write_text(json.dumps(manifest, indent=2)+'\n')
    # Validate metadata before publishing the complete set. Retain revision7.
    for name in changed_files:
        shutil.copy2(stage/name, EXPORT/name)
    shutil.copy2(revision_source, SOURCE)
    shutil.copy2(staged_manifest, EXPORT/'export_manifest.json')
    report = {'status':'ACTION_EXPORT_PASS_UNREAL_REIMPORT_PENDING',
              'source':str(SOURCE), 'source_revision':8, 'geometry_revision':7,
              'animation_revision':8, 'source_sha256':sha(SOURCE),
              'manifest_sha256':sha(EXPORT/'export_manifest.json'),
              'changed_exports':changed_files, 'unchanged_exports':unchanged_files,
              'rest_skeleton_sha256':old_rest, 'geometry_sha256':old_geometry,
              'unchanged_action_sha256':unchanged,
              'timings_preserved':True, 'Unreal_import_tested':False}
    (out/'export-result.json').write_text(json.dumps(report, indent=2)+'\n')
    print('WC_ADA_ACTION_REVISION8_EXPORTED '+json.dumps(report), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=['inspect','refine','motion','export','export-actions'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    before_hash = sha(SOURCE)
    scene_source = args.output/'ada-update24-revision7.blend' if args.mode in ('motion','export') else SOURCE
    bpy.ops.wm.open_mainfile(filepath=str(scene_source))
    arm = bpy.data.objects['Armature']
    mesh = bpy.data.objects['SK_' + UID]
    manifest = json.loads((EXPORT / 'export_manifest.json').read_text())
    if before_hash != manifest['source_sha256']:
        raise RuntimeError('Actual source differs from retained export manifest; inspect provenance before editing')
    if args.mode == 'motion':
        motion(args.output)
        return
    if args.mode == 'export':
        export_revision(args.output)
        return
    if args.mode == 'export-actions':
        export_action_revision(args.output)
        return
    if args.mode == 'refine':
        refine(args.output,before_hash)
        return
    report = {
        'status': 'ACTUAL_BLENDER_INSPECTION_NOT_VISUAL_ACCEPTANCE',
        'blender_version': bpy.app.version_string,
        'source': str(SOURCE), 'source_sha256': before_hash,
        'invariants': invariants(arm),
        'objects': [{'name': ob.name, 'type': ob.type, 'hide_render': ob.hide_render}
                    for ob in bpy.data.objects],
        'mesh_components': components(mesh),
        'hand_rest': {name: {'head':list(arm.data.bones[name].head_local),
                             'tail':list(arm.data.bones[name].tail_local)}
                      for name in ('hand_l','hand_r')},
    }
    use_clip(arm, 'Idle')
    report['renders'] = render_views(args.output, 'before')
    assert sha(SOURCE) == before_hash
    (args.output / 'before-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
    print('WC_ADA_SOURCE_INSPECTED ' + str(args.output), flush=True)


if __name__ == '__main__':
    main()

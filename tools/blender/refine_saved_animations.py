"""Revise selected actions in saved sources without regenerating hero geometry."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_alpha import animate
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+',required=True);parser.add_argument('--apply',action='store_true');parser.add_argument('--skip-render',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
units={u['id']:u for u in json.loads((ROOT/'data/units.json').read_text())['units']}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def geometry_signature():
    state={}
    for obj in bpy.data.objects:
        if obj.type=='MESH':
            state[obj.name]={'vertices':[list(v.co) for v in obj.data.vertices],
                             'polygons':[list(p.vertices) for p in obj.data.polygons],
                             'uv':[[list(v.uv) for v in layer.data] for layer in obj.data.uv_layers],
                             'weights':[[(g.group,g.weight) for g in v.groups] for v in obj.data.vertices]}
        elif obj.type=='ARMATURE':
            state[obj.name]={'rest':{b.name:{'matrix':[list(r) for r in b.matrix_local],'parent':b.parent.name if b.parent else None} for b in obj.data.bones}}
    return hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()
for uid in args.ids:
    unit=units[uid];source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';production=ROOT/f'exports/heroes/{uid}'
    original_source_hash=sha(source);manifest=json.loads((production/'export_manifest.json').read_text())
    report=ROOT/f'reports/WC-330/animation-refinement/{uid}';report.mkdir(parents=True,exist_ok=True)
    target=production if args.apply else ROOT/f'exports/calibration/animation-refinement-trial/{uid}'
    target.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source));sc=bpy.context.scene;arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid]
    signature=geometry_signature();unchanged={p.name:sha(p) for p in production.iterdir() if p.is_file()}
    selected=['Hit','Defeat']
    if unit['unit_class'] in ('priest','mage','ranger'):selected+=['Active','Victory']
    before=(report/'manifest-before.json')
    if not before.exists():before.write_text(json.dumps(manifest,indent=2)+'\n')
    clips=animate(unit,arm,target,selected_clips=selected)
    if geometry_signature()!=signature:raise RuntimeError('Geometry, UV, weights or rest skeleton changed')
    # The canonical manifest still supplies unchanged durations/action names to this actual deformation audit.
    saved=sys.argv
    try:
        sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(report/'motion-invariants.json')]
        runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved
    floor_checks=[]
    for clip,spec in clips.items():
        action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
        minimum=100;frame_at_min=0;ankle_error=0
        for frame in range(1,spec['frames'][1]+1):
            sc.frame_set(frame);bpy.context.view_layer.update()
            evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh()
            value=min(v.co.z for v in data.vertices);evaluated.to_mesh_clear()
            if value<minimum:minimum=value;frame_at_min=frame
            if clip=='Defeat':
                ankle_error=max(ankle_error,max((arm.pose.bones['foot_'+s].head-arm.pose.bones['foot_'+s].bone.head_local).length for s in ('l','r')))
        floor_checks.append({'clip':clip,'minimum_all_mesh_vertex_z_m':minimum,'frame':frame_at_min,
                             'sampled_frames':spec['frames'][1],'maximum_defeat_ankle_displacement_m':ankle_error})
    (report/'all-mesh-floor.json').write_text(json.dumps(floor_checks,indent=2)+'\n')
    if any(r['minimum_all_mesh_vertex_z_m']<-.0001 for r in floor_checks):raise RuntimeError('Weapon or body penetrates floor; see all-mesh-floor.json')
    if any(r['maximum_defeat_ankle_displacement_m']>.015 for r in floor_checks):raise RuntimeError('Defeat loses its planted feet; see all-mesh-floor.json')
    sc.render.resolution_x=384;sc.render.resolution_y=384;sc.cycles.samples=12
    camera=sc.camera;original_camera=(camera.location.copy(),camera.rotation_euler.copy());original_ortho=camera.data.ortho_scale
    camera.data.ortho_scale=unit['height_m']*1.7
    for clip in ([] if args.skip_render else ['Idle']+selected):
        camera.data.ortho_scale=unit['height_m']*(2.15 if clip=='Victory' and uid in ('wc_u_human_priest','wc_u_orc_mage') else 1.7)
        spec=clips.get(clip,manifest['clips'][clip]);action=bpy.data.actions[spec['action']]
        arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
        frame=spec['frames'][1] if clip=='Defeat' else spec['release_frame'] if clip=='Active' else spec['frames'][1]//2
        sc.frame_set(frame)
        for view in ('portrait','game_angle'):
            if view=='portrait':camera.location,camera.rotation_euler=original_camera
            else:
                h=unit['height_m'];camera.location=(0,h*2.5,h*4.3);camera.rotation_euler=(Vector((0,0,h*.51))-camera.location).to_track_quat('-Z','Y').to_euler()
            sc.render.filepath=str(report/f'{clip}_{view}.png');bpy.ops.render.render(write_still=True)
    camera.location,camera.rotation_euler=original_camera;camera.data.ortho_scale=original_ortho
    idle=bpy.data.actions[manifest['clips']['Idle']['action']];arm.animation_data.action=idle;arm.animation_data.action_slot=idle.slots[0]
    sc.frame_set(1);sc.render.resolution_x=768;sc.render.resolution_y=768
    output_source=source if args.apply else source.parent/'trials/animation-refinement6.blend'
    output_source.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(output_source))
    if geometry_signature()!=signature:raise RuntimeError('Source geometry changed after render/export')
    changed_files={f'AN_{uid}_{clip}.fbx' for clip in selected}
    for name,digest in unchanged.items():
        if name not in changed_files and sha(production/name)!=digest:raise RuntimeError('Unrelated production export changed: '+name)
    evidence={'status':'applied_validated_requires_visual_review' if args.apply else 'isolated_trial_validated_requires_visual_review',
              'unit_id':uid,'changed_clips':selected,'source_before_sha256':original_source_hash,'source_after_sha256':sha(output_source),
              'geometry_weights_uv_rest_unchanged':True,'geometry_signature':signature,'source':str(output_source.relative_to(ROOT)),
              'preview_status':'not_rerendered_in_this_pass' if args.skip_render else 'actual_source_pose_renders_written',
              'clips':clips,'exports':{name:sha(target/name) for name in changed_files}}
    if args.apply:
        manifest.setdefault('geometry_source_revision',manifest['source_revision']);manifest['source_revision']=6
        manifest['animation_revision']=6;manifest['animation_refinement_script_sha256']=sha(Path(__file__))
        manifest['animation_pose_script_sha256']=sha(ROOT/'tools/blender/refine_animation_poses.py')
        manifest['animation_author_script_sha256']=sha(ROOT/'tools/blender/author_alpha.py')
        manifest['animation_contact_script_sha256']=sha(ROOT/'tools/blender/hand_contacts.py')
        manifest['animation_normalizer_sha256']=sha(ROOT/'tools/blender/normalized_fbx.py')
        manifest['source_sha256']=sha(source);manifest['clips'].update(clips);manifest['files'].update(evidence['exports'])
        manifest['animation_evidence']=str(report.relative_to(ROOT))
        (production/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif sha(source)!=original_source_hash:raise RuntimeError('Trial changed production source')
    (report/('applied.json' if args.apply else 'trial.json')).write_text(json.dumps(evidence,indent=2)+'\n')
    print('WC_ANIMATION_REFINEMENT_COMPLETE '+uid,flush=True)

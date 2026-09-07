"""Import owned Blender exports using the measured UE 5.7 legacy FBX preset."""
from pathlib import Path
import json
import hashlib
import os
import runpy
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.Enable 0")
assets = unreal.AssetToolsHelpers.get_asset_tools()
library = unreal.EditorAssetLibrary
window_contract = runpy.run_path(str(ROOT/'tools/unreal/attack_window_contract.py'))

def animation_marker_api():
    # Installed UCLASS metadata exposes UAnimationBlueprintLibrary as AnimationLibrary.
    api = unreal.AnimationLibrary
    for name in ('get_animation_sync_markers', 'remove_animation_sync_markers_by_name',
                 'is_valid_anim_notify_track_name', 'add_animation_notify_track', 'add_animation_sync_marker'):
        if not callable(getattr(api, name, None)):
            raise RuntimeError('Required installed AnimationLibrary API unavailable: '+name)
    return api

def install_attack_windows(sequence, plan):
    api = animation_marker_api()
    # Remove only this owned marker namespace; unrelated sync markers remain intact.
    previous = api.get_animation_sync_markers(sequence)
    for name in {str(marker.marker_name) for marker in previous if str(marker.marker_name).startswith(window_contract['PREFIX'])}:
        api.remove_animation_sync_markers_by_name(sequence, name)
    if plan:
        if not api.is_valid_anim_notify_track_name(sequence, window_contract['TRACK']):
            api.add_animation_notify_track(sequence, window_contract['TRACK'])
        for name, time in plan['markers'].items():
            api.add_animation_sync_marker(sequence, name, time, window_contract['TRACK'])
    actual = [(str(marker.marker_name), float(marker.time)) for marker in api.get_animation_sync_markers(sequence)]
    checked = window_contract['validate_imported_markers'](plan, float(sequence.sequence_length), actual)
    # AnimationLibrary sync-marker edits do not mark the package dirty in UE5.7.
    # Force persistence; the separate cold-load test verifies the serialized markers.
    if not library.save_loaded_asset(sequence, only_if_is_dirty=False):
        raise RuntimeError('Cannot persist authored Attack window markers: '+sequence.get_path_name())
    return checked

def task(filename, destination, name, options=None, factory=None):
    existing = unreal.load_asset(destination + '/' + name)
    if existing and options and str(filename).lower().endswith('.fbx'):
        data = existing.get_editor_property('asset_import_data')
        if data:
            is_static = isinstance(existing, unreal.StaticMesh)
            for key, value in {
                'convert_scene': True, 'convert_scene_unit': True,
                'force_front_x_axis': is_static,
                'import_rotation': unreal.Rotator(pitch=0,yaw=180 if is_static else 90,roll=0),
                'import_translation': unreal.Vector(0,0,0),
                'import_uniform_scale': 1.0,
            }.items(): data.set_editor_property(key, value)
            if isinstance(existing, unreal.AnimSequence):
                data.set_editor_property('preserve_local_transform', False)
            elif isinstance(existing, unreal.SkeletalMesh):
                data.set_editor_property('update_skeleton_reference_pose', True)
    job = unreal.AssetImportTask()
    job.filename = str(filename)
    job.destination_path = destination
    job.destination_name = name
    job.automated = True
    job.replace_existing = True
    job.save = True
    if options: job.options = options
    if factory: job.factory = factory
    elif str(filename).lower().endswith('.png'): job.factory = unreal.TextureFactory()
    elif str(filename).lower().endswith('.wav'): job.factory = unreal.SoundFactory()
    assets.import_asset_tasks([job])
    if not job.imported_object_paths:
        raise RuntimeError('Import returned no assets: ' + str(filename))
    return [unreal.load_asset(path) for path in job.imported_object_paths]

def fbx_settings(kind, skeleton=None):
    options = unreal.FbxImportUI()
    options.automated_import_should_detect_type = False
    options.import_materials = False
    options.import_textures = False
    options.create_physics_asset = False
    options.import_as_skeletal = kind != 'static'
    options.import_mesh = kind != 'animation'
    options.import_animations = kind == 'animation'
    options.mesh_type_to_import = {'static':unreal.FBXImportType.FBXIT_STATIC_MESH,'skeletal':unreal.FBXImportType.FBXIT_SKELETAL_MESH,'animation':unreal.FBXImportType.FBXIT_ANIMATION}[kind]
    if skeleton: options.skeleton = skeleton
    for data in (options.static_mesh_import_data, options.skeletal_mesh_import_data, options.anim_sequence_import_data):
        data.convert_scene = True
        data.convert_scene_unit = True
        data.force_front_x_axis = kind == 'static'
        data.import_rotation = unreal.Rotator(pitch=0,yaw=180 if kind == 'static' else 90,roll=0)
        data.import_uniform_scale = 1
    options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', True)
    options.anim_sequence_import_data.set_editor_property('preserve_local_transform', False)
    return options

def hero_material(uid, folder, source):
    base = task(source / f'T_{uid}_BaseColor.png',folder,f'T_{uid}_BaseColor')[0]
    base.set_editor_property('srgb', True)
    mask = task(source / f'T_{uid}_ORM.png',folder,f'T_{uid}_ORM')[0]
    mask.set_editor_property('srgb', False)
    normal=task(source/f'T_{uid}_Normal.png',folder,f'T_{uid}_Normal')[0]
    normal.set_editor_property('srgb',False)
    normal.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP)
    master_path = '/Game/WonderChess/Materials/M_WC_Hero'
    master = unreal.load_asset(master_path)
    if not master:
        master = assets.create_asset('M_WC_Hero','/Game/WonderChess/Materials',unreal.Material,unreal.MaterialFactoryNew())
        sample = unreal.MaterialEditingLibrary.create_material_expression(master,unreal.MaterialExpressionTextureSampleParameter2D,-500,0)
        sample.set_editor_property('parameter_name', 'BaseColor')
        sample.set_editor_property('texture', base)
        unreal.MaterialEditingLibrary.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
        packed = unreal.MaterialEditingLibrary.create_material_expression(master,unreal.MaterialExpressionTextureSampleParameter2D,-500,250)
        packed.set_editor_property('parameter_name', 'ORM')
        packed.set_editor_property('texture', mask)
        packed.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
        for channel,prop in [('R',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),('G',unreal.MaterialProperty.MP_ROUGHNESS),('B',unreal.MaterialProperty.MP_METALLIC)]:
            unreal.MaterialEditingLibrary.connect_material_property(packed,channel,prop)
        unreal.MaterialEditingLibrary.recompile_material(master)
        library.save_loaded_asset(master)
    unreal.MaterialEditingLibrary.set_material_usage(master,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    library.save_loaded_asset(master)
    expressions=unreal.MaterialEditingLibrary.get_material_default_texture_parameter_value(master,'Normal')
    if not expressions:
        sample=unreal.MaterialEditingLibrary.create_material_expression(master,unreal.MaterialExpressionTextureSampleParameter2D,-500,500)
        sample.set_editor_property('parameter_name','Normal')
        sample.set_editor_property('texture',normal)
        sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        unreal.MaterialEditingLibrary.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_NORMAL)
        unreal.MaterialEditingLibrary.recompile_material(master)
        library.save_loaded_asset(master)
    instance = unreal.load_asset(folder+'/MI_'+uid)
    if not instance: instance=assets.create_asset('MI_'+uid,folder,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance,master)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(instance,'BaseColor',base)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(instance,'ORM',mask)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(instance,'Normal',normal)
    for asset in (base,mask,normal,instance): library.save_loaded_asset(asset)
    return instance

def env_flag(name):
    value = os.environ.get(name, '').strip().lower()
    if value in ('', '0', 'false', 'no', 'off'): return False
    if value in ('1', 'true', 'yes', 'on'): return True
    raise ValueError('Expected a boolean environment flag: ' + name)


def main():
    rules=json.loads((ROOT/'data/rules.alpha.json').read_text())
    units={unit['id']:unit for unit in json.loads((ROOT/'data/units.json').read_text())['units']}
    only=os.environ.get('WC_IMPORT_HERO')
    audio_only = env_flag('WC_IMPORT_AUDIO_ONLY')
    if not audio_only: animation_marker_api()
    import_audio = audio_only or not only or env_flag('WC_IMPORT_AUDIO')
    if only and set(only.split(',')) - set(rules['alpha_unit_ids']):
        raise ValueError('Unknown hero selection')
    reports=[]
    audio_reports=[]
    for uid in rules['alpha_unit_ids']:
        if audio_only: continue
        if only and uid not in only.split(','): continue
        source=ROOT/'exports/heroes'/uid
        manifest_path=source/'export_manifest.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest['unit_id'] != uid: raise ValueError('Hero export identity mismatch: '+uid)
        attack_plan=window_contract['attack_window_plan'](manifest['clips']['Attack'],manifest['fps'],units[uid]['stats']['attack_windup_ms'])
        source_blend=ROOT/'art-source/heroes'/uid/(uid+'.blend')
        if hashlib.sha256(source_blend.read_bytes()).hexdigest() != manifest['source_sha256']:
            raise ValueError('Hero source differs from frozen export: '+uid)
        for filename, digest in manifest['files'].items():
            if hashlib.sha256((source/filename).read_bytes()).hexdigest() != digest:
                raise ValueError('Hero export changed: '+uid+'/'+filename)
        folder='/Game/WonderChess/Heroes/'+uid
        material=hero_material(uid,folder,source)
        existing=unreal.load_asset(folder+'/SK_'+uid)
        prior_skeleton=existing.skeleton if existing else None
        skeletal=task(source/f'SK_{uid}.fbx',folder,f'SK_{uid}',fbx_settings('skeletal',prior_skeleton),unreal.FbxFactory())
        mesh=next((x for x in skeletal if isinstance(x,unreal.SkeletalMesh)),None)
        if mesh is None: raise RuntimeError('Missing skeletal mesh '+uid)
        if not mesh.skeleton: raise RuntimeError('Imported mesh has no skeleton '+uid)
        if not library.save_loaded_asset(mesh.skeleton): raise RuntimeError('Cannot persist generated skeleton '+uid)
        mesh.set_editor_property('materials',[unreal.SkeletalMaterial(material_interface=material,material_slot_name='HeroAtlas')])
        lods=[]
        subsystem=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
        for lod in (1,2):
            source_lod=source/f'SK_{uid}_LOD{lod}.fbx'
            result=subsystem.import_lod(mesh,lod,str(source_lod))
            if result!=lod: raise RuntimeError(f'Failed LOD {lod} for {uid}: {result}')
            lods.append(result)
        mesh.set_editor_property('materials',[unreal.SkeletalMaterial(material_interface=material,material_slot_name=slot.material_slot_name) for slot in mesh.materials])
        library.save_loaded_asset(mesh)
        library.save_loaded_asset(mesh.skeleton)
        clips=[]
        for clip in ['Idle','Move','Attack','Active','Hit','Defeat','Victory']:
            name=f'AN_{uid}_{clip}'
            imported=task(source/(name+'.fbx'),folder,name,fbx_settings('animation',mesh.skeleton),unreal.FbxFactory())
            animations=[x for x in imported if isinstance(x,unreal.AnimSequence)]
            if len(animations)!=1: raise RuntimeError('Expected one animation '+name)
            sequence=animations[0]
            marker_result=install_attack_windows(sequence,attack_plan) if clip=='Attack' else None
            clips.append({'name':clip,'path':sequence.get_path_name(),'length':sequence.sequence_length,'attack_window_markers':marker_result})
        portrait=source/'portrait.png'
        if portrait.is_file(): task(portrait,folder,'T_'+uid+'_Portrait')
        bounds=mesh.get_bounds()
        reports.append({'id':uid,'mesh':mesh.get_path_name(),'skeleton':mesh.skeleton.get_path_name(),'prior_skeleton_existed':prior_skeleton is not None,'prior_skeleton_identity_preserved':prior_skeleton==mesh.skeleton if prior_skeleton else None,'skeleton_saved':True,'reference_pose_refresh_requested':True,'cold_reload_validation':'PENDING_SEPARATE_PROCESS','bounds_extent_cm':[bounds.box_extent.x,bounds.box_extent.y,bounds.box_extent.z],'clips':clips,'lods':lods,'status':'IMPORTED_NOT_VISUALLY_ACCEPTED'})
        reports[-1].update({'source_revision':manifest.get('source_revision'),'source_sha256':manifest['source_sha256'],'export_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'units_sha256_at_export':manifest.get('units_source_sha256'),'units_sha256_at_import':hashlib.sha256((ROOT/'data/units.json').read_bytes()).hexdigest()})
        unreal.log('WC_HERO_IMPORTED '+uid)

    expected_ids = [] if audio_only else [uid for uid in rules['alpha_unit_ids'] if not only or uid in only.split(',')]
    if [item['id'] for item in reports] != expected_ids:
        raise RuntimeError('Completed imports do not match the selected heroes')
    if import_audio:
        for path in (ROOT/'exports/audio').glob('*.wav'):
            sounds=task(path,'/Game/WonderChess/Audio',path.stem)
            for sound in sounds:
                if isinstance(sound,unreal.SoundWave):
                    sound.set_sound_asset_compression_type(unreal.SoundAssetCompressionType.PCM)
                    if not library.save_loaded_asset(sound): raise RuntimeError('Cannot save audio: '+sound.get_path_name())
                    audio_reports.append({'path':sound.get_path_name(),'source':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'duration_seconds':sound.get_editor_property('duration'),'channels':sound.get_editor_property('num_channels'),'compression':'PCM','listening_review':'NOT_RUN'})

    report_dir=Path(os.environ.get('WC_EDITOR_REPORT_DIR', str(ROOT/'reports/WC-330'))).resolve()
    report=report_dir/('import-'+('audio' if audio_only else ('selected' if only and ',' in only else only) or 'alpha')+'.json')
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps({'engine':unreal.SystemLibrary.get_engine_version(),'selected_hero_ids':expected_ids,'audio_only':audio_only,'audio_requested':import_audio,'heroes':reports,'audio':audio_reports},indent=2)+'\n')
    unreal.log('WC_ALPHA_IMPORT_COMPLETE '+str(len(reports)))

if __name__ == "__main__": main()

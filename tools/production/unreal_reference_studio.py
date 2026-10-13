"""Build and render an isolated four-camera studio from an explicit JSON recipe.

Launch in a fresh editor with -ExecutePythonScript, not a NullRHI commandlet.
WC_REFERENCE_STUDIO_CONFIG points to the recipe. Existing outputs are refused.
"""
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
import unreal as u

ROOT = Path(__file__).resolve().parents[2]
config_path = Path(os.environ['WC_REFERENCE_STUDIO_CONFIG'])
cfg = json.loads(config_path.read_text(encoding='utf-8-sig'))
out = (ROOT / cfg['output_directory']).resolve()
if not out.is_relative_to(ROOT): raise ValueError('Evidence must remain inside the project')
out.mkdir(parents=True, exist_ok=False)
folder = cfg['asset_folder']
if not folder.startswith('/Game/WonderChess/Diagnostics/'):
    raise ValueError('This studio builder only writes a diagnostic namespace')
level_path = folder + '/L_ReferenceStudio'
if u.EditorAssetLibrary.does_asset_exist(level_path): raise ValueError('Choose a new studio revision')
assets = u.AssetToolsHelpers.get_asset_tools()
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assert levels.new_level(level_path)
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
mesh = u.load_asset(cfg['skeletal_mesh'])
assert isinstance(mesh, u.SkeletalMesh)
actor = actors.spawn_actor_from_class(u.SkeletalMeshActor, u.Vector(*cfg['position_cm']),
                                      u.Rotator(pitch=0, yaw=cfg['yaw_degrees'], roll=0))
actor.set_actor_label('ReferenceCreature_UnchangedGeometry')
actor.set_actor_scale3d(u.Vector(*cfg['scale']))
component = actor.get_component_by_class(u.SkeletalMeshComponent)
component.set_skeletal_mesh_asset(mesh)
component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
library = u.MaterialEditingLibrary
materials = {}
post = u.PostProcessSettings()
for key, value in {'override_auto_exposure_method': True,
                   'auto_exposure_method': u.AutoExposureMethod.AEM_MANUAL,
                   'override_auto_exposure_apply_physical_camera_exposure': True,
                   'auto_exposure_apply_physical_camera_exposure': False,
                   'override_auto_exposure_bias': True, 'auto_exposure_bias': 0.0,
                   'override_ambient_occlusion_intensity': True, 'ambient_occlusion_intensity': 0.0,
                   'override_bloom_intensity': True, 'bloom_intensity': 0.0}.items():
    post.set_editor_property(key, value)
for mode in ('lit', 'basecolor'):
    material = assets.create_asset('M_OriginalColor_' + mode, folder, u.Material, u.MaterialFactoryNew())
    assert material
    library.set_material_usage(material, u.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    if mode == 'basecolor': material.set_editor_property('shading_model', u.MaterialShadingModel.MSM_UNLIT)
    for kind, path in cfg['textures'].items():
        if mode == 'basecolor' and kind != 'BaseColor': continue
        texture = u.load_asset(path)
        assert texture
        node = library.create_material_expression(material, u.MaterialExpressionTextureSample, -250, 0)
        node.texture = texture
        node.sampler_type = {'BaseColor': u.MaterialSamplerType.SAMPLERTYPE_COLOR,
                             'Normal': u.MaterialSamplerType.SAMPLERTYPE_NORMAL,
                             'MetallicRoughness': u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR}[kind]
        ports = {'BaseColor': [('RGB', u.MaterialProperty.MP_BASE_COLOR if mode == 'lit' else u.MaterialProperty.MP_EMISSIVE_COLOR)],
                 'Normal': [('RGB', u.MaterialProperty.MP_NORMAL)],
                 'MetallicRoughness': [('G', u.MaterialProperty.MP_ROUGHNESS), ('B', u.MaterialProperty.MP_METALLIC)]}[kind]
        for port, prop in ports: assert library.connect_material_property(node, port, prop)
    library.recompile_material(material)
    assert u.EditorAssetLibrary.save_loaded_asset(material)
    materials[mode] = material
component.set_material(0, materials['lit'])
sky = actors.spawn_actor_from_class(u.SkyLight, u.Vector(0, 0, 300))
skylight = sky.get_component_by_class(u.SkyLightComponent)
skylight.set_mobility(u.ComponentMobility.MOVABLE)
skylight.set_editor_property('source_type', u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
skylight.set_cubemap(u.load_asset('/Engine/EngineResources/GrayLightTextureCube'))
skylight.set_intensity(cfg.get('sky_intensity', 1.0))
skylight.set_cast_shadows(False)
background = assets.create_asset('M_NeutralBackground', folder, u.Material, u.MaterialFactoryNew())
background.set_editor_property('shading_model', u.MaterialShadingModel.MSM_UNLIT)
background.set_editor_property('two_sided', True)
gray = library.create_material_expression(background, u.MaterialExpressionConstant3Vector, -200, 0)
gray.set_editor_property('constant', u.LinearColor(.18, .18, .18, 1))
assert library.connect_material_property(gray, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
library.recompile_material(background)
assert u.EditorAssetLibrary.save_loaded_asset(background)
shell = actors.spawn_actor_from_class(u.StaticMeshActor, u.Vector(0, 0, 85))
shell.set_actor_label('NeutralBackdrop')
shell.set_actor_scale3d(u.Vector(50,50,50))
shell_component = shell.get_component_by_class(u.StaticMeshComponent)
shell_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'))
shell_component.set_material(0, background)
shell_component.set_cast_shadow(False)
shell_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
for light in cfg['lights']:
    actor_light = actors.spawn_actor_from_class(u.DirectionalLight, u.Vector(0, 0, 400),
                                                u.Rotator(pitch=light['pitch'], yaw=light['yaw'], roll=0))
    actor_light.set_actor_label(light['name'])
    lc = actor_light.get_component_by_class(u.DirectionalLightComponent)
    lc.set_mobility(u.ComponentMobility.MOVABLE)
    lc.set_intensity(light['intensity'])
    lc.set_cast_shadows(False)
views = []
target = u.Vector(*cfg['look_at_cm'])
for slot, offset in [('main', (1,0,0)), ('left', (0,-1,0)), ('back', (-1,0,0)), ('right', (0,1,0))]:
    position = target + u.Vector(*(v * cfg['camera_distance_cm'] for v in offset))
    rotation = u.MathLibrary.find_look_at_rotation(position, target)
    camera = actors.spawn_actor_from_class(u.CameraActor, position, rotation)
    camera.set_actor_label('View_' + slot)
    camera.camera_component.set_editor_property('projection_mode', u.CameraProjectionMode.ORTHOGRAPHIC)
    camera.camera_component.set_editor_property('ortho_width', cfg['ortho_width_cm'])
    camera.camera_component.set_editor_property('aspect_ratio', 1.0)
    camera.camera_component.set_editor_property('post_process_settings', post)
    camera.camera_component.set_editor_property('post_process_blend_weight', 1.0)
    views.append({'slot': slot, 'location_cm': [position.x,position.y,position.z],
                  'rotation_degrees': [rotation.pitch,rotation.yaw,rotation.roll],
                  'ortho_width_cm': cfg['ortho_width_cm'], 'camera_label': camera.get_actor_label()})
assert levels.save_current_level()
for command in ('r.DefaultFeature.AutoExposure 0', 'r.DefaultFeature.MotionBlur 0',
                'r.AntiAliasingMethod 0', 'r.Streaming.FullyLoadUsedTextures 1',
                't.IdleWhenNotForeground 0', 'Slate.bAllowThrottling 0'):
    u.SystemLibrary.execute_console_command(world, command)
report = {'status': 'rendering', 'level': level_path, 'config': cfg, 'views': views, 'captures': [],
          'human_acceptance': False, 'scope': 'fixed-camera calibration candidate; not approved board lighting',
          'engine': u.SystemLibrary.get_engine_version()}
def persist(): (out / 'capture.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
def steps():
    yield 90
    for mode in ('lit','basecolor'):
        component.set_material(0, materials[mode])
        yield 25
        for view in views:
            position = u.Vector(*view['location_cm'])
            rotation = u.MathLibrary.find_look_at_rotation(position, target)
            capture = actors.spawn_actor_from_class(u.SceneCapture2D, position, rotation)
            cc = capture.get_component_by_class(u.SceneCaptureComponent2D)
            cc.capture_every_frame = False
            cc.capture_on_movement = False
            cc.capture_source = u.SceneCaptureSource.SCS_FINAL_COLOR_LDR
            cc.projection_type = u.CameraProjectionMode.ORTHOGRAPHIC
            cc.ortho_width = cfg['ortho_width_cm']
            cc.post_process_settings = post
            cc.post_process_blend_weight = 1.0
            rt = u.RenderingLibrary.create_render_target2d(world, cfg['resolution'], cfg['resolution'],
                    u.TextureRenderTargetFormat.RTF_RGBA8, u.LinearColor(.1,.1,.1,1))
            cc.texture_target = rt
            yield 15
            cc.capture_scene()
            yield 10
            u.RenderingLibrary.read_render_target_pixel(world, rt, cfg['resolution']//2, cfg['resolution']//2)
            path = out / (mode + '-' + view['slot'] + '.png')
            u.RenderingLibrary.export_render_target(world, rt, str(out), path.name)
            assert path.is_file()
            report['captures'].append({'mode': mode, 'slot': view['slot'], 'path': path.relative_to(ROOT).as_posix(),
                                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            persist()
            actors.destroy_actor(capture)
    component.set_material(0, materials['lit'])
    assert levels.save_current_level()
    report['status'] = 'rendered_review_pending'

u.EditorPythonScripting.set_keep_python_script_alive(True)
state = {'wait': 0, 'busy': False, 'handle': None, 'start': time.monotonic(), 'iterator': steps()}
def finish(error=None):
    if error: report.update(status='fail', error=error)
    persist()
    u.unregister_slate_post_tick_callback(state['handle'])
    u.EditorPythonScripting.set_keep_python_script_alive(False)
def tick(delta):
    if state['busy']: return
    if time.monotonic()-state['start'] > 420: finish('Capture timeout'); return
    if state['wait'] > 0: state['wait'] -= 1; return
    state['busy'] = True
    try: state['wait'] = next(state['iterator'])
    except StopIteration: finish()
    except Exception: finish(traceback.format_exc())
    finally: state['busy'] = False
state['handle'] = u.register_slate_post_tick_callback(tick)
persist()

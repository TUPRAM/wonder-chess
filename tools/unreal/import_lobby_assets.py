"""Import the original Brighthaven approach without altering shared arena assets."""
from pathlib import Path
import hashlib
import json
import os
import sys
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
sys.path.insert(0, str(ROOT / 'tools/unreal'))
from import_alpha_assets import task, fbx_settings

source = ROOT / 'exports/lobby'
manifest_path = source / 'lobby_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
source_path = Path(manifest['source']).resolve()
if not source_path.is_relative_to(ROOT / 'art-source/lobby'):
    raise RuntimeError('Lobby source must remain in its owned source directory')
if hashlib.sha256(source_path.read_bytes()).hexdigest() != manifest['source_sha256']:
    raise RuntimeError('Lobby source differs from its export manifest')
for name, expected in manifest['files'].items():
    path = (source / name).resolve()
    if not path.is_relative_to(source) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Lobby export hash mismatch: ' + name)

folder = '/Game/WonderChess/Lobby'
assets = unreal.AssetToolsHelpers.get_asset_tools()
library = unreal.EditorAssetLibrary
master = unreal.load_asset('/Game/WonderChess/Materials/M_WC_Hero')
if not master:
    raise RuntimeError('Verified shared surface material is missing')
material = unreal.load_asset(folder + '/MI_WC_Brighthaven')
if not material:
    material = assets.create_asset('MI_WC_Brighthaven', folder, unreal.MaterialInstanceConstant,
                                  unreal.MaterialInstanceConstantFactoryNew())
unreal.MaterialEditingLibrary.set_material_instance_parent(material, master)
for channel in ('BaseColor', 'Normal', 'ORM'):
    texture = task(source / ('T_wc_brighthaven_approach_' + channel + '.png'), folder,
                   'T_WC_Brighthaven_' + channel)[0]
    texture.set_editor_property('srgb', channel == 'BaseColor')
    if channel == 'Normal':
        texture.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material, channel, texture)
    if not library.save_loaded_asset(texture):
        raise RuntimeError('Cannot save lobby texture')
if not library.save_loaded_asset(material):
    raise RuntimeError('Cannot save lobby material instance')

subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
records = []
for name in [manifest['combined_mesh'], *manifest['modules']]:
    options = fbx_settings('static')
    options.static_mesh_import_data.combine_meshes = True
    loaded = task(source / (name + '.fbx'), folder, name, options, unreal.FbxFactory())
    meshes = [item for item in loaded if isinstance(item, unreal.StaticMesh)]
    if len(meshes) != 1:
        raise RuntimeError('Expected one combined static mesh: ' + name)
    mesh = meshes[0]
    if name == manifest['combined_mesh']:
        for lod in (1, 2):
            if subsystem.import_lod(mesh, lod, str(source / (name + f'_LOD{lod}.fbx'))) != lod:
                raise RuntimeError('Failed lobby LOD: ' + str(lod))
        if subsystem.get_lod_count(mesh) != 3:
            raise RuntimeError('Expected three imported lobby LODs')
    mesh.set_material(0, material)
    if not library.save_loaded_asset(mesh):
        raise RuntimeError('Cannot save lobby mesh: ' + name)
    bounds = mesh.get_bounding_box()
    size = bounds.max - bounds.min
    if name == manifest['combined_mesh']:
        expected_height = (manifest['bounds']['max_m'][2] - manifest['bounds']['min_m'][2]) * 100
        if abs(size.z - expected_height) > 1:
            raise RuntimeError(f'Lobby centimeter calibration mismatch: {size.z} versus {expected_height}')
    records.append({'name': name, 'path': mesh.get_path_name(),
                    'bounds_min_cm': [bounds.min.x, bounds.min.y, bounds.min.z],
                    'bounds_max_cm': [bounds.max.x, bounds.max.y, bounds.max.z],
                    'lod_count': subsystem.get_lod_count(mesh)})
report = {'status': 'IMPORTED_PLACEMENT_VISUAL_AND_PERFORMANCE_REVIEW_PENDING',
          'engine': unreal.SystemLibrary.get_engine_version(),
          'source_sha256': manifest['source_sha256'],
          'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          'shared_material_changed': False, 'meshes': records}
output = Path(os.environ['WC_EDITOR_REPORT_DIR']) / 'lobby-import.json'
output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
unreal.log('WC_LOBBY_IMPORT_PASS ' + str(len(records)))

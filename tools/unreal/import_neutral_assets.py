"""Import owned mechanical neutral assets through the measured skeletal FBX path."""
from pathlib import Path
import hashlib
import json
import os
import sys
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
sys.path.insert(0, str(ROOT / 'tools/unreal'))
from import_alpha_assets import task, fbx_settings, hero_material, library


def main():
    definitions = json.loads((ROOT / 'data/neutrals.json').read_text(encoding='utf-8'))['creatures']
    selected = set(filter(None, os.environ.get('WC_IMPORT_NEUTRALS', '').split(',')))
    if selected - {row['id'] for row in definitions}:
        raise ValueError('Unknown neutral selection')
    reports = []
    for definition in definitions:
        uid = definition['id']
        if selected and uid not in selected:
            continue
        source = ROOT / 'exports/neutrals' / uid
        manifest = json.loads((source / 'export_manifest.json').read_text(encoding='utf-8'))
        if manifest['unit_id'] != uid:
            raise ValueError('Neutral export identity mismatch: ' + uid)
        for name, expected in manifest['files'].items():
            if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
                raise ValueError('Changed export: ' + str(source / name))
        blend = ROOT / 'art-source/neutrals' / uid / (uid + '.blend')
        if hashlib.sha256(blend.read_bytes()).hexdigest() != manifest['source_sha256']:
            raise ValueError('Changed neutral authoring source: ' + uid)
        folder = '/Game/WonderChess/Neutrals/' + uid
        material = hero_material(uid, folder, source)
        existing = unreal.load_asset(folder + '/SK_' + uid)
        skeleton = existing.skeleton if existing else None
        imported = task(source / ('SK_' + uid + '.fbx'), folder, 'SK_' + uid,
                        fbx_settings('skeletal', skeleton), unreal.FbxFactory())
        meshes = [obj for obj in imported if isinstance(obj, unreal.SkeletalMesh)]
        if len(meshes) != 1 or not meshes[0].skeleton:
            raise RuntimeError('Expected one skeletal neutral with skeleton: ' + uid)
        mesh = meshes[0]
        subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
        for lod in (1, 2):
            if subsystem.import_lod(mesh, lod, str(source / f'SK_{uid}_LOD{lod}.fbx')) != lod:
                raise RuntimeError(f'Neutral LOD failed: {uid}/{lod}')
        mesh.set_editor_property('materials', [unreal.SkeletalMaterial(material_interface=material, material_slot_name=slot.material_slot_name) for slot in mesh.materials])
        for asset in (mesh.skeleton, mesh):
            if not library.save_loaded_asset(asset):
                raise RuntimeError('Cannot save imported neutral asset: ' + asset.get_path_name())
        clips = []
        required = ['Idle', 'Move', 'Attack', 'Hit', 'Defeat'] + (['Active'] if definition['ability'] else [])
        for clip in required:
            name = f'AN_{uid}_{clip}'
            animations = [obj for obj in task(source / (name + '.fbx'), folder, name,
                          fbx_settings('animation', mesh.skeleton), unreal.FbxFactory()) if isinstance(obj, unreal.AnimSequence)]
            if len(animations) != 1 or animations[0].sequence_length <= 0:
                raise RuntimeError('Invalid imported neutral clip: ' + name)
            clips.append({'name': clip, 'path': animations[0].get_path_name(), 'seconds': animations[0].sequence_length})
        task(source / 'portrait.png', folder, 'T_' + uid + '_Portrait')
        bounds = mesh.get_bounds()
        reports.append({'id': uid, 'status': 'IMPORTED_COLD_VALIDATION_AND_VISUAL_REVIEW_PENDING',
                        'source_revision': manifest['source_revision'], 'source_sha256': manifest['source_sha256'],
                        'manifest_sha256': hashlib.sha256((source / 'export_manifest.json').read_bytes()).hexdigest(),
                        'mesh': mesh.get_path_name(), 'skeleton': mesh.skeleton.get_path_name(),
                        'bounds_cm': [bounds.box_extent.x*2, bounds.box_extent.y*2, bounds.box_extent.z*2],
                        'clips': clips, 'lods': [0, 1, 2]})
        unreal.log('WC_NEUTRAL_IMPORTED ' + uid)
    output = Path(os.environ['WC_EDITOR_REPORT_DIR'])
    output.mkdir(parents=True, exist_ok=True)
    (output / 'neutral-import.json').write_text(json.dumps({'engine': unreal.SystemLibrary.get_engine_version(), 'neutrals': reports}, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

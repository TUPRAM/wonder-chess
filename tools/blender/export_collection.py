"""Blender-only selection exporter, syntax checked but NOT Blender/Unreal tested here.
Exports a named collection and the currently assigned action/frame range. Does NOT retarget,
apply transforms, invent an animation selection, export all actions, or certify the FBX.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys


def main() -> None:
    import bpy
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collection', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--acknowledge-unverified-profile', action='store_true')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    profile = json.loads(args.profile.read_text(encoding='utf-8'))
    if profile.get('status') != 'CALIBRATED' and not args.acknowledge_unverified_profile:
        raise RuntimeError('Profile is unverified. Use acknowledgement for calibration only; do not label output accepted')
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != '.fbx':
        raise ValueError('Output must have .fbx extension')
    if output.exists() and not args.overwrite:
        raise FileExistsError(f'Refusing to overwrite {output}')
    collection = bpy.data.collections.get(args.collection)
    if not collection:
        raise ValueError(f'Collection not found: {args.collection}')
    objects = [obj for obj in collection.all_objects if obj.type in {'MESH', 'ARMATURE'}]
    if not any(obj.type == 'MESH' for obj in objects):
        raise ValueError('No exportable mesh in collection')
    if bpy.context.mode != 'OBJECT':
        raise RuntimeError('Leave edit/pose mode before export; this script will not change the authoring state')
    for obj in objects:
        if any(abs(float(scale) - 1.0) > 1e-5 for scale in obj.scale):
            raise ValueError(f'{obj.name}: non-unit scale; inspect source pipeline instead of applying blindly')
        if obj.hide_get() or obj.hide_select or obj.name not in bpy.context.view_layer.objects:
            raise ValueError(f'{obj.name}: hidden, unselectable, or absent from active view layer')
    options = dict(profile['operator'])
    options['use_selection'] = True
    options['object_types'] = {'MESH', 'ARMATURE'}
    supported = {prop.identifier for prop in bpy.ops.export_scene.fbx.get_rna_type().properties}
    unsupported = sorted(set(options) - supported)
    if unsupported:
        raise RuntimeError(f'Installed FBX exporter does not support options: {unsupported}')
    selected = list(bpy.context.selected_objects)
    active = bpy.context.view_layer.objects.active
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = next((obj for obj in objects if obj.type == 'ARMATURE'), objects[0])
        result = bpy.ops.export_scene.fbx(filepath=str(output), **options)
        if 'FINISHED' not in result or not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError(f'FBX export did not produce a nonempty file: {result}')
    finally:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            if obj.name in bpy.context.view_layer.objects:
                obj.select_set(True)
        bpy.context.view_layer.objects.active = active
    report = {'status': 'exported_not_engine_validated', 'blender_version': bpy.app.version_string,
              'file_name': output.name, 'profile_status': profile.get('status'),
              'frame_range': [bpy.context.scene.frame_start, bpy.context.scene.frame_end],
              'objects': [obj.name for obj in objects],
              'assigned_actions': {obj.name: obj.animation_data.action.name
                                   for obj in objects if obj.animation_data and obj.animation_data.action}}
    output.with_suffix('.export.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

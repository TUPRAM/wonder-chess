"""Blender-only calibration scaffold. Syntax checked; NOT executed in Blender in this kit.
Example: blender --background --factory-startup --python-exit-code 1 --python this_file.py -- --output /absolute/calibration.blend
Creates measurements and a simple animated rig, NOT a finished game asset. Does not clear existing objects.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--overwrite', action='store_true')
    return parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


def main() -> None:
    import bpy
    args = arguments()
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != '.blend':
        raise ValueError('Output must be a .blend file')
    if output.exists() and not args.overwrite:
        raise FileExistsError(f'Refusing to overwrite {output}')
    if 'WC_CALIBRATION' in bpy.data.collections:
        raise RuntimeError('WC_CALIBRATION exists: use a clean scene, not a destructive reset')
    output.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.render.fps = 60
    collection = bpy.data.collections.new('WC_CALIBRATION')
    scene.collection.children.link(collection)
    created = []

    def own(obj, name):
        obj.name = name
        for old_collection in list(obj.users_collection):
            old_collection.objects.unlink(obj)
        collection.objects.link(obj)
        created.append(obj)
        return obj

    bpy.ops.mesh.primitive_cube_add(size=1, location=(-2, 0, 0.5))
    own(bpy.context.object, 'CAL_Cube_1m')
    bpy.ops.mesh.primitive_cube_add(size=1, location=(1, 0, -0.1))
    tile = own(bpy.context.object, 'CAL_Tile_2m')
    tile.dimensions = (2, 2, 0.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Arrow authored in +Y; validate where it points after actual engine import.
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.06, depth=0.9,
                                      location=(1, 0.1, 0.12), rotation=(math.pi / 2, 0, 0))
    own(bpy.context.object, 'CAL_ForwardY_Shaft')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.18, radius2=0, depth=0.35,
                                  location=(1, 0.7, 0.12), rotation=(-math.pi / 2, 0, 0))
    own(bpy.context.object, 'CAL_ForwardY_Tip')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.armature_add(location=(4, 0, 0))
    armature = own(bpy.context.object, 'CAL_Rig')
    bpy.ops.object.mode_set(mode='EDIT')
    root = armature.data.edit_bones[0]
    root.name = 'root'
    root.head, root.tail = (0, 0, 0), (0, 0, 0.2)
    child = armature.data.edit_bones.new('probe')
    child.head, child.tail = (0, 0, 0.2), (0, 0, 1.2)
    child.parent = root
    child.use_connect = True
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.mesh.primitive_cube_add(size=1, location=(4, 0, 0.75))
    probe = own(bpy.context.object, 'CAL_AnimatedProbe')
    probe.dimensions = (0.3, 0.3, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    weights = probe.vertex_groups.new(name='probe')
    weights.add(list(range(len(probe.data.vertices))), 1.0, 'REPLACE')
    modifier = probe.modifiers.new('CAL_Armature', 'ARMATURE')
    modifier.object = armature
    pose = armature.pose.bones['probe']
    pose.rotation_mode = 'XYZ'
    for frame, angle in [(1, 0), (31, math.radians(15)), (61, 0)]:
        pose.rotation_euler = (0, angle, 0)
        pose.keyframe_insert(data_path='rotation_euler', frame=frame, group='probe')
    if armature.animation_data and armature.animation_data.action:
        armature.animation_data.action.name = 'CAL_Probe_OneSecond'
    scene.frame_start, scene.frame_end = 1, 61
    scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    report = {
        'status': 'created_in_blender_not_imported_in_unreal',
        'blender_version': bpy.app.version_string,
        'source_unit': 'meter', 'source_forward': '+Y', 'fps': 60,
        'output_name': output.name,
        'objects': [{'name': obj.name, 'type': obj.type,
                     'dimensions_m': [round(float(v), 6) for v in obj.dimensions]}
                    for obj in created],
        'required_engine_checks': ['cube=100cm', 'tile=200cm', 'arrow=+X',
                                   'root scale is stable', 'animation changes pose, not size'],
    }
    output.with_suffix('.calibration.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

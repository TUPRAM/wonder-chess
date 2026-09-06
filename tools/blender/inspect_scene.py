"""Read-only Blender collection inspection. Syntax checked only in the supplied kit.
Use: blender asset.blend --background --python-exit-code 1 --python inspect_scene.py -- --collection EXPORT --output report.json
Zero exit validates only the reported structural checks, never aesthetics or engine import.
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
    parser.add_argument('--max-materials', type=int, default=2)
    parser.add_argument('--max-triangles', type=int, default=15000)
    parser.add_argument('--max-influences', type=int, default=4)
    parser.add_argument('--require-skin', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    collection = bpy.data.collections.get(args.collection)
    if collection is None:
        raise ValueError(f'Unknown collection: {args.collection}')
    errors, warnings, objects = [], [], []
    total_triangles = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(collection.all_objects, key=lambda item: item.name):
        record = {'name': obj.name, 'type': obj.type, 'scale': list(obj.scale),
                  'dimensions': list(obj.dimensions)}
        if any(abs(float(s) - 1.0) > 1e-5 for s in obj.scale):
            errors.append(f'{obj.name}: non-unit object scale; inspect before rigging/export, do not blindly apply')
        if obj.type == 'MESH':
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                mesh.calc_loop_triangles()
                record['evaluated_triangles'] = len(mesh.loop_triangles)
                total_triangles += len(mesh.loop_triangles)
            finally:
                evaluated.to_mesh_clear()
            record['material_slots'] = len(obj.material_slots)
            record['uv_layers'] = len(obj.data.uv_layers)
            if len(obj.material_slots) > args.max_materials:
                errors.append(f'{obj.name}: too many material slots')
            if not obj.data.uv_layers:
                errors.append(f'{obj.name}: no UV layer')
            if any(slot.material is None for slot in obj.material_slots):
                errors.append(f'{obj.name}: missing material assignment')
            armatures = [mod.object for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object]
            if args.require_skin and not armatures:
                errors.append(f'{obj.name}: no armature modifier (socket props must be checked separately)')
            if armatures:
                deform_names = {bone.name for arm in armatures for bone in arm.data.bones if bone.use_deform}
                group_names = {group.index: group.name for group in obj.vertex_groups}
                unweighted = excessive = unnormalized = 0
                for vertex in obj.data.vertices:
                    weights = [group.weight for group in vertex.groups
                               if group_names.get(group.group) in deform_names and group.weight > 1e-6]
                    unweighted += not weights
                    excessive += len(weights) > args.max_influences
                    unnormalized += bool(weights) and abs(sum(weights) - 1.0) > 1e-3
                record['skin_checks'] = {'unweighted': unweighted, 'excess_influences': excessive,
                                         'unnormalized': unnormalized}
                if unweighted or excessive or unnormalized:
                    errors.append(f'{obj.name}: skin-weight checks failed')
        elif obj.type == 'ARMATURE':
            roots = [bone.name for bone in obj.data.bones if bone.parent is None]
            record['roots'] = roots
            record['deform_bones'] = sum(bone.use_deform for bone in obj.data.bones)
            if roots != ['root']:
                errors.append(f'{obj.name}: expected one root bone named root; got {roots}')
            if record['deform_bones'] > 60:
                warnings.append(f'{obj.name}: exceeds provisional 60-deforming-bone budget')
        objects.append(record)
    if total_triangles > args.max_triangles:
        errors.append(f'Collection has {total_triangles} evaluated triangles, above selected budget')
    if not any(obj['type'] == 'MESH' for obj in objects):
        errors.append('Collection contains no meshes')
    report = {'status': 'failed' if errors else 'structural_checks_passed_visual_review_required',
              'blender_version': bpy.app.version_string, 'collection': args.collection,
              'evaluated_triangle_total': total_triangles, 'objects': objects,
              'errors': errors, 'warnings': warnings,
              'not_checked': ['appearance', 'deformation across all clips', 'UV overlap appropriateness',
                              'normal-map convention', 'Unreal import', 'LOD silhouette', 'gameplay readability']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    if errors:
        raise RuntimeError('Structural validation failed; see report')


if __name__ == '__main__':
    main()

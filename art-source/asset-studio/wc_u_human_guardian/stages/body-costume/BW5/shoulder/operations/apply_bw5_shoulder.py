"""Apply the REJECTED Ada-only shoulder study to an independent diagnostic scene.

No scene loads or saves. Owns exactly six named shoulder objects; one retained
failed standalone trim becomes inactive because its replacement is connected to Lame2.
"""
import json
from pathlib import Path
import bpy

DEFAULT_RECORD = Path(__file__).resolve().parents[1] / 'records/final_owned_geometry.json'

def apply_bw5_shoulder(scene=None, record_path=DEFAULT_RECORD):
    scene = scene or bpy.context.scene
    record = json.loads(Path(record_path).read_text())
    assert scene.name == 'BW4_ARMOR_LOCAL_AUTHORING_ONLY' or scene.get('BW5_INDEPENDENT_ARMOR_CANDIDATE'), 'Independent armor scene required'
    for name, spec in record['objects'].items():
        obj = scene.objects.get(name)
        assert obj is not None and obj.type == 'MESH', name
        assert max(abs(obj.matrix_world[i][j] - spec['matrix_world'][i][j]) for i in range(4) for j in range(4)) < 1e-6, name + ': changed registration'
        armatures = [m for m in obj.modifiers if m.type == 'ARMATURE']
        assert len(armatures) == 1 and armatures[0].object.name == 'BW4_Armor_Independent_Rig', name + ': attachment conflict'
        mesh = bpy.data.meshes.new(name + '_BW5_ExecutedSurface')
        mesh.from_pydata(spec['vertices'], [], spec['faces'])
        mesh.update()
        for material in obj.data.materials:
            mesh.materials.append(material)
        obj.data = mesh
        for polygon in mesh.polygons:
            polygon.use_smooth = True
        if spec['crease_edges'] is not None:
            assert len(mesh.edges) == len(spec['crease_edges'])
            crease = mesh.attributes.new('crease_edge', 'FLOAT', 'EDGE')
            for entry, value in zip(crease.data, spec['crease_edges']):
                entry.value = value
        obj.vertex_groups.clear()
        group = obj.vertex_groups.new(name=spec['owner_bone'])
        group.add(list(range(len(mesh.vertices))), 1, 'REPLACE')
        for modifier in obj.modifiers:
            entry = next(m for m in spec['modifiers'] if m['name'] == modifier.name and m['type'] == modifier.type)
            modifier.show_viewport = entry['show_viewport']
            modifier.show_render = entry['show_render']
            if modifier.type == 'SOLIDIFY':
                for key in ['thickness', 'offset', 'use_even_offset']:
                    setattr(modifier, key, entry[key])
        for key, value in spec['properties'].items():
            obj[key] = value
        obj.hide_render = spec['hidden_superseded']
        obj.hide_set(spec['hidden_superseded'])
    scene['BW5_SHOULDER_EXPLICIT_ACTIVE'] = json.dumps(record['active_objects'])
    scene['BW5_SHOULDER_SCOPE'] = record['scope']
    bpy.context.view_layer.update()
    return record['active_objects']

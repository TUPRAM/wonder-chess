"""Author a new synthetic scene solely for locally executing AS1 helper APIs."""
from pathlib import Path
import json
import sys
import bpy

root = Path(sys.argv[sys.argv.index('--') + 1])
assert not (root / 'fixture.blend').exists()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new('AS1_FIXTURE')
scene.collection.children.link(collection)


def move(ob):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    collection.objects.link(ob)


def material(name, color, metallic):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Metallic'].default_value = metallic
    node.inputs['Roughness'].default_value = .42
    return mat


bpy.ops.mesh.primitive_cube_add(size=1, location=(-.3, 0, .6))
box = bpy.context.object
box.name = 'FixtureWeightedBox'
box.scale = (.55, .4, 1.2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
box['wc_part_id'] = 'fixture_weighted_box'
box.data.materials.append(material('FixtureBlue', (.025, .2, .6), .3))
move(box)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.38, location=(.5, 0, .9))
sphere = bpy.context.object
sphere.name = 'FixtureSphere'
sphere['wc_part_id'] = 'fixture_unskinned_sphere'
sphere.data.materials.append(material('FixtureRed', (.65, .045, .018), 0))
for face in sphere.data.polygons:
    face.use_smooth = True
move(sphere)
arm = bpy.data.armatures.new('FixtureSkeleton')
rig = bpy.data.objects.new('FixtureRig', arm)
collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bone = arm.edit_bones.new('root')
bone.head = (0, 0, 0)
bone.tail = (0, 0, 1)
bpy.ops.object.mode_set(mode='OBJECT')
group = box.vertex_groups.new(name='root')
group.add(list(range(len(box.data.vertices))), 1, 'REPLACE')
modifier = box.modifiers.new('FixtureSkin', 'ARMATURE')
modifier.object = rig
scene.frame_set(1)
(root / 'installed-bpy-api.json').write_text(json.dumps({
    'blender_version': bpy.app.version_string,
    'save_as_mainfile_doc': bpy.ops.wm.save_as_mainfile.__doc__,
    'render_doc': bpy.ops.render.render.__doc__,
    'mesh_calc_loop_triangles_doc': box.data.calc_loop_triangles.__doc__,
    'image_empty_display_type': 'IMAGE' in [i.identifier for i in bpy.types.Object.bl_rna.properties['empty_display_type'].enum_items],
    'material_override_property': 'material_override' in scene.view_layers[0].bl_rna.properties,
    'armature_preserve_volume_property': 'use_deform_preserve_volume' in modifier.bl_rna.properties,
}, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'fixture.blend'), check_existing=True)
print('NEW AS1 SYNTHETIC FIXTURE SAVED; NO ADA SOURCE OPENED')

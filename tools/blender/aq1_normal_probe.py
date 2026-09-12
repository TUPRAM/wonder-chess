"""Build/bake/render an isolated, physically raised AQ1 tangent-normal probe.

Run inside Blender, or call ``build_probe(outdir)`` from the AQ1 execution lane.
Only a new probe scene and the explicit output directory are written. The open
hero, its rig, actions, materials and source file are never edited or saved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _mesh(scene, name, vertices, faces, material, make_uv=False):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    if make_uv:
        uv = mesh.uv_layers.new(name="UV0_SourceXY")
        for polygon in mesh.polygons:
            for loop in polygon.loop_indices:
                point = mesh.vertices[mesh.loops[loop].vertex_index].co
                uv.data[loop].uv = ((point.x + .2) / .4, (point.y + .2) / .4)
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def _inset(polygon, distance):
    """Intersect inward parallel edges; keeps the unequal chevron legs intact."""
    points = [Vector(point) for point in polygon]
    area = sum(points[i].x * points[(i + 1) % len(points)].y -
               points[(i + 1) % len(points)].x * points[i].y
               for i in range(len(points)))
    if area <= 0:
        raise ValueError("Probe polygons must be counterclockwise")
    result = []
    for index, corner in enumerate(points):
        before = points[(index - 1) % len(points)]
        after = points[(index + 1) % len(points)]
        u, v = (corner - before).normalized(), (after - corner).normalized()
        a = corner + Vector((-u.y, u.x)) * distance
        b = corner + Vector((-v.y, v.x)) * distance
        det = u.x * v.y - u.y * v.x
        if abs(det) < 1e-8:
            result.append((a + b) / 2)
        else:
            offset = b - a
            t = (offset.x * v.y - offset.y * v.x) / det
            result.append(a + u * t)
    return result


def _raised(scene, name, polygon, height, bevel, material):
    inner = _inset(polygon, bevel)
    outer = [Vector(point) for point in polygon]
    vertices, faces, rings = [], [], []
    n = len(polygon)
    for z, t in [(0.0004, 0), (height - bevel, 0)] + [
            (height - bevel + bevel * math.sin(math.pi * step / 8),
             1 - math.cos(math.pi * step / 8)) for step in range(1, 5)]:
        ring = []
        for source, inset in zip(outer, inner):
            point = source.lerp(inset, t)
            ring.append(len(vertices))
            vertices.append((point.x, point.y, z))
        if rings:
            for index in range(n):
                nxt = (index + 1) % n
                faces.append((rings[-1][index], rings[-1][nxt], ring[nxt], ring[index]))
        rings.append(ring)
    faces += [tuple(reversed(rings[0])), tuple(rings[-1])]
    obj = _mesh(scene, name, vertices, faces, material, make_uv=True)
    obj["AQ1_probe_geometry"] = "physically raised above Z=0; not an indentation"
    return obj


def _select(scene, objects, active):
    for obj in scene.objects:
        obj.select_set(False)
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    scene.view_layers[0].objects.active = active


def _export_cm(scene, path, objects):
    """Same measured cm-copy/unit basis; no source transforms are applied."""
    copies = []
    source_units = scene.unit_settings.scale_length
    try:
        for source in objects:
            copied = source.copy()
            copied.data = source.data.copy()
            copied.name = source.name + "_CM_EXPORT"
            copied.data.transform(Matrix.Scale(100, 4))
            copied.location = source.location * 100
            copied.scale = (1, 1, 1)
            copied.hide_render = False
            scene.collection.objects.link(copied)
            copied.hide_set(False)
            copies.append(copied)
        scene.unit_settings.scale_length = .01
        _select(scene, copies, copies[0])
        bpy.context.view_layer.update()
        bpy.ops.export_scene.fbx(
            filepath=str(path), use_selection=True, object_types={"MESH"},
            global_scale=1, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
            axis_forward="-Y", axis_up="Z", use_mesh_modifiers=True,
            mesh_smooth_type="FACE", use_tspace=True, bake_anim=False,
            path_mode="AUTO", embed_textures=False)
    finally:
        for copied in copies:
            mesh = copied.data
            bpy.data.objects.remove(copied, do_unlink=True)
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        scene.unit_settings.scale_length = source_units


def _normal_samples(objects, image):
    """Measure baked slope signs against actual upward-facing bevel normals."""
    pixels = list(image.pixels)
    width, height = image.size
    records = []
    for obj in objects:
        for face in obj.data.polygons:
            normal = face.normal
            if normal.z < .20 or abs(normal.y) < .20:
                continue
            center = sum((obj.data.vertices[index].co for index in face.vertices),
                         Vector()) / len(face.vertices)
            u, v = (center.x + .2) / .4, (center.y + .2) / .4
            x = max(0, min(width - 1, int(u * width)))
            y = max(0, min(height - 1, int(v * height)))
            rgba = pixels[4 * (y * width + x):4 * (y * width + x) + 4]
            baked = Vector(tuple(2 * channel - 1 for channel in rgba[:3]))
            if baked.length < .01:
                continue
            baked.normalize()
            agreement = normal.y * baked.y > 0
            angle = math.degrees(math.acos(max(-1, min(1, normal.dot(baked)))))
            records.append({"object": obj.name, "source_face": face.index,
                            "source_xy_m": [center.x, center.y], "uv": [u, v],
                            "raised_surface_normal_xyz": list(normal),
                            "baked_normal_xyz": list(baked), "green": rgba[1],
                            "green_sign_matches_source": agreement,
                            "angular_error_degrees": angle})
    greens = pixels[1::4]
    slopes = [record for record in records if record["angular_error_degrees"] < 18]
    return {"pixel_green_min": min(greens), "pixel_green_max": max(greens),
            "sample_count": len(records),
            "green_sign_match_count": sum(record["green_sign_matches_source"] for record in records),
            "samples_within_18_degrees": len(slopes),
            "interpretation": "Measured bake diagnostic; not engine orientation acceptance",
            "samples": records}


def build_probe(outdir, texture_size=1024):
    """Bake a known raised shape and return its executed probe manifest."""
    if texture_size not in (256, 1024):
        raise ValueError("Use 256 for a quick probe or 1024 for the reference bake")
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    names = ["SM_AQ1_NormalProbe_Low.fbx", "SM_AQ1_NormalProbe_Control.fbx",
             "T_AQ1_NormalProbe_PosY.png", "AQ1_NormalProbe_Source.blend",
             "blender_geometry_control.png", "blender_pos_y_normal.png", "probe_manifest.json"]
    if any((outdir / name).exists() for name in names):
        raise FileExistsError("Use a fresh probe output directory; retained evidence is never overwritten")
    scene = bpy.data.scenes.new("AQ1_AsymmetricRaisedNormalProbe")
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    window = bpy.context.window
    previous_scene = window.scene if window else None
    if window:
        window.scene = scene
    try:
        with bpy.context.temp_override(scene=scene, view_layer=scene.view_layers[0]):
            scene.render.engine = "CYCLES"
            scene.cycles.samples = 32
            scene.cycles.use_denoising = False
            scene.render.resolution_x = scene.render.resolution_y = 768
            scene.render.resolution_percentage = 100
            scene.render.image_settings.file_format = "PNG"
            scene.view_settings.view_transform = "Standard"
            scene.view_settings.exposure = 0
            scene.view_settings.gamma = 1
            world = bpy.data.worlds.new("AQ1_NormalProbe_World")
            world.use_nodes = True
            world.node_tree.nodes["Background"].inputs["Color"].default_value = (.08, .08, .08, 1)
            world.node_tree.nodes["Background"].inputs["Strength"].default_value = .3
            scene.world = world
            clay = bpy.data.materials.new("M_AQ1_NormalProbe_Clay")
            clay.use_nodes = True
            shader = clay.node_tree.nodes.get("Principled BSDF")
            shader.inputs["Base Color"].default_value = (.42, .42, .42, 1)
            shader.inputs["Roughness"].default_value = .72
            shader.inputs["Metallic"].default_value = 0
            target = clay.copy()
            target.name = "M_AQ1_NormalProbe_Baked"
            plane_vertices = [(-.2, -.2, 0), (.2, -.2, 0), (.2, .2, 0), (-.2, .2, 0)]
            low = _mesh(scene, "AQ1_NormalProbe_Low", plane_vertices, [(0, 1, 2, 3)],
                        target, make_uv=True)
            base = _mesh(scene, "AQ1_NormalProbe_ControlBase",
                         [(x, y, .0002) for x, y, _ in plane_vertices],
                         [(0, 1, 2, 3)], clay, make_uv=True)
            chevron_points = [(-.130, -.105), (-.095, -.130), (.030, .035),
                              (.122, -.018), (.142, .022), (.018, .110)]
            marker_points = [(-.150, .105), (-.110, .105), (-.150, .155)]
            chevron = _raised(scene, "AQ1_NormalProbe_RaisedChevron",
                               chevron_points, .026, .008, clay)
            marker = _raised(scene, "AQ1_NormalProbe_UpperLeftMarker",
                             marker_points, .014, .004, clay)
            highs = [base, chevron, marker]
            image = bpy.data.images.new("T_AQ1_NormalProbe_PosY", width=texture_size,
                                        height=texture_size, alpha=True, float_buffer=False)
            image.colorspace_settings.name = "Non-Color"
            image.generated_color = (.5, .5, 1, 1)
            image.filepath_raw = str(outdir / names[2])
            image.file_format = "PNG"
            image_node = target.node_tree.nodes.new("ShaderNodeTexImage")
            image_node.image = image
            target.node_tree.nodes.active = image_node
            bake = scene.render.bake
            bake.use_selected_to_active = True
            bake.use_cage = False
            bake.cage_extrusion = .040
            bake.max_ray_distance = .090
            bake.use_clear = True
            bake.margin = 4
            bake.normal_space = "TANGENT"
            bake.normal_r, bake.normal_g, bake.normal_b = "POS_X", "POS_Y", "POS_Z"
            _select(scene, highs + [low], low)
            bpy.ops.object.bake(type="NORMAL")
            image.save()
            samples = _normal_samples([chevron, marker], image)
            if not (samples["pixel_green_min"] < .4 and samples["pixel_green_max"] > .6):
                raise RuntimeError("Actual bake did not capture opposing raised bevel slopes")
            normal = target.node_tree.nodes.new("ShaderNodeNormalMap")
            normal.space = "TANGENT"
            normal.uv_map = "UV0_SourceXY"
            target.node_tree.links.new(image_node.outputs["Color"], normal.inputs["Color"])
            target.node_tree.links.new(normal.outputs["Normal"],
                                       target.node_tree.nodes.get("Principled BSDF").inputs["Normal"])
            camera_data = bpy.data.cameras.new("AQ1_NormalProbe_Camera")
            camera = bpy.data.objects.new("AQ1_NormalProbe_Camera", camera_data)
            scene.collection.objects.link(camera)
            camera.location = (0, 0, 1)
            camera.rotation_euler = (0, 0, 0)
            camera_data.type = "ORTHO"
            camera_data.ortho_scale = .45
            scene.camera = camera
            light_data = bpy.data.lights.new("AQ1_NormalProbe_Key", "SUN")
            light_data.energy = 2.2
            light_data.angle = math.radians(2)
            if hasattr(light_data, "use_shadow"):
                light_data.use_shadow = False
            light = bpy.data.objects.new("AQ1_NormalProbe_Key", light_data)
            scene.collection.objects.link(light)
            light_from = Vector((-.4, -.6, .8)).normalized()
            light.rotation_euler = (-light_from).to_track_quat("-Z", "Y").to_euler()
            low.hide_render = True
            scene.render.filepath = str(outdir / names[4])
            bpy.ops.render.render(write_still=True, scene=scene.name)
            low.hide_render = False
            for obj in highs:
                obj.hide_render = True
            scene.render.filepath = str(outdir / names[5])
            bpy.ops.render.render(write_still=True, scene=scene.name)
            _export_cm(scene, outdir / names[0], [low])
            _export_cm(scene, outdir / names[1], highs)
            image.pack()
            bpy.data.libraries.write(str(outdir / names[3]), {scene},
                                      path_remap="RELATIVE_ALL", fake_user=True, compress=True)
            geometry = {}
            for obj in [low] + highs:
                obj.data.calc_loop_triangles()
                geometry[obj.name] = {
                    "vertices": len(obj.data.vertices), "triangles": len(obj.data.loop_triangles),
                    "bounds_min_m": [min(v.co[axis] for v in obj.data.vertices) for axis in range(3)],
                    "bounds_max_m": [max(v.co[axis] for v in obj.data.vertices) for axis in range(3)]}
            manifest = {
                "status": "BLENDER_BAKED_RENDERED_EXPORTED; UNREAL_PARITY_PENDING",
                "blender_version": bpy.app.version_string, "source_script_sha256": _sha(__file__),
                "source": "original procedural known-asymmetric raised test geometry; no external asset",
                "source_unit_m": 1, "plane_extent_m": [.4, .4], "plane_normal": "+Z",
                "uv0": {"u": "+X", "v": "+Y", "domain": "entire square maps (0,0)..(1,1)"},
                "chevron_outline_xy_m": chevron_points, "chevron_height_m": .026,
                "marker_outline_xy_m": marker_points, "marker_height_m": .014,
                "geometry": geometry,
                "bake": {"type": "actual Cycles selected-to-active tangent normal bake",
                         "size_px": texture_size, "space": "TANGENT", "channels": ["+X", "+Y", "+Z"],
                         "colorspace": "Non-Color", "cage_extrusion_m": .040,
                         "max_ray_distance_m": .090, "margin_px": 4},
                "normal_measurements": samples,
                "render": {"camera": "orthographic +Z, screen right +X and screen up +Y",
                           "light_source_direction_xyz": list(light_from),
                           "sun_energy": 2.2, "shadows": "disabled on meshes and light when API supports it",
                           "surface": "same diffuse gray roughness .72, metallic 0",
                           "comparison_limit": "normal map reproduces slopes, not geometric height/parallax"},
                "fbx": {"mesh_coordinate_units": "centimeters from independent 100x copies",
                        "scene_unit_m": .01, "global_scale": 1, "axis_forward": "-Y", "axis_up": "Z",
                        "apply_scale_options": "FBX_SCALE_UNITS", "use_tspace": True,
                        "intended_engine_path": "legacy static, import normals, compute MikkTSpace tangents; retain UV0"},
                "unreal_review": "pending actual geometry/control/keep-green/flip-green capture; do not infer pass",
                "files": {name: _sha(outdir / name) for name in names[:-1]}}
            (outdir / names[-1]).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            print("AQ1_NORMAL_PROBE_EXECUTED " + str(outdir / names[-1]), flush=True)
            return manifest
    finally:
        if window and previous_scene:
            window.scene = previous_scene


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--texture-size", type=int, choices=(256, 1024), default=1024)
    args = parser.parse_args(arguments)
    build_probe(args.output, args.texture_size)

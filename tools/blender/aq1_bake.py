"""Bake an isolated AQ1 candidate; never modifies source parts or canonical outputs.

Call bake_candidate(parts, armature, output_directory) inside Blender. The returned
mesh is an independent, skinned export copy. High detail copies are retained in a
hidden collection. This is a real Cycles bake, not generated placeholder maps.
"""
from __future__ import annotations

import hashlib
import json
import math
from array import array
from pathlib import Path

import bpy
import numpy as np


UID = "wc_u_human_guardian"


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _source_state(parts, armature):
    return _digest({
        "parts": [{"name": ob.name, "matrix": [list(r) for r in ob.matrix_world],
                   "vertices": [list(v.co) for v in ob.data.vertices],
                   "faces": [list(p.vertices) for p in ob.data.polygons],
                   "weights": [[(g.group, g.weight) for g in v.groups] for v in ob.data.vertices],
                   "materials": [m.name if m else None for m in ob.data.materials],
                   "uv": [[list(v.uv) for v in layer.data] for layer in ob.data.uv_layers]}
                  for ob in parts],
        "rest": {b.name: {"matrix": [list(r) for r in b.matrix_local],
                          "parent": b.parent.name if b.parent else None}
                 for b in armature.data.bones},
        "actions": {a.name: [[f.data_path, f.array_index,
                              [[list(k.co), list(k.handle_left), list(k.handle_right), k.interpolation]
                               for k in f.keyframe_points]]
                             for layer in a.layers for strip in layer.strips
                             for bag in strip.channelbags for f in bag.fcurves]
                    for a in bpy.data.actions},
    })


def _select(objects, active):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = active


def _operator(operator, **kwargs):
    """Filter optional parameters against the actual installed Blender RNA."""
    supported = operator.get_rna_type().properties.keys()
    actual = {key: value for key, value in kwargs.items() if key in supported}
    operator(**actual)
    return actual


def _new_collection(name):
    if bpy.data.collections.get(name):
        raise RuntimeError(f"Candidate bake collection already exists; preserve or use a fresh scene: {name}")
    result = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(result)
    return result


def _copy_mesh(source, name, collection):
    result = source.copy()
    result.data = source.data.copy()
    result.name = name
    result.animation_data_clear()
    collection.objects.link(result)
    world = source.matrix_world.copy()
    result.parent = None
    result.matrix_world = world
    result.hide_render = False
    result.hide_viewport = False
    result.hide_set(False)
    if name.startswith('AQ1_LOW_'):
        from aq1_runtime_geometry import optimize_export_copy
        result['aq1_runtime_geometry_record'] = json.dumps(optimize_export_copy(source, result))
    for modifier in list(result.modifiers):
        if modifier.type == "ARMATURE" or not modifier.show_render:
            result.modifiers.remove(modifier)
        else:
            _select([result], result)
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    return result


def _unwrap(part):
    # The AQ1 authoring helpers deliberately use an XZ projection as a temporary
    # UV field. Nonzero area does not prove an unwrap: front/back can coincide.
    # Re-unwrap only the independent export copy, retaining all original UV data.
    previous_layers = [layer.name for layer in part.data.uv_layers]
    for layer in list(part.data.uv_layers):
        part.data.uv_layers.remove(layer)
    part.data.uv_layers.new(name="AQ1_UV")
    _select([part], part)
    quiet_tube = any(key in part.name for key in ('pauldron_rim', 'hair_tie'))
    if quiet_tube:
        for edge in part.data.edges:
            edge.use_seam = True
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    angle = 25 if 'pauldron_rim' in part.name else 66
    if quiet_tube:
        actual = _operator(bpy.ops.uv.unwrap, method='ANGLE_BASED', margin=.002)
    else:
        actual = _operator(bpy.ops.uv.smart_project, angle_limit=math.radians(angle),
                           island_margin=0.012, area_weight=0.0,
                           correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return {"method": "seamed quiet tube faces" if quiet_tube else "semantic-part angle-based smart-project unwrap", "operator": actual,
            "replaced_export_copy_uv_layers": previous_layers,
            "reason": "authoring projection is provisional and may overlap front/back",
            "source_uvs_unchanged": True}


def _validate_uv(mesh, size):
    """Detect packed triangle-interior overlaps at the actual atlas resolution.

    This is a measured sampled check, not a proof against subpixel intersection.
    Shared edges are excluded using strict barycentric interior tests.
    """
    mesh.data.calc_loop_triangles()
    uv = mesh.data.uv_layers.active
    owners = array("i", [-1])*(size*size)
    overlap = bytearray(size*size)
    overlap_parts = {}
    degenerate = 0
    subpixel = 0
    out_of_bounds = 0
    for triangle_id, triangle in enumerate(mesh.data.loop_triangles):
        coordinates = [tuple(uv.data[index].uv) for index in triangle.loops]
        if not all(math.isfinite(value) for pair in coordinates for value in pair):
            raise RuntimeError("Packed UV coordinates contain a nonfinite value")
        if any(value < -1e-6 or value > 1+1e-6 for pair in coordinates for value in pair):
            out_of_bounds += 1
        pixels = [(x*size, y*size) for x, y in coordinates]
        a, b, c = pixels
        v0, v1 = (b[0]-a[0], b[1]-a[1]), (c[0]-a[0], c[1]-a[1])
        denominator = v0[0]*v1[1] - v0[1]*v1[0]
        if abs(denominator) < 1e-10:
            degenerate += 1
            continue
        left = max(0, math.floor(min(point[0] for point in pixels)))
        right = min(size-1, math.ceil(max(point[0] for point in pixels)))
        bottom = max(0, math.floor(min(point[1] for point in pixels)))
        top = min(size-1, math.ceil(max(point[1] for point in pixels)))
        if left > right or bottom > top:
            subpixel += 1
            continue
        hit = False
        for y in range(bottom, top+1):
            dy = y+.5-a[1]
            for x in range(left, right+1):
                dx = x+.5-a[0]
                u = (dx*v1[1]-dy*v1[0])/denominator
                v = (v0[0]*dy-v0[1]*dx)/denominator
                if u > 1e-7 and v > 1e-7 and u+v < 1-1e-7:
                    hit = True
                    pixel = y*size+x
                    if owners[pixel] >= 0:
                        overlap[pixel] = 1
                        marker = mesh.data.attributes.get('aq1_semantic_part')
                        if marker:
                            identity = str(marker.data[triangle.polygon_index].value)
                            overlap_parts[identity] = overlap_parts.get(identity, 0)+1
                    owners[pixel] = triangle_id
        if not hit:
            subpixel += 1
    coverage = sum(owner >= 0 for owner in owners)
    overlap_count = sum(overlap)
    result = {"method": "triangle interiors sampled at atlas pixel centers; excludes shared edges",
              "resolution": size, "covered_texels": coverage,
              "coverage_fraction": coverage/(size*size),
              "overlapping_texels": overlap_count, "overlap_semantic_indices": overlap_parts, "out_of_bounds_triangles": out_of_bounds,
              "zero_area_uv_triangles": degenerate, "triangles_without_pixel_center": subpixel,
              "limitation": "subpixel overlaps and distortion still require visual UV inspection"}
    if coverage == 0 or out_of_bounds or overlap_count:
        raise RuntimeError("Packed candidate UV validation failed: " + json.dumps(result))
    return result


def _quilt(material):
    """Add restrained procedural diagonal seams to the copied ivory material."""
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not shader or shader.inputs["Normal"].is_linked:
        return False
    tex = nodes.new("ShaderNodeTexCoord")
    waves = []
    for angle in (math.pi / 4, -math.pi / 4):
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Rotation"].default_value[2] = angle
        links.new(tex.outputs["Generated"], mapping.inputs["Vector"])
        wave = nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        wave.inputs["Scale"].default_value = 7.0
        wave.inputs["Distortion"].default_value = 0.0
        links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
        seam = nodes.new("ShaderNodeMath")
        seam.operation = "GREATER_THAN"
        seam.inputs[1].default_value = 0.93
        links.new(wave.outputs["Fac"], seam.inputs[0])
        waves.append(seam)
    crossing = nodes.new("ShaderNodeMath")
    crossing.operation = "MAXIMUM"
    links.new(waves[0].outputs[0], crossing.inputs[0])
    links.new(waves[1].outputs[0], crossing.inputs[1])
    bump = nodes.new("ShaderNodeBump")
    bump.invert = True
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.00065
    links.new(crossing.outputs[0], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return True


def _emission_channel(materials, socket_name):
    """Temporarily expose a copied material input for an unlit scalar/color bake."""
    restore = []
    for material in materials:
        nodes, links = material.node_tree.nodes, material.node_tree.links
        shader = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
        output = next(n for n in nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        old = [(link.from_socket, link.to_socket) for link in output.inputs["Surface"].links]
        emission = nodes.new("ShaderNodeEmission")
        source = shader.inputs[socket_name]
        if source.is_linked:
            links.new(source.links[0].from_socket, emission.inputs["Color"])
        else:
            value = source.default_value
            emission.inputs["Color"].default_value = tuple(value) if socket_name == "Base Color" else (value, value, value, 1)
        links.new(emission.outputs[0], output.inputs["Surface"])
        restore.append((material, emission, old))
    return restore


def _restore_materials(saved):
    for material, emission, old in saved:
        material.node_tree.nodes.remove(emission)
        for source, target in old:
            material.node_tree.links.new(source, target)


def _image(name, size, color_space):
    # UE treats 16-bit source formats as linear before its texture sRGB flag.
    # Color bakes therefore use an 8-bit sRGB buffer; data maps stay linear.
    image = bpy.data.images.new(name, width=size, height=size, alpha=False, float_buffer=color_space != 'sRGB')
    image.colorspace_settings.name = color_space
    return image


def _pixels(image):
    pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(pixels)
    return pixels.reshape((-1, 4))


def _save_image(image, path):
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Bake produced no saved image: {path}")
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "png_bit_depth": path.read_bytes()[24],
            "width": image.size[0], "height": image.size[1],
            "color_space": image.colorspace_settings.name}


def _runtime_material(images):
    material = bpy.data.materials.new("M_AQ1_Ada_Baked")
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    samples = {}
    for key, image in images.items():
        node = nodes.new("ShaderNodeTexImage")
        node.image = image
        node.label = key
        samples[key] = node
    links.new(samples["BaseColor"].outputs["Color"], shader.inputs["Base Color"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.space = "TANGENT"
    links.new(samples["Normal"].outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    channels = nodes.new("ShaderNodeSeparateColor")
    channels.mode = "RGB"
    links.new(samples["ORM"].outputs["Color"], channels.inputs["Color"])
    links.new(channels.outputs["Green"], shader.inputs["Roughness"])
    links.new(channels.outputs["Blue"], shader.inputs["Metallic"])
    return material


def bake_candidate(parts, armature, out_dir, texture_size=1024):
    """Return (independent export mesh, measured bake metadata).

    Run in an isolated saved candidate. Existing target maps or bake collections
    cause an error. Higher-resolution comparison maps do not approve a budget.
    """
    parts = list(parts)
    if not parts or any(p.type != "MESH" for p in parts) or armature.type != "ARMATURE":
        raise ValueError("Explicit semantic mesh parts and an armature are required")
    if texture_size not in (1024, 2048):
        raise ValueError("AQ1 supports 1K baseline or explicit 2K comparison only")
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        raise RuntimeError("Enter Object mode before baking the candidate")
    out_dir = Path(out_dir).resolve()
    canonical = Path(__file__).resolve().parents[2] / "exports" / "heroes" / UID
    if out_dir == canonical or canonical in out_dir.parents:
        raise ValueError("Use an isolated candidate path, not canonical hero exports")
    targets = {key: out_dir / f"T_{UID}_{key}.png" for key in ("BaseColor", "Normal", "ORM")}
    if any(p.exists() for p in targets.values()):
        raise RuntimeError("Bake targets already exist; preserve evidence and choose a fresh output directory")
    for part in parts:
        if not part.data.materials or any(m is None or not m.use_nodes or not any(
                n.type == "BSDF_PRINCIPLED" for n in m.node_tree.nodes) for m in part.data.materials):
            raise ValueError(f"Part needs valid Principled source materials: {part.name}")
    before = _source_state(parts, armature)
    scene = bpy.context.scene
    saved_selection, saved_active = list(bpy.context.selected_objects), bpy.context.view_layer.objects.active
    saved_engine, saved_samples = scene.render.engine, scene.cycles.samples
    saved_render_visibility = {ob: ob.hide_render for ob in scene.objects if ob.type == "MESH"}
    bake = scene.render.bake
    bake_keys = ("use_selected_to_active", "cage_extrusion", "max_ray_distance", "margin",
                 "use_clear", "normal_space", "normal_r", "normal_g", "normal_b",
                 "use_pass_direct", "use_pass_indirect", "use_pass_color")
    saved_bake = {key: getattr(bake, key) for key in bake_keys}
    low_collection = _new_collection("AQ1_BAKED_EXPORT")
    high_collection = _new_collection("AQ1_BAKE_DETAIL")
    lows, highs, high_materials, uv_records, details = [], [], {}, [], []
    geometry_records = []
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        for index, source in enumerate(parts):
            low = _copy_mesh(source, "AQ1_LOW_" + source.name, low_collection)
            geometry_records.append(json.loads(low['aq1_runtime_geometry_record']))
            uv_records.append({"part": source.name, "uv": _unwrap(low)})
            marker = low.data.attributes.new("aq1_semantic_part", "INT", "FACE")
            for value in marker.data:
                value.value = index
            lows.append(low)
            high = _copy_mesh(source, "AQ1_DETAIL_" + source.name, high_collection)
            for slot in high.material_slots:
                original = slot.material
                if original.name not in high_materials:
                    copied = original.copy()
                    copied.name = "AQ1_DETAIL_" + original.name
                    high_materials[original.name] = copied
                    if "ivory" in original.name.lower() or "cloth" in original.name.lower():
                        if _quilt(copied):
                            details.append({"material": original.name,
                                            "detail": "procedural diagonal seam bump baked to tangent normal; not a sculpt bake",
                                            "bump_distance_m": 0.00065})
                slot.material = high_materials[original.name]
            name = source.name.lower()
            if any(key in name for key in ("armor_", "bracer", "shield_shell", "sword_blade", "sword_guard")):
                bevel = high.modifiers.new("AQ1_LocalEdgeDetail", "BEVEL")
                bevel.width = 0.0008
                bevel.segments = 2
                bevel.limit_method = "ANGLE"
                bevel.angle_limit = math.radians(35)
                bevel.use_clamp_overlap = True
                details.append({"part": source.name, "detail": "independent high-copy angle-limited bevel",
                                "width_m": bevel.width, "segments": bevel.segments})
            highs.append(high)
        _select(lows, lows[0])
        bpy.ops.object.join()
        low = bpy.context.object
        low.name = "SK_AQ1_" + UID
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.select_all(action="SELECT")
        bpy.ops.uv.average_islands_scale()
        bpy.ops.object.mode_set(mode="OBJECT")
        # Reserve more texels for readable face and emblem surfaces before packing.
        uv = low.data.uv_layers.active
        marker = low.data.attributes["aq1_semantic_part"]
        for index, source in enumerate(parts):
            if not any(key in source.name.lower() for key in ("head", "face", "shield_crest")):
                continue
            loop_ids = [i for polygon in low.data.polygons if marker.data[polygon.index].value == index
                        for i in polygon.loop_indices]
            if loop_ids:
                center = sum((uv.data[i].uv.copy() for i in loop_ids), uv.data[loop_ids[0]].uv * 0) / len(loop_ids)
                for i in loop_ids:
                    uv.data[i].uv = center + (uv.data[i].uv - center) * 1.3
        bpy.ops.object.mode_set(mode="EDIT")
        packing = _operator(bpy.ops.uv.pack_islands, rotate=True, scale=True,
                            margin_method="SCALED", margin=0.003)
        bpy.ops.object.mode_set(mode="OBJECT")
        triangulate = low.modifiers.new("AQ1_ConsistentBakeTriangles", "TRIANGULATE")
        bpy.ops.object.modifier_apply(modifier=triangulate.name)
        low.data.calc_loop_triangles()
        if len(low.data.loop_triangles)>25000:
            (out_dir/'geometry-budget-failure.json').write_text(json.dumps({'triangles':len(low.data.loop_triangles),'parts':geometry_records},indent=2))
            raise RuntimeError('Export copy exceeds AQ1 25k experiment; inspect geometry before baking')
        try:
            uv_validation = _validate_uv(low, texture_size)
        except RuntimeError as exc:
            (out_dir/'uv-failure.json').write_text(json.dumps({'error':str(exc),'semantic_parts':{str(i):ob.name for i,ob in enumerate(parts)}},indent=2))
            raise
        target_material = bpy.data.materials.new("M_AQ1_BakeTarget")
        target_material.use_nodes = True
        low.data.materials.clear()
        low.data.materials.append(target_material)
        for face in low.data.polygons:
            face.material_index = 0
        image_node = target_material.node_tree.nodes.new("ShaderNodeTexImage")
        target_material.node_tree.nodes.active = image_node
        scene.render.engine = "CYCLES"
        scene.cycles.samples = 16
        bake.use_selected_to_active = True
        bake.cage_extrusion = 0.003
        bake.max_ray_distance = 0.006
        bake.margin = 8 if texture_size == 1024 else 16
        bake.use_clear = True
        bake.normal_space = "TANGENT"
        bake.normal_r, bake.normal_g, bake.normal_b = "POS_X", "POS_Y", "POS_Z"
        images = {key: _image(f"AQ1_{key}_{texture_size}", texture_size,
                             "sRGB" if key == "BaseColor" else "Non-Color")
                  for key in ("BaseColor", "Normal", "AO", "Roughness", "Metallic")}
        # The editable source overlaps the independent bake copies exactly.
        # Exclude it and unrelated scene geometry from the ambient-occlusion bake.
        bake_objects = set(highs + [low])
        for ob in scene.objects:
            if ob.type == "MESH" and ob not in bake_objects:
                ob.hide_render = True
        _select(highs + [low], low)
        channels = {"BaseColor": "Base Color", "Roughness": "Roughness", "Metallic": "Metallic"}
        for key, image in images.items():
            print('AQ1_BAKE_CHANNEL_START',key,flush=True)
            image_node.image = image
            saved_materials = _emission_channel(list(high_materials.values()), channels[key]) if key in channels else []
            try:
                bpy.ops.object.bake(type="EMIT" if key in channels else ("NORMAL" if key == "Normal" else "AO"))
            finally:
                _restore_materials(saved_materials)
            print('AQ1_BAKE_CHANNEL_DONE',key,flush=True)
        pixels = {key: _pixels(image) for key, image in images.items()}
        normal = pixels["Normal"]
        covered = normal[:, 2] > 0.1
        if not np.any(covered):
            raise RuntimeError("Normal bake contains no covered surface texels")
        normal_xy = normal[covered, :2]
        variation = float(np.max(np.ptp(normal_xy, axis=0)))
        nonflat = int(np.count_nonzero(np.max(np.abs(normal_xy - 0.5), axis=1) > 0.01))
        if variation < 0.015 or nonflat < 64:
            raise RuntimeError(f"Normal bake is effectively flat: variation={variation}, changed_texels={nonflat}")
        packed = np.ones_like(normal)
        for index, key in enumerate(("AO", "Roughness", "Metallic")):
            packed[:, index] = np.clip(pixels[key][:, 0], 0, 1)
        orm = _image(f"AQ1_ORM_{texture_size}", texture_size, "Non-Color")
        orm.pixels.foreach_set(packed.ravel())
        orm.update()
        images["ORM"] = orm
        files = {key: _save_image(images[key], path) for key, path in targets.items()}
        runtime = _runtime_material({key: images[key] for key in targets})
        low.data.materials.clear()
        low.data.materials.append(runtime)
        modifier = low.modifiers.new("AQ1_Armature", "ARMATURE")
        modifier.object = armature
        low.parent = armature
        low.matrix_parent_inverse = armature.matrix_world.inverted()
        if _source_state(parts, armature) != before:
            raise RuntimeError("Candidate bake unexpectedly changed source geometry, rig or actions")
        metadata = {
            "status": "actual_cycles_bake_completed_pending_visual_and_Unreal_review",
            "blender_version": bpy.app.version_string, "source_preservation_sha256": before,
            "mesh": low.name, "triangles": len(low.data.loop_triangles), "material_slots": 1,
            "size": texture_size, "uv_parts": uv_records, "packing": packing,
            "uv_validation": uv_validation,
            "runtime_geometry": geometry_records,
            "semantic_parts": {str(i): ob.name for i, ob in enumerate(parts)},
            "texel_priority": "head/face/crest islands scaled 1.3 before global packing",
            "high_detail": details, "organic_subdivision": "none; shaped source surfaces retained",
            "bake": {"engine": "Cycles", "samples": 16, "selected_to_active": True,
                     "cage_extrusion_m": 0.003, "max_ray_distance_m": 0.006,
                     "normal_space": "tangent +Y, Blender basis; verify Unreal asymmetric test",
                     "base_color": "unlit source Principled input baked as emission",
                     "ORM": "linear R=actual AO bake G=roughness input bake B=metallic input bake"},
            "normal_measurements": {"covered_texels": int(np.count_nonzero(covered)),
                                    "xy_peak_to_peak": variation, "nonflat_texels": nonflat},
            "files": files,
            "pending": ["map/UV visual inspection", "projection artifacts and normal orientation",
                        "1K gameplay readability", "continuous seven-clip deformation", "Unreal material parity"],
        }
        (out_dir / "bake-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        return low, metadata
    finally:
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        high_collection.hide_render = True
        high_collection.hide_viewport = True
        for ob, hidden in saved_render_visibility.items():
            if ob.name in bpy.data.objects:
                ob.hide_render = hidden
        for key, value in saved_bake.items():
            setattr(bake, key, value)
        scene.render.engine, scene.cycles.samples = saved_engine, saved_samples
        bpy.ops.object.select_all(action="DESELECT")
        for ob in saved_selection:
            if ob.name in bpy.data.objects:
                ob.select_set(True)
        bpy.context.view_layer.objects.active = saved_active

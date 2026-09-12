"""Conservative semantic thickness allocation for independent AQ1 export copies.

Call optimize_export_copy(source, copied) before the copy's modifier-apply loop.
The authored armor surface remains intact. Only a copied Solidify's hidden inner
duplicate is replaced with a perimeter strip; hanging cloth keeps both sides.
"""
from __future__ import annotations

import hashlib
import json
import math

import bmesh
import bpy


ARMOR = {
    "armor_chest": "Breastplate inward duplicate lies against the fitted torso; keep outer plate and edge thickness",
    "armor_back": "Backplate inward duplicate lies against the fitted torso; keep outer plate and edge thickness",
    "armor_pauldron_l": "Pauldron inward duplicate is backed by its coat sleeve; retain lower rim thickness",
    "armor_pauldron_r": "Pauldron inward duplicate is backed by its coat sleeve; retain lower rim thickness",
    "boot_toe_plate_l": "Toe-cap inward duplicate lies against the continuous leather boot; retain visible roof and perimeter thickness",
    "boot_toe_plate_r": "Toe-cap inward duplicate lies against the continuous leather boot; retain visible roof and perimeter thickness",
}
DOUBLE_SIDED_CLOTH = {"coat_skirt", "tabard_front", "tabard_back"}


def _signature(obj):
    return hashlib.sha256(json.dumps({
        "vertices": [list(vertex.co) for vertex in obj.data.vertices],
        "faces": [list(face.vertices) for face in obj.data.polygons],
        "weights": [[(group.group, group.weight) for group in vertex.groups]
                    for vertex in obj.data.vertices],
        "uv": [[list(loop.uv) for loop in layer.data] for layer in obj.data.uv_layers],
        "modifiers": [(modifier.name, modifier.type, modifier.show_viewport, modifier.show_render)
                      for modifier in obj.modifiers],
    }, sort_keys=True).encode()).hexdigest()


def _evaluated_stats(obj):
    """Read the actual modifier result, with skinning excluded only on this copy."""
    armatures = [(modifier, modifier.show_viewport) for modifier in obj.modifiers
                 if modifier.type == "ARMATURE"]
    for modifier, _ in armatures:
        modifier.show_viewport = False
    try:
        bpy.context.view_layer.update()
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            return {"vertices": len(mesh.vertices), "triangles": len(mesh.loop_triangles),
                    "faces": len(mesh.polygons)}
        finally:
            evaluated.to_mesh_clear()
    finally:
        for modifier, enabled in armatures:
            modifier.show_viewport = enabled


def _boundary_thickness(copied, modifier):
    if abs(modifier.offset + 1) > 1e-6 or modifier.thickness <= 0:
        raise RuntimeError("Only the reviewed inward, positive-thickness AQ1 shell is supported")
    if modifier.vertex_group or modifier.use_flip_normals:
        raise RuntimeError("Weighted or flipped thickness requires a separate semantic review")
    if not modifier.use_rim:
        raise RuntimeError("Source thickness has no rim; do not infer a new construction")
    bm = bmesh.new()
    bm.from_mesh(copied.data)
    bm.normal_update()
    original_faces = list(bm.faces)
    boundaries = [edge for edge in bm.edges if edge.is_boundary]
    if not boundaries or any(len(edge.link_faces) > 2 for edge in bm.edges):
        bm.free()
        raise RuntimeError("Expected manifold open armor patch with an explicit boundary")
    # These are geometric perimeter edges, not component indices or vertex-count
    # selectors. Every authored face remains; source objects are never traversed
    # for destructive operations.
    boundary_vertices = {vertex for edge in boundaries for vertex in edge.verts}
    deform = bm.verts.layers.deform.active
    inner = {}
    for vertex in boundary_vertices:
        duplicate = bm.verts.new(vertex.co - vertex.normal * modifier.thickness)
        if deform:
            for group, weight in vertex[deform].items():
                duplicate[deform][group] = weight
        inner[vertex] = duplicate
    for edge in boundaries:
        loop = next(loop for loop in edge.link_faces[0].loops if loop.edge == edge)
        a, b = loop.vert, loop.link_loop_next.vert
        face = bm.faces.new((b, a, inner[a], inner[b]))
        face.material_index = loop.face.material_index
        face.smooth = False
    if not all(face.is_valid for face in original_faces):
        bm.free()
        raise RuntimeError("Export allocation unexpectedly invalidated an authored armor face")
    bm.to_mesh(copied.data)
    bm.free()
    copied.data.update()
    record = {"modifier": modifier.name, "thickness_m": modifier.thickness,
              "authored_faces_retained": len(original_faces),
              "perimeter_edges": len(boundaries), "added_perimeter_vertices": len(inner),
              "rim_faces_added": len(boundaries),
              "inner_surface": "omitted only on this export copy; physically backed by torso/sleeve",
              "new_rim_uv": "provisional; caller unwraps this copy before atlas bake",
              "normals": "authored winding preserved; no face orientation reversal"}
    copied.modifiers.remove(modifier)
    return record


def optimize_export_copy(source, copied):
    """Return measured allocation metadata; never touch an original/shared mesh.

    Hook after copying/linking, before applying modifiers or unwrapping. Call for
    AQ1_LOW_* only. Keep the original source as the high-detail bake donor when
    comparing its fuller inward shell or two-segment edge against this copy.
    """
    if source is copied or source.data is copied.data:
        raise ValueError("AQ1 runtime allocation requires independent object AND mesh data")
    if source.type != "MESH" or copied.type != "MESH":
        raise ValueError("AQ1 runtime allocation only accepts mesh copies")
    if not copied.name.startswith("AQ1_LOW_"):
        raise ValueError("AQ1 runtime allocation is limited to explicitly named low export copies")
    semantic = source.get("aq1_semantic_part", source.name)
    if not isinstance(semantic, str):
        semantic = source.name
    before_source = _signature(source)
    before = _evaluated_stats(copied)
    changes = []
    if semantic in ARMOR:
        shells = [modifier for modifier in copied.modifiers
                  if modifier.type == "SOLIDIFY" and modifier.show_render]
        if len(shells) != 1:
            raise RuntimeError("Expected exactly one reviewed inward shell for " + semantic)
        changes.append(_boundary_thickness(copied, shells[0]))
        # At the broad torso plates, one forged edge plane carries the silhouette;
        # finer rounding belongs in the separately baked source comparison.
        if semantic in {"armor_chest", "armor_back", "boot_toe_plate_l", "boot_toe_plate_r"}:
            for modifier in copied.modifiers:
                if modifier.type == "BEVEL" and modifier.show_render:
                    old = {"segments": modifier.segments, "width_m": modifier.width,
                           "limit_method": modifier.limit_method,
                           "angle_limit_degrees": math.degrees(modifier.angle_limit)}
                    modifier.segments = 1
                    modifier.limit_method = "ANGLE"
                    modifier.angle_limit = math.radians(35)
                    modifier.use_clamp_overlap = True
                    changes.append({"modifier": modifier.name, "before": old,
                                    "after": {"segments": 1, "width_m": modifier.width,
                                              "limit_method": "ANGLE", "angle_limit_degrees": 35},
                                    "reason": "single visible forged edge chamfer; broad plate contour retained"})
    after = _evaluated_stats(copied)
    after_source = _signature(source)
    if before_source != after_source:
        raise RuntimeError("Authored source changed during export-only allocation")
    if semantic in ARMOR and after["triangles"] >= before["triangles"]:
        raise RuntimeError("Semantic allocation did not reduce this armor copy; inspect actual modifier topology")
    reason = ARMOR.get(semantic, "No reviewed redundant armor shell; preserve complete surface and modifiers")
    if semantic in DOUBLE_SIDED_CLOTH:
        reason = "Keep the full skirt/tabard underside: it can be exposed by motion and must not be removed blindly"
    record = {"semantic_part": semantic, "strategy": reason, "changes": changes,
              "before_evaluated": before, "after_evaluated": after,
              "saved_triangles": before["triangles"] - after["triangles"],
              "source_sha256_before": before_source, "source_sha256_after": after_source,
              "source_unchanged": True, "visual_acceptance": "pending actual render and all seven clips",
              "budget_status": "measured per-copy cost only; caller verifies total 15k/25k comparison limits"}
    copied["aq1_runtime_geometry_strategy"] = reason
    return record

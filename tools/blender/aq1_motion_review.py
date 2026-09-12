"""Render and measure actual AQ1 motion without saving or promoting a .blend.

Run in a separate Blender process on an explicitly opened candidate. Quantitative
checks and contact sheets are evidence to review, not artistic approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "blender"))
from aq1_capture import setup, VIEWS
from refine_update_ada import invariants, use_clip

UID = "wc_u_human_guardian"
CLIPS = ("Idle", "Move", "Attack", "Active", "Hit", "Defeat", "Victory")


def _objects(collection_name=None):
    if collection_name:
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            raise RuntimeError("Requested collection is unavailable: " + collection_name)
        meshes = [ob for ob in collection.all_objects if ob.type == "MESH"]
        if not meshes:
            raise RuntimeError("Requested collection has no mesh")
        return meshes, collection_name
    for name in ("AQ1_BAKED_EXPORT", "AQ1_EDITABLE"):
        collection = bpy.data.collections.get(name)
        if collection:
            meshes = [ob for ob in collection.all_objects if ob.type == "MESH"]
            if meshes:
                return meshes, name
    baseline = bpy.data.objects.get("SK_" + UID)
    if baseline and baseline.type == "MESH":
        return [baseline], "canonical mesh in explicitly opened baseline scene"
    raise RuntimeError("No explicit AQ1 or Ada baseline mesh found")


def _world_vertices(ob, depsgraph):
    evaluated = ob.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        matrix = evaluated.matrix_world
        positions = [matrix @ vertex.co for vertex in mesh.vertices]
        group_names = {group.index: group.name for group in ob.vertex_groups}
        feet = {side: [] for side in ("l", "r")}
        for vertex, point in zip(mesh.vertices, positions):
            for side in feet:
                if any(group_names.get(group.group) in ("foot_"+side, "toe_"+side)
                       and group.weight > .5 for group in vertex.groups):
                    feet[side].append(point.z)
        return positions, feet
    finally:
        evaluated.to_mesh_clear()


def _semantic_parts():
    collection = bpy.data.collections.get("AQ1_EDITABLE")
    if not collection:
        return {}
    return {ob.get("aq1_semantic_part", ob.name): ob for ob in collection.all_objects
            if ob.type == "MESH"}


def _witness(semantic, name, depsgraph, cache):
    ob = semantic.get(name)
    if ob is None:
        return None
    if ob not in cache:
        cache[ob] = _world_vertices(ob, depsgraph)[0]
    return cache[ob]


def _mean(points):
    return sum(points, Vector((0, 0, 0))) / len(points)


def _rigid_axis(semantic, name, points, armature, hand):
    """Compare a measured equipment axis to its rest axis driven by the wrist."""
    ob = semantic.get(name)
    if ob is None or not points:
        return None
    rest = [ob.matrix_world @ vertex.co for vertex in ob.data.vertices]
    if len(rest) != len(points):
        return {"status": "unavailable: evaluated topology differs from named source",
                "source_vertices": len(rest), "evaluated_vertices": len(points)}
    axes = [max(p[i] for p in rest)-min(p[i] for p in rest) for i in range(3)]
    axis = max(range(3), key=lambda i: axes[i])
    if axes[axis] < 1e-7:
        return {"status": "unavailable: degenerate source axis"}
    order = sorted(range(len(rest)), key=lambda index: rest[index][axis])
    count = max(1, len(order)//12)
    first, last = order[:count], order[-count:]
    before = _mean([rest[i] for i in last])-_mean([rest[i] for i in first])
    after = _mean([points[i] for i in last])-_mean([points[i] for i in first])
    rest_matrix = armature.matrix_world @ armature.data.bones[hand].matrix_local
    pose_matrix = armature.matrix_world @ armature.pose.bones[hand].matrix
    expected = (pose_matrix @ rest_matrix.inverted()).to_3x3() @ before
    return {"status": "actual evaluated source-part endpoint centroids",
            "longitudinal_axis_world": list(after.normalized()),
            "length_m": after.length,
            "rest_axis_length_m": before.length,
            "wrist_relative_axis_error_degrees": math.degrees(expected.angle(after, 0.0))}


def _measure(meshes, armature, semantic, scene):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points, feet, cache = [], {"l": [], "r": []}, {}
    for mesh in meshes:
        vertices, support = _world_vertices(mesh, depsgraph)
        cache[mesh] = vertices
        points.extend(vertices)
        for side in feet:
            feet[side].extend(support[side])
    if not points or any(not math.isfinite(value) for point in points for value in point):
        raise RuntimeError("Motion produced empty or nonfinite evaluated geometry")
    lower = [min(point[i] for point in points) for i in range(3)]
    upper = [max(point[i] for point in points) for i in range(3)]
    projected = [world_to_camera_view(scene, scene.camera, Vector((x, y, z)))
                 for x in (lower[0], upper[0]) for y in (lower[1], upper[1])
                 for z in (lower[2], upper[2])]
    feet_min = {side: min(values) if values else None for side, values in feet.items()}
    available_feet = [value for value in feet_min.values() if value is not None]
    eyes = []
    for side in ("l", "r"):
        eye = _witness(semantic, "eye_white_"+side, depsgraph, cache)
        if eye:
            eyes.append(_mean(eye).z)
    shield = _witness(semantic, "shield_shell", depsgraph, cache)
    shield_max = max(point.z for point in shield) if shield else None
    grips = {}
    for name, hand in (("sword_grip", "hand_r"), ("hand_grip_r", "hand_r"), ("hand_grip_l", "hand_l")):
        vertices = _witness(semantic, name, depsgraph, cache)
        if vertices:
            center = _mean(vertices)
            wrist = armature.matrix_world @ armature.pose.bones[hand].head
            grips[name] = {"centroid_world_m": list(center),
                           "centroid_to_wrist_m": (center-wrist).length,
                           "interpretation": "geometric witness, not a finger contact/intersection proof"}
    wrists = {}
    for side in ("l", "r"):
        matrix = armature.matrix_world @ armature.pose.bones["hand_"+side].matrix
        wrists[side] = {"position_world_m": list(matrix.translation),
                        "quaternion_wxyz": list(matrix.to_quaternion())}
    return {
        "bounds_world_m": {"min": lower, "max": upper,
                           "size": [b-a for a, b in zip(lower, upper)]},
        "evaluated_vertex_count": len(points),
        "feet_min_z_m": feet_min,
        "support_foot_min_z_m": min(available_feet) if available_feet else None,
        "root_translation_m": armature.pose.bones["root"].location.length,
        "maximum_pose_scale_error": max(abs(value-1) for bone in armature.pose.bones for value in bone.scale),
        "eye_centroid_above_shield_top_m": min(eyes)-shield_max if eyes and shield_max is not None else None,
        "eye_clearance_source": "actual evaluated named editable eye/shield parts" if eyes and shield else "unavailable; no named eye/shield witnesses",
        "wrists": wrists, "grip_witnesses": grips,
        "equipment_alignment": {
            "sword": _rigid_axis(semantic, "sword_blade", _witness(semantic, "sword_blade", depsgraph, cache), armature, "hand_r"),
            "shield": _rigid_axis(semantic, "shield_shell", shield, armature, "hand_l")},
        "camera_bounds": {"min": [min(point[i] for point in projected) for i in range(2)],
                          "max": [max(point[i] for point in projected) for i in range(2)],
                          "interpretation": "projected world AABB; conservative crop warning"},
    }


def _contact_sheets(frames, directory, thumb=128, columns=7, rows=5):
    outputs = []
    for start in range(0, len(frames), columns*rows):
        batch = frames[start:start+columns*rows]
        used_rows = math.ceil(len(batch)/columns)
        canvas = np.ones((used_rows*thumb, columns*thumb, 4), dtype=np.float32)
        canvas[:, :, :3] = .045
        cells = []
        for index, record in enumerate(batch):
            source = bpy.data.images.load(record["path"], check_existing=False)
            try:
                source.colorspace_settings.name = "Non-Color"
                source.scale(thumb, thumb)
                pixels = np.empty(len(source.pixels), dtype=np.float32)
                source.pixels.foreach_get(pixels)
                col, row = index % columns, index // columns
                y = (used_rows-row-1)*thumb
                canvas[y:y+thumb, col*thumb:(col+1)*thumb] = pixels.reshape((thumb, thumb, 4))
                cells.append({"row_top_down": row, "column": col, "authored_frame": record["frame"], "source": record["path"]})
            finally:
                bpy.data.images.remove(source)
        image = bpy.data.images.new("AQ1_MotionContactSheet", columns*thumb, used_rows*thumb, alpha=True, float_buffer=True)
        try:
            # Copy the captured PNG colors without applying a second view transform.
            image.colorspace_settings.name = "Non-Color"
            image.pixels.foreach_set(canvas.ravel())
            image.update()
            target = directory/f"contact_sheet_{start//(columns*rows)+1:02d}.png"
            image.filepath_raw = str(target)
            image.file_format = "PNG"
            image.save()
            outputs.append({"path": str(target), "cells": cells,
                            "method": "downsampled actual rendered frames in chronological row order"})
        finally:
            bpy.data.images.remove(image)
    return outputs


def review_candidate(out_dir, collection_name=None, render_fps=20, size=512):
    if render_fps != 20 or size != 512:
        raise ValueError("This AQ1 review contract uses 20fps / 512px captures")
    out_dir = Path(out_dir).resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        raise RuntimeError("Preserve existing motion evidence; choose a fresh output directory")
    scene = bpy.context.scene
    if scene.render.fps != 60 or abs(scene.render.fps_base-1) > 1e-8:
        raise RuntimeError("Expected the authored 60fps timing contract")
    meshes, scope = _objects(collection_name)
    armature = bpy.data.objects.get("Armature")
    if armature is None or armature.type != "ARMATURE":
        raise RuntimeError("Existing Armature is unavailable")
    before = invariants(armature)
    saved_action = armature.animation_data.action
    saved_slot = armature.animation_data.action_slot
    saved_frame = scene.frame_current
    saved_pose = armature.data.pose_position
    saved_visibility = {ob: ob.hide_render for ob in scene.objects}
    saved_viewport = {ob: (ob.hide_viewport, ob.hide_get()) for ob in scene.objects}
    saved_collections = {collection: collection.hide_viewport for collection in bpy.data.collections}
    saved_world, saved_camera = scene.world, scene.camera
    saved_engine = scene.render.engine
    saved_render = {key: getattr(scene.render, key) for key in
                    ("resolution_x", "resolution_y", "resolution_percentage", "film_transparent", "filepath")}
    saved_format = scene.render.image_settings.file_format
    saved_view = {key: getattr(scene.view_settings, key) for key in ("view_transform", "exposure", "gamma")}
    saved_cycles = (scene.cycles.samples, scene.cycles.use_denoising)
    objects_before = set(bpy.data.objects)
    semantic = _semantic_parts()
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    report = {"status": "STARTED", "source": bpy.data.filepath,
              "source_sha256": hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() if bpy.data.filepath else None,
              "blender_version": bpy.app.version_string, "mesh_scope": scope,
              "rendered_objects": [ob.name for ob in meshes], "source_fps": 60,
              "render_sample_fps": 20, "resolution": [512, 512],
              "camera": {"view": "three_quarter", "values": VIEWS["three_quarter"]},
              "clip_results": [], "quantitative_issues": [],
              "visual_review": "pending; generated frames have not been viewed by this script",
              "limits": ["20fps renders sample continuous 60fps actions; every integer source frame is measured",
                         "grip centroids and wrist-relative axes do not establish finger contact or no intersection",
                         "eye/shield witnesses use retained named editable geometry, not a reconstructed baked vertex selector",
                         "contact sheet order is chronological; continuous playback review remains a human/agent task",
                         "foot-plane thresholds follow existing source invariant checks, not artistic acceptance"]}
    output = out_dir/"motion_review.json"
    output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    try:
        for ob in scene.objects:
            if ob.type == "MESH":
                ob.hide_render = ob not in meshes
        for mesh in meshes:
            mesh.hide_set(False)
            mesh.hide_viewport = False
        for mesh in semantic.values():
            # Hidden render witnesses must still participate in deformation evaluation.
            mesh.hide_set(False)
            mesh.hide_viewport = False
            for collection in mesh.users_collection:
                collection.hide_viewport = False
        for mesh in meshes:
            for collection in mesh.users_collection:
                collection.hide_viewport = False
        scene = setup()
        # Camera/lighting match fixed AQ1 capture; EEVEE is explicitly recorded.
        choices = scene.render.bl_rna.properties["engine"].enum_items.keys()
        engine = next((name for name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE") if name in choices), None)
        if engine is None:
            raise RuntimeError("Installed Blender exposes no EEVEE render engine")
        scene.render.engine = engine
        report["render_engine"] = engine
        loc, target, scale = VIEWS["three_quarter"]
        scene.camera.location = loc
        scene.camera.rotation_euler = (Vector(target)-scene.camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.camera.data.ortho_scale = scale
        scene.render.resolution_x = scene.render.resolution_y = size
        armature.data.pose_position = "POSE"
        for clip in CLIPS:
            action = bpy.data.actions.get(f"AN_{UID}_{clip}")
            if action is None:
                raise RuntimeError("Missing required actual action: " + clip)
            start, end = (int(round(value)) for value in action.frame_range)
            if end <= start:
                raise RuntimeError("Degenerate required action: " + clip)
            use_clip(armature, clip, start)
            folder = out_dir/clip
            folder.mkdir()
            frame_records, renders = [], []
            scheduled = set(range(start, end+1, 3)) | {end}
            release = 16 if clip == "Attack" else 19 if clip == "Active" else None
            # Extrema evidence includes immediate neighbors without disguising
            # these extra stills as equally spaced continuous-playback frames.
            contact_frames = {f for f in (release-1, release, release+1) if start <= f <= end} if release else set()
            for frame in range(start, end+1):
                scene.frame_set(frame)
                bpy.context.view_layer.update()
                record = _measure(meshes, armature, semantic, scene)
                record["frame"] = frame
                record["time_seconds_from_start"] = (frame-start)/60
                frame_records.append(record)
                failures = []
                if record["root_translation_m"] > 1e-6 or record["maximum_pose_scale_error"] > 1e-6:
                    failures.append("root translation or pose scale drift")
                support = record["support_foot_min_z_m"]
                if support is None:
                    failures.append("support-foot geometry unavailable")
                elif support < -.025 or support > .045:
                    failures.append("support-foot floor threshold exceeded")
                if failures:
                    report["quantitative_issues"].append({"clip": clip, "frame": frame, "issues": failures})
                if frame in scheduled or frame in contact_frames:
                    path = folder/f"frame_{frame:04d}.png"
                    scene.render.filepath = str(path)
                    bpy.ops.render.render(write_still=True)
                    if not path.is_file() or path.stat().st_size == 0:
                        raise RuntimeError("Actual render did not produce " + str(path))
                    renders.append({"frame": frame, "time_seconds": (frame-start)/60,
                                    "path": str(path), "continuous_sequence": frame in scheduled,
                                    "contact_extremum": frame in contact_frames})
            continuous = [r for r in renders if r["continuous_sequence"]]
            clip_result = {"clip": clip, "action": action.name, "frame_range": [start, end],
                           "authored_duration_seconds": (end-start)/60, "measured_frames": len(frame_records),
                           "rendered_frames": renders, "continuous_sequence_frames": [r["frame"] for r in continuous],
                           "release_frame_absolute": release,
                           "measurements_path": str(folder/"measurements.json"),
                           "contact_sheets": _contact_sheets(renders, folder)}
            (folder/"measurements.json").write_text(json.dumps(frame_records, indent=2)+"\n", encoding="utf-8")
            report["clip_results"].append(clip_result)
            output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
            print("AQ1_MOTION_CLIP_RENDERED", clip, len(frame_records), len(renders), flush=True)
        if invariants(armature) != before:
            raise RuntimeError("Motion review changed authored rest/action data")
        report["status"] = "EXECUTED_WITH_QUANTITATIVE_ISSUES" if report["quantitative_issues"] else "QUANTITATIVE_CHECKS_PASSED_VISUAL_REVIEW_PENDING"
        report["preserved_invariants"] = before
        report["wall_seconds"] = time.perf_counter()-started
        report["total_measured_frames"] = sum(c["measured_frames"] for c in report["clip_results"])
        report["total_rendered_frames"] = sum(len(c["rendered_frames"]) for c in report["clip_results"])
        output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        return report
    except Exception as exc:
        report["status"] = "FAILED_OR_INTERRUPTED"
        report["error"] = str(exc)
        report["wall_seconds"] = time.perf_counter()-started
        output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        raise
    finally:
        armature.animation_data.action = saved_action
        armature.animation_data.action_slot = saved_slot
        armature.data.pose_position = saved_pose
        scene.frame_set(saved_frame)
        scene.render.engine = saved_engine
        for key, value in saved_render.items():
            setattr(scene.render, key, value)
        scene.render.image_settings.file_format = saved_format
        for key, value in saved_view.items():
            setattr(scene.view_settings, key, value)
        scene.cycles.samples, scene.cycles.use_denoising = saved_cycles
        scene.world, scene.camera = saved_world, saved_camera
        for ob, hidden in saved_visibility.items():
            if ob.name in bpy.data.objects:
                ob.hide_render = hidden
        for ob, (hidden, local_hidden) in saved_viewport.items():
            if ob.name in bpy.data.objects:
                ob.hide_viewport = hidden
                ob.hide_set(local_hidden)
        for collection, hidden in saved_collections.items():
            if collection.name in bpy.data.collections:
                collection.hide_viewport = hidden
        for ob in set(bpy.data.objects)-objects_before:
            bpy.data.objects.remove(ob, do_unlink=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--collection")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    result = review_candidate(args.output, args.collection)
    print("AQ1_MOTION_REVIEW_EXECUTED", result["status"], result["total_rendered_frames"], flush=True)


if __name__ == "__main__":
    main()

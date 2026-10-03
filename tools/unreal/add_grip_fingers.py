"""Add three grip bones to one hand of a Meshy-rigged hero and weight the hand's vertices to them.

Meshy's auto-rig stops at the wrist, so a hand cannot close around a handle. This works on a duplicate of the
body mesh: it adds <Side>Fingers1 (knuckles), <Side>Fingers2 (mid-finger) and <Side>Thumb under the hand bone and
splits the hand bone's own skin weights between them by position. The four fingers bend together as one unit.
Every new bone is unrotated in mesh space at rest, so the game can curl it about a mesh-space axis.

Reads WC_GRIP_RIG (JSON: mesh, out_mesh, hand, report, optional thumb_threshold, knuckle, middle).
Candidate rigging only; the result needs a look in the game before it is used.
"""
import json
import os
import traceback
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
job = json.loads(Path(os.environ["WC_GRIP_RIG"]).read_text(encoding="utf-8"))
report = {"job": job, "status": "STARTED"}


def vec(v):
    return [v.x, v.y, v.z]


def sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
def mul(a, k): return [a[0] * k, a[1] * k, a[2] * k]
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def norm(a):
    length = dot(a, a) ** 0.5
    return mul(a, 1 / length)
def mean(points): return mul([sum(p[i] for p in points) for i in range(3)], 1 / len(points))
def smooth(low, high, x):
    k = min(1.0, max(0.0, (x - low) / (high - low)))
    return k * k * (3 - 2 * k)
def rounded(a): return [round(x, 2) for x in a]


try:
    hand = job["hand"]
    side = hand.replace("Hand", "")
    names = [f"{side}Fingers1", f"{side}Fingers2", f"{side}Thumb"]
    if unreal.EditorAssetLibrary.does_asset_exist(job["out_mesh"]):
        raise RuntimeError("Output mesh already exists; choose a new name")
    source = unreal.EditorAssetLibrary.load_asset(job["mesh"])
    # Positions come from the untouched source; vertex numbering is shared with the skin-weight tool.
    dynamic = unreal.DynamicMesh()
    unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
        source, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD())
    queries = unreal.GeometryScript_MeshQueries
    mesh = unreal.EditorAssetLibrary.duplicate_asset(job["mesh"], job["out_mesh"])
    reader = unreal.SkinWeightModifier()
    reader.set_skeletal_mesh(mesh)
    count = reader.get_num_vertices()
    if count != queries.get_vertex_count(dynamic):
        raise RuntimeError("Vertex numbering differs between the two tools")
    weights, points = {}, {}
    for index in range(count):
        entry = {str(bone): float(value) for bone, value in reader.get_vertex_weights(index).items()}
        if entry.get(hand, 0) > 0:
            position = queries.get_vertex_position(dynamic, index)
            position = position[0] if isinstance(position, tuple) else position
            weights[index], points[index] = entry, vec(position)

    skeleton = unreal.SkeletonModifier()
    skeleton.set_skeletal_mesh(mesh)
    hand_global = skeleton.get_bone_transform(hand, True)
    wrist = vec(hand_global.translation)
    core = [points[i] for i in weights if weights[i][hand] > 0.5]
    axis = norm(sub(mean(core), wrist))
    along = sorted(core, key=lambda p: dot(sub(p, wrist), axis))
    axis = norm(sub(mean(along[int(len(along) * 0.8):]), wrist))
    length = max(dot(sub(p, wrist), axis) for p in core)
    # Toward the body's centre line; the thumb of a hanging arm lies on that side.
    inward = [-1.0 if wrist[0] > 0 else 1.0, 0.0, 0.0]
    inward = norm(sub(inward, mul(axis, dot(inward, axis))))
    palm = cross(axis, inward) if side == "Right" else cross(inward, axis)
    t = {i: dot(sub(points[i], wrist), axis) for i in weights}
    s = {i: dot(sub(points[i], wrist), inward) for i in weights}
    threshold = job.get("thumb_threshold")
    if threshold is None:
        # The thumb is separated from the fingers by the widest empty band across the hand.
        band = sorted(s[i] for i in weights if weights[i][hand] > 0.5 and 0.3 * length < t[i] < 0.9 * length)
        low, high = int(len(band) * 0.3), int(len(band) * 0.95)
        gap, threshold = max((band[k + 1] - band[k], (band[k + 1] + band[k]) / 2) for k in range(low, high))
        report["thumb_gap_cm"] = round(gap, 2)
        if gap < 0.5:
            threshold = None
    knuckle, middle, blend = job.get("knuckle", 0.5) * length, job.get("middle", 0.74) * length, 0.07 * length
    thumb = [i for i in weights if threshold is not None and s[i] > threshold and t[i] > 0.2 * length]
    thumb_set = set(thumb)
    fingers = [i for i in weights if i not in thumb_set]

    def centre(indices, target, fallback):
        near = [points[i] for i in indices if abs(t[i] - target) < blend]
        return mean(near) if near else fallback

    places = {names[0]: centre(fingers, knuckle, add(wrist, mul(axis, knuckle))),
              names[1]: centre(fingers, middle, add(wrist, mul(axis, middle)))}
    if thumb:
        base = sorted(thumb, key=lambda i: t[i])[:max(1, len(thumb) * 3 // 10)]
        places[names[2]] = mean([points[i] for i in base])
    parents = {names[0]: hand, names[1]: names[0], names[2]: hand}
    for name in names:
        if name not in places:
            continue
        target = unreal.Transform(location=unreal.Vector(*places[name]), rotation=unreal.Rotator(0, 0, 0), scale=unreal.Vector(1, 1, 1))
        parent_global = skeleton.get_bone_transform(parents[name], True)
        skeleton.add_bone(name, parents[name], unreal.MathLibrary.make_relative_transform(target, parent_global))
        report.setdefault("bones", {})[name] = {"wanted": rounded(places[name]),
                                                "placed": rounded(vec(skeleton.get_bone_transform(name, True).translation))}
    if not skeleton.commit_skeleton_to_skeletal_mesh():
        raise RuntimeError("Committing the new bones failed")

    writer = unreal.SkinWeightModifier()
    writer.set_skeletal_mesh(mesh)
    for index, entry in weights.items():
        share = entry.pop(hand)
        if index in thumb_set:
            moved = smooth(threshold, threshold + 1.0, s[index])
            entry[names[2]] = share * moved
            entry[hand] = share * (1 - moved)
        else:
            first, second = smooth(knuckle - blend, knuckle + blend, t[index]), smooth(middle - blend, middle + blend, t[index])
            entry[hand] = share * (1 - first)
            entry[names[0]] = share * (first - second)
            entry[names[1]] = share * second
        writer.set_vertex_weights(index, {unreal.Name(bone): value for bone, value in entry.items() if value > 0.0005})
    writer.normalize_all_weights()
    if not writer.commit_weights_to_skeletal_mesh():
        raise RuntimeError("Committing the skin weights failed")
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh.skeleton)
    report.update(status="RIGGED", hand_vertices=len(weights), thumb_vertices=len(thumb), wrist=rounded(wrist),
                  hand_axis=rounded(axis), inward=rounded(inward), palm_normal=rounded(palm), hand_length_cm=round(length, 1),
                  thumb_threshold=None if threshold is None else round(threshold, 2),
                  finger_curl_axis=rounded(cross(axis, palm)), all_bones=[str(b) for b in writer.get_all_bone_names()])
except Exception:
    report["status"] = "FAILED"
    report["error"] = traceback.format_exc()
path = root / job["report"]
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

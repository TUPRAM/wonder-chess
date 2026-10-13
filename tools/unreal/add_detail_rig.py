"""Extend a Meshy-rigged hero with jointed fingers and forearm twist bones, on a duplicate of the body mesh.

Meshy's auto-rig ends at the wrist. For a body modelled with open hands and separated fingers this adds, per hand,
three bones for each digit found (Thumb, Index, Middle, Ring, Pinky) and one forearm twist bone, and moves the hand
and forearm skin weights onto them by position. Digits are found as separate pieces of the hand surface beyond the
knuckle line, so the body images must show the fingers apart.

Every new bone is unrotated in mesh space at rest, so the game can bend it about a mesh-space axis taken from the
report. Reads WC_DETAIL_RIG (JSON: mesh, out_mesh, report). Candidate rigging; look at it in the game before use.
"""
import json
import os
import traceback
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
job = json.loads(Path(os.environ["WC_DETAIL_RIG"]).read_text(encoding="utf-8"))
report = {"job": job, "status": "STARTED", "hands": {}}


def sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
def mul(a, k): return [a[0] * k, a[1] * k, a[2] * k]
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def size(a): return dot(a, a) ** 0.5
def norm(a):
    length = size(a)
    return mul(a, 1 / length) if length > 1e-9 else [0.0, 0.0, 0.0]
def mean(points): return mul([sum(p[i] for p in points) for i in range(3)], 1 / len(points))
def smooth(low, high, x):
    k = min(1.0, max(0.0, (x - low) / (high - low)))
    return k * k * (3 - 2 * k)
def rounded(a): return [round(x, 3) for x in a]
def vec(v): return [v.x, v.y, v.z]


def pieces(indices, triangles, key):
    """Connected pieces of the surface among `indices`; vertices split at texture seams are joined by position."""
    parent = {}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    inside = set(indices)
    for i in inside:
        parent.setdefault(key[i], key[i])
    for a, b, c in triangles:
        if a in inside and b in inside and c in inside:
            ra, rb, rc = find(key[a]), find(key[b]), find(key[c])
            parent[rb] = ra
            parent[find(key[c])] = ra
    groups = {}
    for i in inside:
        groups.setdefault(find(key[i]), []).append(i)
    return list(groups.values())


try:
    if unreal.EditorAssetLibrary.does_asset_exist(job["out_mesh"]):
        raise RuntimeError("Output mesh already exists; choose a new name")
    source = unreal.EditorAssetLibrary.load_asset(job["mesh"])
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
    position, weights, key = [], [], []
    for index in range(count):
        p = queries.get_vertex_position(dynamic, index)
        p = vec(p[0] if isinstance(p, tuple) else p)
        position.append(p)
        key.append((round(p[0], 2), round(p[1], 2), round(p[2], 2)))
        weights.append({str(bone): float(value) for bone, value in reader.get_vertex_weights(index).items()})
    triangles = []
    for triangle in range(queries.get_num_triangle_i_ds(dynamic)):
        corners = queries.get_triangle_indices(dynamic, triangle)
        corners = corners[0] if isinstance(corners, tuple) else corners
        triangles.append((corners.x, corners.y, corners.z))
    report["vertices"], report["triangles"] = count, len(triangles)

    skeleton = unreal.SkeletonModifier()
    skeleton.set_skeletal_mesh(mesh)
    new_bones, changed = [], {}

    def place(name, parent, where):
        target = unreal.Transform(location=unreal.Vector(*where), rotation=unreal.Rotator(0, 0, 0), scale=unreal.Vector(1, 1, 1))
        skeleton.add_bone(name, parent, unreal.MathLibrary.make_relative_transform(target, skeleton.get_bone_transform(parent, True)))
        new_bones.append(name)

    for side in ("Right", "Left"):
        hand, fore = f"{side}Hand", f"{side}ForeArm"
        wrist, elbow = vec(skeleton.get_bone_transform(hand, True).translation), vec(skeleton.get_bone_transform(fore, True).translation)
        owned = [i for i in range(count) if weights[i].get(hand, 0) > 0]
        core = [i for i in owned if weights[i][hand] > 0.5]
        axis = norm(sub(mean([position[i] for i in core]), wrist))
        far = sorted(core, key=lambda i: dot(sub(position[i], wrist), axis))
        axis = norm(sub(mean([position[i] for i in far[int(len(far) * 0.8):]]), wrist))
        if job.get("limb_radius_cm"):
            # A wide sleeve hangs on the hand bone too. Follow the forearm's line and keep only what lies close
            # to it, which is the hand itself.
            axis = norm(sub(wrist, elbow))
            def off_line(i):
                q = sub(position[i], wrist)
                return size(sub(q, mul(axis, dot(q, axis))))
            owned = [i for i in owned if off_line(i) <= job["limb_radius_cm"] and dot(sub(position[i], wrist), axis) > -2]
            core = [i for i in core if i in set(owned)]
        t = {i: dot(sub(position[i], wrist), axis) for i in owned}
        length = max(t[i] for i in core)

        def digits(cut):
            found = pieces([i for i in owned if t[i] > cut * length], triangles, key)
            return [g for g in found if len(g) >= 12 and max(t[i] for i in g) - min(t[i] for i in g) > 0.12 * length]

        # The thumb leaves the palm first: slide a cut from the wrist outward until the surface beyond it falls
        # into two pieces, and take the smaller one.
        thumb, info = None, {"hand_axis": rounded(axis), "hand_length_cm": round(length, 2), "digits": {}}
        # The bodies are drawn in an A-pose with the palms toward the thighs, so the thumb is the forward-most
        # digit. A piece only counts as the thumb if it is small, short and clearly in front of the hand; that
        # keeps hanging sleeves, cuffs and stray fingertips from being taken for it.
        centre = mean([position[i] for i in core])
        forward = norm(sub([0.0, 1.0, 0.0], mul(axis, axis[1])))
        for cut in range(20, 72, 2):
            found = digits(cut / 100.0)
            if len(found) < 2:
                continue
            total = sum(len(g) for g in found)
            fit = [g for g in found if len(g) < 0.3 * total
                   and max(t[i] for i in g) - min(t[i] for i in g) < 0.45 * length
                   and dot(sub(mean([position[i] for i in g]), centre), forward) > 0.12 * length]
            if fit:
                thumb = max(fit, key=lambda g: dot(sub(mean([position[i] for i in g]), centre), forward))
                info["thumb_cut"] = cut / 100.0
                break
        if thumb is None:
            # No separate piece: take the part of the mid-hand that stands clearly forward of it.
            lump = [i for i in owned if 0.2 * length < t[i] < 0.8 * length
                    and dot(sub(position[i], centre), forward) > 0.2 * length]
            if len(lump) >= 30:
                thumb, info["thumb_cut"] = lump, "forward lump"
        thumb_set = set(thumb or [])
        knuckle = job.get("knuckle", 0.48) * length
        region = [i for i in owned if i not in thumb_set and t[i] > knuckle]
        # The fingers lie side by side even where the model joined them. Find the direction they are spread along
        # (the widest direction of the finger region across the hand) and cut it into four bands at the grooves.
        middle = mean([position[i] for i in region])
        e1 = norm(cross(axis, [0.0, 0.0, 1.0] if abs(axis[2]) < 0.9 else [1.0, 0.0, 0.0]))
        e2 = cross(axis, e1)
        xx = xy = yy = 0.0
        for i in region:
            q = sub(position[i], middle)
            a, b = dot(q, e1), dot(q, e2)
            xx, xy, yy = xx + a * a, xy + a * b, yy + b * b
        import math
        angle = 0.5 * math.atan2(2 * xy, xx - yy)
        across = norm(add(mul(e1, math.cos(angle)), mul(e2, math.sin(angle))))
        # The fingers fan out front to back; if the widest direction is not that, trust the pose instead.
        if abs(dot(across, forward)) < 0.5:
            across = forward
        elif dot(across, forward) < 0:
            across = mul(across, -1)
        palm = cross(axis, across) if side == "Right" else cross(across, axis)
        w = {i: dot(sub(position[i], middle), across) for i in region}
        tips = [w[i] for i in region if t[i] > 0.62 * length]
        low, high = min(tips), max(tips)
        bins = 36
        histogram = [0.0] * bins
        for value in tips:
            histogram[min(bins - 1, int((value - low) / (high - low) * bins))] += 1
        for _ in range(2):
            histogram = [(histogram[max(0, k - 1)] + 2 * histogram[k] + histogram[min(bins - 1, k + 1)]) / 4 for k in range(bins)]
        count_fingers = job.get("fingers", 4)
        edges = []
        for k in range(1, count_fingers):
            target = k * bins / count_fingers
            window = range(max(1, int(target - bins / (count_fingers * 2.5))), min(bins - 1, int(target + bins / (count_fingers * 2.5)) + 1))
            groove = min(window, key=lambda b: (histogram[b], abs(b - target)))
            edges.append(low + (groove + 0.5) / bins * (high - low))
        info.update(toward_thumb=rounded(across), palm_normal=rounded(palm), finger_grooves_cm=rounded(edges), knuckle_cm=round(knuckle, 2))
        # Band 0 is the pinky side (least toward the thumb); the index finger is nearest the thumb.
        bands = [[] for _ in range(count_fingers)]
        for i in region:
            bands[sum(1 for edge in edges if w[i] > edge)].append(i)
        labels = {4: ["Pinky", "Ring", "Middle", "Index"], 3: ["Pinky", "Middle", "Index"]}.get(count_fingers, [f"Finger{n + 1}" for n in range(count_fingers)])
        named = [(label, group) for label, group in zip(labels, bands) if len(group) >= 12]
        if thumb:
            named.insert(0, ("Thumb", thumb))
        for label, group in named:
            # Axis of the digit: from its root to its tip, refined once.
            direction = axis
            for _ in range(2):
                order = sorted(group, key=lambda i: dot(position[i], direction))
                edge = max(3, len(order) // 7)
                base, tip = mean([position[i] for i in order[:edge]]), mean([position[i] for i in order[-edge:]])
                direction = norm(sub(tip, base))
            along = {i: dot(sub(position[i], base), direction) for i in group}
            reach = max(along.values())
            joints = [0.0, 0.42 * reach, 0.72 * reach]
            names = [f"{side}{label}{n}" for n in (1, 2, 3)]
            parents = [hand, names[0], names[1]]
            for name, parent, at in zip(names, parents, joints):
                place(name, parent, add(base, mul(direction, at)))
            blend = 0.08 * reach
            for i in group:
                entry = dict(weights[i]) if i not in changed else changed[i]
                share = entry.pop(hand, 0.0)
                if share <= 0:
                    continue
                x = along[i]
                second, third = smooth(joints[1] - blend, joints[1] + blend, x), smooth(joints[2] - blend, joints[2] + blend, x)
                rooted = smooth(-0.03 * reach, 0.12 * reach, x)
                entry[hand] = share * (1 - rooted)
                entry[names[0]] = share * rooted * (1 - second)
                entry[names[1]] = share * rooted * (second - third)
                entry[names[2]] = share * rooted * third
                changed[i] = entry
            info["digits"][label] = {"vertices": len(group), "length_cm": round(reach, 2), "direction": rounded(direction),
                                     "flex_axis": rounded(norm(cross(direction, palm))), "bones": names}
        # Forearm twist: the lower forearm follows half of the wrist's turn, so the skin does not pinch at the wrist.
        twist = f"{side}ForeArmTwist"
        span = sub(wrist, elbow)
        place(twist, fore, add(elbow, mul(span, 0.6)))
        reach, line = size(span), norm(span)
        moved = 0
        for i in range(count):
            share = weights[i].get(fore, 0.0)
            if share <= 0:
                continue
            entry = changed.get(i) or dict(weights[i])
            part = smooth(0.35, 0.9, dot(sub(position[i], elbow), line) / reach)
            if part <= 0:
                continue
            entry[fore] = share * (1 - part)
            entry[twist] = share * part
            changed[i] = entry
            moved += 1
        info.update(forearm_axis=rounded(line), forearm_twist_vertices=moved)
        report["hands"][side] = info

    if not skeleton.commit_skeleton_to_skeletal_mesh():
        raise RuntimeError("Committing the new bones failed")
    writer = unreal.SkinWeightModifier()
    writer.set_skeletal_mesh(mesh)
    for index, entry in changed.items():
        writer.set_vertex_weights(index, {unreal.Name(bone): value for bone, value in entry.items() if value > 0.0005})
    writer.normalize_all_weights()
    if not writer.commit_weights_to_skeletal_mesh():
        raise RuntimeError("Committing the skin weights failed")
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh.skeleton)
    report.update(status="RIGGED", new_bones=new_bones, bone_count=len(writer.get_all_bone_names()), vertices_reweighted=len(changed))
except Exception:
    report["status"] = "FAILED"
    report["error"] = traceback.format_exc()
path = root / job["report"]
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

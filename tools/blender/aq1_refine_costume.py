"""Bounded tailored-costume replacement for the retained AQ1 r02 candidate.

Caller supplies initialized aq1_author_forms as form and owns save/render/review.
This module never opens/saves a file, changes a rig/action or runs reconstruction.
"""
import math
import bpy
from mathutils import Vector


def refine_costume(form):
    arm, collection = form.ARM, form.COL
    required = ["body_base", "armor_chest", "armor_back", "coat_skirt", "tabard_front", "tabard_back"]
    required += [prefix + side for side in ("l", "r") for prefix in ("coat_sleeve_", "boot_", "boot_sole_", "boot_toe_plate_")]
    for name in required:
        obj = bpy.data.objects.get(name)
        if obj is None or obj not in list(collection.objects) or obj.type != "MESH":
            raise RuntimeError("Expected named r02 costume surface: " + name)
        if any(abs(value - 1) > .00001 for value in obj.scale):
            raise RuntimeError("Unexpected unapplied candidate object scale: " + name)
    for name in required:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    def shell(obj, thickness, bevel=0):
        modifier = obj.modifiers.new("TailoredThickness", "SOLIDIFY")
        modifier.thickness = thickness
        modifier.offset = -1
        if bevel:
            modifier = obj.modifiers.new("ControlledEdge", "BEVEL")
            modifier.width, modifier.segments = bevel, 2
        return obj

    def tube(name, sections, material, weights, x=0, power=1, caps=False, segments=28):
        verts, faces, skin = [], [], []
        for row, (z, rx, ry, cy) in enumerate(sections):
            for index in range(segments):
                angle = 2 * math.pi * index / segments
                sn, cs = math.sin(angle), math.cos(angle)
                verts.append((x + rx * math.copysign(abs(sn) ** power, sn), cy + ry * math.copysign(abs(cs) ** power, cs), z))
                skin.append(weights[row] if isinstance(weights, list) else weights)
        for row in range(len(sections) - 1):
            for index in range(segments):
                a = row * segments + index
                b = row * segments + (index + 1) % segments
                faces.append((a, b, b + segments, a + segments))
        if caps:
            faces += [tuple(range(segments - 1, -1, -1)), tuple((len(sections) - 1) * segments + i for i in range(segments))]
        return form.mesh(name, verts, faces, material, weights=skin)

    # The hidden torso stays inside the breastplate. A fitted shoulder yoke
    # joins the sleeve roots instead of exposing the old coarse shoulder slab.
    torso_sections = [(.895, .162, .089, -.012), (1.03, .148, .093, -.013),
                      (1.15, .178, .103, -.018), (1.27, .222, .103, -.014),
                      (1.35, .242, .083, -.009), (1.39, .292, .070, -.006),
                      (1.418, .279, .061, -.005)]
    torso_weights = [{"pelvis": 1}, {"pelvis": .5, "spine_01": .5}, {"spine_01": .5, "spine_02": .5},
                     {"spine_02": 1}, {"spine_02": .6, "spine_03": .4}, {"spine_03": 1}, {"spine_03": 1}]
    tube("body_base", torso_sections, "ivory", torso_weights, caps=True)

    plate_rows = [(1.087, .155, .122), (1.115, .177, .144), (1.185, .217, .166),
                  (1.27, .247, .151), (1.337, .272, .119), (1.385, .258, .099)]
    verts, faces = [], []
    segments = 28
    for row, (z, rx, ry) in enumerate(plate_rows):
        for index in range(segments + 1):
            angle = -1.72 + 3.44 * index / segments
            front = max(0, math.cos(angle))
            ridge = .015 * front ** 10 * (math.sin(math.pi * row / (len(plate_rows) - 1)) ** .5)
            top = -.023 * front ** 3 if row == len(plate_rows) - 1 else 0
            verts.append((rx * math.sin(angle), ry * math.cos(angle) + ridge + .007, z + top))
    for row in range(len(plate_rows) - 1):
        for index in range(segments):
            a = row * (segments + 1) + index
            faces.append((a, a + 1, a + segments + 2, a + segments + 1))
    shell(form.mesh("armor_chest", verts, faces, "steel", "spine_02"), .007, .0025)
    # Only the rear surface is needed: no hidden full steel barrel inside chest.
    verts, faces = [], []
    for z, rx, ry in [(1.10, .158, .123), (1.22, .222, .132), (1.32, .253, .109), (1.392, .225, .083)]:
        for index in range(25):
            angle = math.pi / 2 + math.pi * index / 24
            verts.append((rx * math.sin(angle), ry * math.cos(angle) - .012, z))
    for row in range(3):
        for index in range(24):
            a = row * 25 + index
            faces.append((a, a + 1, a + 26, a + 25))
    shell(form.mesh("armor_back", verts, faces, "steel_dark", "spine_02"), .006, .002)

    # A coat skirt around the actual +/-0.1547m hip joints and 0.12m thighs.
    # Squarer rounded sections provide front/side clearance without a huge bell.
    skirt_rows = [(1.047, .169, .129), (1.005, .192, .146), (.947, .264, .183),
                  (.891, .299, .193), (.81, .308, .192), (.714, .314, .187), (.689, .312, .183)]
    power, segments = .73, 40
    verts, faces, weights = [], [], []
    for row, (z, rx, ry) in enumerate(skirt_rows):
        for index in range(segments):
            angle = 2 * math.pi * index / segments
            sn, cs = math.sin(angle), math.cos(angle)
            x = rx * math.copysign(abs(sn) ** power, sn)
            y = ry * math.copysign(abs(cs) ** power, cs)
            lower = max(0, min(1, (.95 - z) / .26))
            y += .0035 * math.sin(angle * 6) * lower
            verts.append((x, y, z + .006 * math.cos(angle * 4) * lower))
            influence = lower * .40 * min(1, abs(x) / .12)
            weights.append({"pelvis": 1 - influence, "thigh_l" if x >= 0 else "thigh_r": influence})
    for row in range(len(skirt_rows) - 1):
        for index in range(segments):
            a = row * segments + index
            b = row * segments + (index + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    shell(form.mesh("coat_skirt", verts, faces, "ivory", weights=weights), .004)

    def skirt_envelope(z, x):
        for top, bottom in zip(skirt_rows, skirt_rows[1:]):
            if bottom[0] <= z <= top[0]:
                fraction = (top[0] - z) / (top[0] - bottom[0])
                rx, ry = [top[j] * (1 - fraction) + bottom[j] * fraction for j in (1, 2)]
                break
        else:
            _, rx, ry = skirt_rows[0] if z > skirt_rows[0][0] else skirt_rows[-1]
        return ry * max(0, 1 - (abs(x) / rx) ** (2 / power)) ** (power / 2)

    for front in (True, False):
        verts, faces, weights = [], [], []
        cols, rows = 7, 11
        for side in (-1, 1):
            start = len(verts)
            for row in range(rows):
                t = row / (rows - 1)
                width = .139 + .021 * t
                gap = .026 * max(0, (t - .63) / .37)
                for index in range(cols + 1):
                    u = index / cols
                    x = side * (gap + (width - gap) * u)
                    z = 1.042 - .407 * t + .018 * u * t ** 5
                    depth = skirt_envelope(z, x) + .016 + .005 * math.sin(u * math.pi * 2) * t
                    verts.append((x, depth * (1 if front else -1), z))
                    follow = .28 * max(0, (t - .25) / .75)
                    weights.append({"pelvis": 1 - follow, "thigh_l" if side > 0 else "thigh_r": follow})
            for row in range(rows - 1):
                for index in range(cols):
                    a = start + row * (cols + 1) + index
                    faces.append((a, a + 1, a + cols + 2, a + cols + 1))
        shell(form.mesh("tabard_front" if front else "tabard_back", verts, faces, "navy", weights=weights), .003)

    for side in ("l", "r"):
        shoulder = arm.data.bones["upperarm_" + side].head_local.copy()
        elbow = arm.data.bones["lowerarm_" + side].head_local.copy()
        wrist = arm.data.bones["hand_" + side].head_local.copy()
        axis = elbow - shoulder
        points = [shoulder - axis * .065, shoulder + axis * .17, shoulder + axis * .42,
                  shoulder + axis * .72, elbow, elbow + (wrist - elbow) * .22,
                  elbow + (wrist - elbow) * .55, wrist]
        skin = [{"upperarm_" + side: 1}] * 3
        skin += [{"upperarm_" + side: .8, "lowerarm_" + side: .2},
                 {"upperarm_" + side: .4, "lowerarm_" + side: .6},
                 {"lowerarm_" + side: 1}, {"lowerarm_" + side: 1},
                 {"lowerarm_" + side: .8, "hand_" + side: .2}]
        form.sweep("coat_sleeve_" + side, points, [.091, .091, .087, .073, .069, .068, .054, .043],
                   "ivory", "upperarm_" + side, segments=24, weights=skin)
        ankle = arm.data.bones["foot_" + side].head_local.copy()
        foot = "foot_" + side
        calf = "calf_" + side
        # Continuous upper from the top of the sole into the ankle. No stacked balls.
        upper = [(.035, .079, .158, .073), (.056, .084, .161, .073),
                 (.083, .082, .155, .071), (.115, .076, .134, .047),
                 (.153, .067, .091, .008), (.192, .060, .066, -.004),
                 (.245, .061, .067, -.003), (.273, .065, .068, -.002)]
        skin = [{foot: 1}] * 5 + [{foot: .85, calf: .15}, {foot: .6, calf: .4}, {foot: .45, calf: .55}]
        tube("boot_" + side, upper, "leather", skin, x=ankle.x, power=.68, caps=True, segments=28)
        sole = [(.012, .081, .159, .073), (.017, .088, .166, .073),
                (.033, .088, .166, .073), (.04, .081, .161, .073)]
        tube("boot_sole_" + side, sole, "leather", {foot: 1}, x=ankle.x, power=.68, caps=True, segments=28)
        # Toe cap is an open forged roof conforming to the upper, not an oval pod.
        verts, faces = [], []
        toe_rows = [(.096, .067, .164), (.129, .073, .153), (.173, .078, .133),
                    (.211, .071, .105), (.238, .048, .068)]
        cols = 14
        for y, half_width, top in toe_rows:
            for index in range(cols + 1):
                u = -1 + 2 * index / cols
                verts.append((ankle.x + half_width * u, y, top - .041 * abs(u) ** 1.65))
        for row in range(len(toe_rows) - 1):
            for index in range(cols):
                a = row * (cols + 1) + index
                faces.append((a, a + 1, a + cols + 2, a + cols + 1))
        shell(form.mesh("boot_toe_plate_" + side, verts, faces, "steel", foot), .003, .001)

    return {
        "replaced_semantic_parts": required,
        "changes": ["Fitted torso sits behind a curved chest and rear armor shell",
                    "Rounded tailored skirt clears the existing thigh envelope",
                    "Split tabards follow the coat envelope with deliberate front/back separation",
                    "Reduced sleeves fit the existing pauldrons and r02 bracers",
                    "Continuous leather boot uppers and flat soles replace stacked ellipsoids",
                    "Curved toe-cap roofs follow the upper without closed hidden metal pods"],
        "skeleton_actions": "not_modified",
        "visual_status": "RENDER_AND_CONTINUOUS_CLIP_REVIEW_REQUIRED",
    }

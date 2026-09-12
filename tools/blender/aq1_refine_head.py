"""Bounded AQ1 head revision using named candidate parts, never canonical surgery."""
from __future__ import annotations

import math

import bpy
from mathutils import Vector


PI = math.pi
PROFILE = [
    (1.491, .026, .034, .017), (1.509, .048, .056, .010),
    (1.531, .074, .071, -.003), (1.557, .089, .079, -.009),
    (1.590, .103, .083, -.014), (1.622, .115, .087, -.017),
    (1.658, .114, .092, -.018), (1.694, .112, .094, -.017),
    (1.732, .106, .087, -.015), (1.769, .093, .073, -.014),
    (1.800, .062, .049, -.014), (1.814, .012, .012, -.014),
]


def _catmull(a, b, c, d, t):
    return .5 * ((2 * b) + (-a + c) * t + (2*a - 5*b + 4*c - d) * t*t
                 + (-a + 3*b - 3*c + d) * t*t*t)


def _dims(z):
    for index, (a, b) in enumerate(zip(PROFILE, PROFILE[1:])):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            before, after = PROFILE[max(0, index-1)], PROFILE[min(len(PROFILE)-1, index+2)]
            values = tuple(_catmull(before[i], a[i], b[i], after[i], t) for i in range(1, 4))
            return max(.008, values[0]), max(.008, values[1]), values[2]
    return PROFILE[0][1:] if z < PROFILE[0][0] else PROFILE[-1][1:]


def _g(value, center, width):
    return math.exp(-((value - center) / width) ** 2)


def face_y(x, z):
    """Continuous brow, cheek, nose, muzzle and chin surface in source meters."""
    rx, ry, cy = _dims(z)
    y = cy + ry * math.sqrt(max(.00001, 1 - (x/rx)**2))
    # A bridge, rounded tip and alar transition are part of the facial surface.
    y += .024 * _g(x, 0, .018) * _g(z, 1.660, .046)
    y += .029 * _g(x, 0, .019) * _g(z, 1.627, .013)
    y += .009 * (_g(x, -.014, .008) + _g(x, .014, .008)) * _g(z, 1.619, .009)
    y -= .005 * _g(x, 0, .026) * _g(z, 1.609, .005)
    for side in (-1, 1):
        y -= .009 * _g(x, side*.050, .030) * _g(z, 1.670, .013)
        y += .007 * _g(x, side*.048, .035) * _g(z, 1.697, .010)
        y += .011 * _g(x, side*.067, .031) * _g(z, 1.637, .022)
        y -= .004 * _g(x, side*.076, .026) * _g(z, 1.576, .021)
    y += .004 * _g(x, 0, .028) * _g(z, 1.588, .023)
    y += .006 * _g(x, 0, .029) * _g(z, 1.581, .007)
    y += .007 * _g(x, 0, .027) * _g(z, 1.569, .006)
    y += .005 * _g(x, 0, .035) * _g(z, 1.526, .013)
    return y


def _material(module, key, color, roughness=.62):
    old = module.MATS.get(key)
    if old:
        if not old.name.startswith("AQ1_"):
            raise RuntimeError(f"Refusing non-AQ1 material: {old.name}")
        return old
    return module.make_material(key, color, roughness, 0)


def _face(module):
    # Front samples use uniform X spacing so nose/eye support gets useful topology.
    # The back uses a quieter elliptical arc; each complete ring has 64 vertices.
    ring = [(u, math.sqrt(max(0, 1-u*u)), True) for u in [-1 + 2*i/40 for i in range(41)]]
    ring += [(math.sin(PI/2 + PI*i/24), math.cos(PI/2 + PI*i/24), False)
             for i in range(1, 24)]
    heights = [1.491, 1.498, 1.508, 1.519, 1.530, 1.541, 1.552,
               1.560, 1.567, 1.573, 1.579, 1.585, 1.593, 1.601,
               1.609, 1.616, 1.622, 1.629, 1.637, 1.646, 1.655,
               1.663, 1.670, 1.678, 1.686, 1.695, 1.705, 1.718,
               1.733, 1.749, 1.765, 1.781, 1.796, 1.807, 1.814]
    vertices, faces = [], []
    for z in heights:
        rx, ry, cy = _dims(z)
        for u, c, front in ring:
            x = rx*u
            vertices.append((x, face_y(x, z) if front else cy+ry*c, z))
    n = len(ring)
    for row in range(len(heights)-1):
        for col in range(n):
            a, b = row*n+col, row*n+(col+1) % n
            faces.append((a, b, b+n, a+n))
    faces += [tuple(range(n-1, -1, -1)), tuple((len(heights)-1)*n+i for i in range(n))]
    return module.mesh("head_surface", vertices, faces, "skin")


def _eye_position(side, t, upper):
    x = side*(.023 + .050*t)
    center = 1.665 + .0045*t
    z = center + (.0088 if upper else -.0056)*math.sin(PI*t)
    return x, z


def _eye_y(x, z, side):
    t = max(0, min(1, (abs(x)-.023)/.050))
    return face_y(x, z) + .0024 + .0032*math.sin(PI*t)


def _eyes(module):
    for side, label in ((1, "l"), (-1, "r")):
        boundary = []
        for upper, sequence in ((True, range(21)), (False, range(19, 0, -1))):
            for index in sequence:
                x, z = _eye_position(side, index/20, upper)
                boundary.append((x, _eye_y(x, z, side), z))
        cx, cz = side*.048, 1.6672
        center = (cx, _eye_y(cx, cz, side)+.0009, cz)
        module.mesh("eye_white_"+label, [center]+boundary,
                    [(0, i+1, (i+1) % len(boundary)+1) for i in range(len(boundary))], "eye")
        # Skin ribbons merge the eye opening into the orbit. No tube surrounds it.
        for upper in (True, False):
            vertices, faces = [], []
            for row in range(3):
                amount = row/2
                for index in range(21):
                    t = index/20
                    x, z = _eye_position(side, t, upper)
                    z += amount*(.005 if upper else -.005)*math.sin(PI*t)
                    y_inner = _eye_y(x, z, side) + .00025
                    y_outer = face_y(x, z) + .00015
                    y = y_inner*(1-amount) + y_outer*amount
                    vertices.append((x, y, z))
            for row in range(2):
                for index in range(20):
                    a = row*21+index
                    faces.append((a, a+1, a+22, a+21))
            module.mesh("eyelid_"+("upper_" if upper else "lower_")+label, vertices, faces, "skin")
        # Restrained upper lash line, omitted from the lower lid to avoid a wire ring.
        vertices, faces = [], []
        for row in (0, 1):
            for index in range(21):
                t = index/20
                x, z = _eye_position(side, t, True)
                z += row*.0012*math.sin(PI*t)
                vertices.append((x, _eye_y(x, z, side)+.00065, z))
        for index in range(20):
            faces.append((index, index+1, index+22, index+21))
        module.mesh("eye_lash_"+label, vertices, faces, "lid_shadow")
        # Shallow iris and pupil disks follow the supported eye surface.
        for semantic, rx, rz, mat, offset in (("iris", .0086, .0065, "iris", .00135),
                                               ("pupil", .00415, .0044, "hair", .0017)):
            vertices = [(cx, _eye_y(cx, cz, side)+offset, cz)]
            for index in range(24):
                angle = 2*PI*index/24
                x, z = cx+rx*math.cos(angle), cz+rz*math.sin(angle)
                vertices.append((x, _eye_y(x, z, side)+offset, z))
            module.mesh(semantic+"_"+label, vertices,
                        [(0, i+1, (i+1) % 24+1) for i in range(24)], mat)
        module.ellipsoid("eye_glint_"+label,
                         (cx-.0018, _eye_y(cx, cz, side)+.0024, cz+.0025),
                         (.0011, .00045, .0012), "eye", rings=4, segments=8)
        # Square, calm inner brow tapers into the temple instead of an inflated tube.
        vertices, faces = [], []
        for row in (0, 1):
            for index in range(14):
                t = index/13
                x = side*(.021+.063*t)
                bottom = 1.690 + .0035*math.sin(PI*t) - .002*t
                thickness = (.0065*(1-t)**.6+.00035)*row
                z = bottom+thickness
                vertices.append((x, face_y(x, z)+.0014, z))
        for index in range(13):
            faces.append((index, index+1, index+15, index+14))
        module.mesh("brow_"+label, vertices, faces, "hair")


def _mouth_and_nose(module):
    # The surface already contains lip volume; these fitted ribbons define planes
    # and color without a disconnected lip tube or a dramatic baked shadow.
    def seam(x):
        t = abs(x)/.028
        return 1.5755 + .0018*t*t - .0008*_g(x, 0, .007)

    for upper, mat in ((True, "lip_upper"), (False, "lip_lower")):
        vertices, faces = [], []
        for row in range(3):
            amount = row/2
            for index in range(25):
                x = -.028+.056*index/24
                span = max(0, 1-(x/.028)**2)
                thickness = (.0052 + .0014*_g(abs(x), .009, .005)) if upper else .0064
                z = seam(x) + (1 if upper else -1)*amount*thickness*span
                vertices.append((x, face_y(x, z)+.00045, z))
        for row in range(2):
            for index in range(24):
                a = row*25+index
                faces.append((a, a+1, a+26, a+25))
        module.mesh("mouth_"+("upper" if upper else "lower"), vertices, faces, mat)
    vertices, faces = [], []
    for row in (0, 1):
        for index in range(25):
            x = -.028+.056*index/24
            z = seam(x)+(row-.5)*.0009*max(0, 1-(x/.028)**2)
            vertices.append((x, face_y(x, z)+.0009, z))
    for index in range(24):
        faces.append((index, index+1, index+26, index+25))
    module.mesh("mouth_line", vertices, faces, "lid_shadow")
    for side, label in ((1, "l"), (-1, "r")):
        vertices = []
        cx, cz = side*.0124, 1.6167
        for index in range(14):
            angle = 2*PI*index/14
            x = cx+.0042*math.cos(angle)
            z = cz+.00165*math.sin(angle)+side*.14*(x-cx)
            vertices.append((x, face_y(x, z)+.00035, z))
        module.mesh("nose_nostril_"+label, vertices, [tuple(range(14))], "nostril")


def _resample(points, radii, count):
    points = [Vector(p) for p in points]
    sampled, widths = [], []
    for index in range(count):
        u = (len(points)-1)*index/(count-1)
        segment = min(len(points)-2, int(u))
        t = u-segment
        ids = [max(0, segment-1), segment, segment+1, min(len(points)-1, segment+2)]
        sampled.append(tuple(_catmull(*(points[i] for i in ids), t)))
        widths.append(max(.0006, _catmull(*(radii[i] for i in ids), t)))
    return sampled, widths


def _hair(module):
    vertices, faces = [], []
    segments, rows = 36, 9
    for row in range(rows+1):
        t = row/rows
        for index in range(segments):
            angle = 2*PI*index/segments
            front = max(0, math.cos(angle))
            bottom = 1.640+.103*front+.009*math.sin(2*angle)
            phi = .025+(PI/2-.025)*t
            z = 1.823+(bottom-1.823)*(1-math.cos(phi))
            rx, ry, cy = _dims(min(z, 1.813))
            vertices.append(((rx+.006)*math.sin(angle),
                             cy+(ry+.007)*math.cos(angle), z))
    for row in range(rows):
        for index in range(segments):
            a, b = row*segments+index, row*segments+(index+1) % segments
            faces.append((a, b, b+segments, a+segments))
    module.mesh("hair_cap", vertices, faces, "hair")
    locks = [
        ([(-.021,.047,1.819),(-.053,.090,1.801),(-.081,.105,1.777),(-.104,.084,1.748),(-.119,.040,1.710),(-.113,-.013,1.670)],
         [.003,.017,.020,.020,.015,.002]),
        ([(-.014,.050,1.823),(.018,.089,1.814),(.060,.101,1.790),(.097,.079,1.758),(.118,.034,1.716),(.113,-.030,1.678)],
         [.003,.018,.022,.020,.016,.002]),
        ([(-.012,.010,1.823),(.040,.025,1.815),(.082,.014,1.793),(.112,-.025,1.756),(.116,-.071,1.708),(.077,-.105,1.666)],
         [.003,.019,.022,.021,.018,.003]),
        ([(-.034,.003,1.818),(-.077,.014,1.799),(-.112,-.015,1.756),(-.116,-.063,1.711),(-.078,-.107,1.674)],
         [.003,.019,.022,.021,.005]),
        ([(-.022,-.044,1.814),(.023,-.073,1.796),(.066,-.096,1.756),(.076,-.110,1.713),(.039,-.116,1.674),(0,-.121,1.650)],
         [.004,.020,.024,.021,.017,.004]),
    ]
    for index, (points, widths) in enumerate(locks):
        points, widths = _resample(points, widths, 20)
        module.sweep("hair_swept_lock_"+str(index), points, widths, "hair", "head", segments=8, depth=.45)
    # Two continuous alternating masses form a short braid instead of stacked balls.
    for side, phase in ((0, 0), (1, PI)):
        points, widths = [], []
        for index in range(22):
            t = index/21
            taper = 1-.52*t
            points.append((.017*math.cos(5*PI*t+phase)*taper,
                           -.121-.008*math.sin(5*PI*t+phase)-.005*t,
                           1.689-.187*t))
            widths.append(.017*taper)
        module.sweep("hair_braid_"+str(side), points, widths, "hair", "head", segments=8, depth=.9)
    points = [(-.018,-.126,1.511),(-.009,-.143,1.511),(.009,-.143,1.511),(.018,-.126,1.511)]
    points, widths = _resample(points, [.0035]*4, 12)
    module.sweep("hair_tie", points, widths, "leather", "head", segments=6)


def refine_head(module):
    """Replace only owned AQ1 head parts and return an honest authoring record."""
    if module.ARM is None or module.COL is None or module.COL.name != "AQ1_EDITABLE":
        raise RuntimeError("Initialize the author module with the live AQ1_EDITABLE candidate")
    before = module.invariants(module.ARM)
    prefixes = ("hair_", "eye_", "eyelid_", "iris_", "pupil_", "ear_", "brow_", "mouth_", "nose_")
    owned = [ob for ob in module.COL.objects if ob.type == "MESH" and
             (ob.get("aq1_semantic_part", ob.name) == "head_surface" or
              ob.get("aq1_semantic_part", ob.name).startswith(prefixes))]
    if not any(ob.get("aq1_semantic_part", ob.name) == "head_surface" for ob in owned):
        raise RuntimeError("No named AQ1 head source found; refusing topology-based selection")
    for key in ("skin", "hair", "eye", "iris"):
        if not module.MATS[key].name.startswith("AQ1_"):
            raise RuntimeError(f"Refusing shared material {module.MATS[key].name}")
    removed = [ob.name for ob in owned]
    owned_set = set(owned)
    module.PARTS[:] = [ob for ob in module.PARTS if ob not in owned_set]
    for ob in owned:
        bpy.data.objects.remove(ob, do_unlink=True)
    hair = next(n for n in module.MATS["hair"].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    old_hair_roughness = float(hair.inputs["Roughness"].default_value)
    hair.inputs["Roughness"].default_value = .67
    _material(module, "lip_upper", "84513E")
    _material(module, "lip_lower", "A2664D")
    _material(module, "lid_shadow", "36221C", .7)
    _material(module, "nostril", "6B4031", .7)
    start = len(module.PARTS)
    _face(module)
    _eyes(module)
    _mouth_and_nose(module)
    for side, label in ((1, "l"), (-1, "r")):
        module.ellipsoid("ear_"+label, (side*.116,-.012,1.643),
                         (.016,.014,.035), "skin", rings=8, segments=12)
        module.ellipsoid("ear_fold_"+label, (side*.125,.001,1.644),
                         (.005,.004,.020), "lip_upper", rings=6, segments=8)
    _hair(module)
    after = module.invariants(module.ARM)
    if before != after:
        raise RuntimeError("Head refinement changed the rest skeleton or action data")
    created = module.PARTS[start:]
    triangles = 0
    for ob in created:
        ob.data.calc_loop_triangles()
        triangles += len(ob.data.loop_triangles)
    return {
        "status": "head_geometry_authored_requires_actual_render_review",
        "removed_named_parts": removed, "new_named_parts": [ob.name for ob in created],
        "head_source_triangles": triangles, "preserved_skeleton_actions": before,
        "changes": ["continuous cheek, jaw, brow, nose and lip support surface",
                    "fitted skin eyelid ribbons with an upper-only lash accent",
                    "restrained nostril and shaped upper/lower lip regions",
                    "smoothly resampled swept hair and continuous braid masses"],
        "local_material_changes": {"hair_roughness_before": old_hair_roughness,
                                   "hair_roughness_after": .67,
                                   "new": ["lip_upper", "lip_lower", "lid_shadow", "nostril"],
                                   "skin_and_hair_base_colors_preserved": True},
        "pending": ["adult reference likeness and calm expression in actual pixels",
                    "side nose/lip continuity", "eye intersections and outline quality",
                    "hair silhouette and all seven animation extrema"],
    }

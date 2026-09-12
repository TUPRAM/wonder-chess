"""Editable AQ1 Ada equipment, authored in metre/Z-up/+Y-forward rest space.

This module only adds named candidate parts to the supplied collection. It does
not open/save files, reset a scene, change a rig/action, or touch canonical art.
The caller owns execution, visual review, baking and candidate export.
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Vector


TAU = 2.0 * math.pi


class _Part:
    def __init__(self, name, material="steel", smooth=True):
        self.name = name
        self.default_material = material
        self.default_smooth = smooth
        self.vertices = []
        self.faces = []
        self.face_materials = []
        self.face_smooth = []

    def vertex(self, point):
        self.vertices.append(tuple(point))
        return len(self.vertices) - 1

    def ring(self, points):
        return [self.vertex(point) for point in points]

    def face(self, indices, material=None, smooth=None):
        self.faces.append(tuple(indices))
        self.face_materials.append(material or self.default_material)
        self.face_smooth.append(self.default_smooth if smooth is None else smooth)

    def bridge(self, first, second, material=None, smooth=None):
        assert len(first) == len(second)
        for index in range(len(first)):
            nxt = (index + 1) % len(first)
            self.face((first[index], first[nxt], second[nxt], second[index]),
                      material, smooth)

    def finish(self, armature, materials, collection, bone, uv="box"):
        mesh = bpy.data.meshes.new(self.name + "_source")
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.update()
        # Recalculate normals without an operator or dependence on selection.
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        slots = list(dict.fromkeys(self.face_materials))
        for key in slots:
            mesh.materials.append(materials[key])
        for polygon, key, smooth in zip(mesh.polygons, self.face_materials,
                                        self.face_smooth):
            polygon.material_index = slots.index(key)
            polygon.use_smooth = smooth
        layer = mesh.uv_layers.new(name="AQ1_SourceUV")
        lower = [min(point[axis] for point in self.vertices) for axis in range(3)]
        upper = [max(point[axis] for point in self.vertices) for axis in range(3)]
        for polygon in mesh.polygons:
            normal_axis = max(range(3), key=lambda axis: abs(polygon.normal[axis]))
            axes = (0, 2) if uv == "front" else tuple(
                axis for axis in range(3) if axis != normal_axis)
            # Front/back shield and sword faces have a single coherent planar
            # island; side faces and gloves use six nonoverlapping atlas cells.
            cell = 0 if uv == "front" else normal_axis * 2 + int(
                polygon.normal[normal_axis] < 0)
            for loop_index in polygon.loop_indices:
                point = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                u, v = [(point[axis] - lower[axis]) /
                        max(upper[axis] - lower[axis], 1e-6) for axis in axes]
                if uv != "front":
                    u, v = ((cell % 3 + .025 + .95 * u) / 3,
                            (cell // 3 + .025 + .95 * v) / 2)
                layer.data[loop_index].uv = (u, v)
        obj = bpy.data.objects.new(self.name, mesh)
        collection.objects.link(obj)
        weights = obj.vertex_groups.new(name=bone)
        weights.add(list(range(len(mesh.vertices))), 1.0, "REPLACE")
        modifier = obj.modifiers.new("AQ1 existing hand driver", "ARMATURE")
        modifier.object = armature
        obj["aq1_semantic_part"] = self.name
        obj["aq1_rest_driver"] = bone
        obj["aq1_source_triangle_count"] = sum(len(face) - 2 for face in self.faces)
        obj["aq1_uv_intent"] = (
            "Coherent front/back planar equipment projection; bake into final atlas"
            if uv == "front" else
            "Six direction source islands; consolidate and inspect during atlas bake")
        obj["aq1_geometry_status"] = "candidate; requires actual render and clip review"
        return obj


def _loft(part, centers, radii, sides=10, preferred=(0, 1, 0), caps=True,
          material=None):
    """Transported elliptic sections, used for shaped handles and finger tips."""
    rings = []
    points = [Vector(point) for point in centers]
    previous_u = None
    for index, point in enumerate(points):
        tangent = (points[min(index + 1, len(points) - 1)] -
                   points[max(0, index - 1)]).normalized()
        reference = Vector(preferred) if previous_u is None else previous_u
        u = reference - tangent * reference.dot(tangent)
        if u.length < 1e-5:
            reference = Vector((1, 0, 0))
            u = reference - tangent * reference.dot(tangent)
        u.normalize()
        v = tangent.cross(u).normalized()
        previous_u = u
        radius = radii[index]
        ru, rv = (radius, radius) if isinstance(radius, (float, int)) else radius
        ring = part.ring(point + u * (ru * math.cos(TAU * side / sides)) +
                         v * (rv * math.sin(TAU * side / sides))
                         for side in range(sides))
        if rings:
            part.bridge(rings[-1], ring, material)
        rings.append(ring)
    if caps:
        part.face(tuple(reversed(rings[0])), material, False)
        part.face(rings[-1], material, False)
    return rings


def _outline():
    """A peaked kite: straight designed spans joined by small corner fillets."""
    controls = [
        (0, .440), (.112, .385), (.215, .326), (.278, .235),
        (.286, .105), (.265, -.055), (.186, -.258), (.082, -.391),
        (0, -.445), (-.082, -.391), (-.186, -.258), (-.265, -.055),
        (-.286, .105), (-.278, .235), (-.215, .326), (-.112, .385),
    ]
    corner_fillet = (.025, .20, .11, .12, .28, .25, .22, .18,
                     .035, .18, .22, .25, .28, .12, .11, .20)
    result = []
    for index in range(len(controls)):
        before, corner, after = [Vector(controls[(index + offset) % len(controls)])
                                 for offset in (-1, 0, 1)]
        fillet = corner_fillet[index]
        start = corner + (before - corner) * fillet
        end = corner + (after - corner) * fillet
        for step in range(3):
            t = step / 2
            result.append((1 - t) ** 2 * start +
                          2 * (1 - t) * t * corner + t * t * end)
    return result


def _shield(armature, materials, collection, hand):
    center = hand + Vector((0, .1469, .2679))
    outline = _outline()

    def surface(x, z):
        radius = min(1.0, math.sqrt((x / .288) ** 2 + (z / .445) ** 2))
        return center.y + .088 * (1 - radius * radius)

    shell = _Part("shield_shell", "navy")
    shell_rings = []
    for radius in (.20, .48, .74, .946):
        ring = shell.ring((center.x + point.x * radius,
                           center.y + .088 * (1 - radius * radius),
                           center.z + point.y * radius) for point in outline)
        if shell_rings:
            shell.bridge(shell_rings[-1], ring)
        shell_rings.append(ring)
    middle = shell.vertex((center.x, center.y + .088, center.z))
    for index in range(len(outline)):
        shell.face((middle, shell_rings[0][index],
                    shell_rings[0][(index + 1) % len(outline)]))
    rear = shell.ring((center.x + point.x * .946, center.y - .022,
                       center.z + point.y * .946) for point in outline)
    shell.bridge(shell_rings[-1], rear, "steel_dark", False)
    rear_center = shell.vertex((center.x, center.y - .022, center.z))
    for index in range(len(outline)):
        shell.face((rear_center, rear[(index + 1) % len(outline)], rear[index]),
                   "leather", False)

    rim = _Part("shield_rim", "steel")
    last = None
    first = None
    for radius, depth in ((.925, .014), (.946, .027), (.987, .026),
                          (1.008, .011), (1.008, -.024), (.987, -.038),
                          (.934, -.026)):
        ring = rim.ring((center.x + point.x * radius, center.y + depth,
                         center.z + point.y * radius) for point in outline)
        if last is not None:
            rim.bridge(last, ring)
        else:
            first = ring
        last = ring
    rim.bridge(last, first)

    crest = _Part("shield_crest", "gold")
    crest_z = .045
    crest_center = Vector((center.x, surface(0, crest_z) + .018,
                           center.z + crest_z))
    crest_rings = []
    for radius, raised in ((.020, .027), (.062, .023), (.087, .014), (.094, 0)):
        ring = crest.ring((crest_center.x + radius * math.cos(TAU * i / 32),
                           surface(radius * math.cos(TAU * i / 32),
                                   crest_z + radius * math.sin(TAU * i / 32)) +
                           .018 + raised,
                           crest_center.z + radius * math.sin(TAU * i / 32))
                          for i in range(32))
        if crest_rings:
            crest.bridge(crest_rings[-1], ring)
        crest_rings.append(ring)
    crest.face(tuple(reversed(crest_rings[0])))
    back_ring = crest.ring((crest_center.x + .094 * math.cos(TAU * i / 32),
                            surface(.094 * math.cos(TAU * i / 32),
                                    crest_z + .094 * math.sin(TAU * i / 32)) + .001,
                            crest_center.z + .094 * math.sin(TAU * i / 32))
                           for i in range(32))
    crest.bridge(crest_rings[-1], back_ring)
    crest.face(back_ring, smooth=False)
    # One broad sun applique. Rays are beveled wedges, never rods or ornaments.
    for ray in range(10):
        angle = TAU * ray / 10 + math.pi / 2
        radius = .175 if ray % 2 == 0 else .143
        planar = [(r * math.cos(a), crest_z + r * math.sin(a)) for r, a in
                  ((.088, angle - .145), (radius, angle), (.088, angle + .145))]
        bottom = crest.ring((center.x + x, surface(x, z) + .006, center.z + z)
                            for x, z in planar)
        upper = crest.ring((center.x + x, surface(x, z) + .014, center.z + z)
                           for x, z in planar)
        ridge = crest.vertex((center.x + .105 * math.cos(angle),
                              surface(.105 * math.cos(angle),
                                      crest_z + .105 * math.sin(angle)) + .023,
                              center.z + crest_z + .105 * math.sin(angle)))
        crest.bridge(bottom, upper, smooth=False)
        crest.face(tuple(reversed(bottom)), smooth=False)
        for index in range(3):
            crest.face((upper[index], upper[(index + 1) % 3], ridge), smooth=False)

    straps = _Part("shield_straps", "leather")
    # Raised rear handle clears the palm. Its ends return to the shield back.
    grip_center = Vector((hand.x, hand.y + .025, hand.z + .033))
    _loft(straps,
          [(hand.x, center.y - .027, grip_center.z - .098),
           (hand.x, grip_center.y + .012, grip_center.z - .074),
           (hand.x, grip_center.y, grip_center.z - .051),
           (hand.x, grip_center.y, grip_center.z + .052),
           (hand.x, grip_center.y + .012, grip_center.z + .074),
           (hand.x, center.y - .027, grip_center.z + .098)],
          [.016, .017, .017, .017, .017, .016], 10, material="leather")
    # A separate broad wrist strap has real width/thickness, with fixed ends.
    strap_rings = []
    for index in range(13):
        t = index / 12
        x = hand.x - .085 + .17 * t
        y = center.y - .030 - .148 * math.sin(math.pi * t)
        z = grip_center.z + .114
        ring = straps.ring(((x, y - .004, z - .019), (x, y + .004, z - .019),
                            (x, y + .004, z + .019), (x, y - .004, z + .019)))
        if strap_rings:
            straps.bridge(strap_rings[-1], ring, smooth=False)
        strap_rings.append(ring)
    straps.face(tuple(reversed(strap_rings[0])), smooth=False)
    straps.face(strap_rings[-1], smooth=False)
    return [part.finish(armature, materials, collection, "hand_l", "front")
            for part in (shell, rim, crest)] + [
                straps.finish(armature, materials, collection, "hand_l")]


def _sword(armature, materials, collection, hand):
    center = hand + Vector((-.005, .025, .033))
    axis = Vector((-.18, .035, -.983)).normalized()
    width = Vector((1, 0, -axis.x / axis.z)).normalized()
    front = width.cross(axis).normalized()

    def position(x, y, length):
        return center + width * x + front * y + axis * length

    blade = _Part("sword_blade", "steel", smooth=False)
    blade_rings = []
    for length, half_width, thickness in ((.083, .028, .010),
                                          (.117, .035, .011),
                                          (.441, .029, .009),
                                          (.548, .017, .006)):
        section = [(-half_width, 0), (-half_width * .76, thickness * .39),
                   (0, thickness), (half_width * .76, thickness * .39),
                   (half_width, 0), (half_width * .76, -thickness * .39),
                   (0, -thickness), (-half_width * .76, -thickness * .39)]
        ring = blade.ring(position(x, y, length) for x, y in section)
        if blade_rings:
            blade.bridge(blade_rings[-1], ring)
        blade_rings.append(ring)
    blade.face(tuple(reversed(blade_rings[0])))
    tip = blade.vertex(position(0, 0, .603))
    for index in range(8):
        blade.face((blade_rings[-1][index], blade_rings[-1][(index + 1) % 8], tip))

    guard = _Part("sword_guard", "gold", smooth=False)
    guard_rings = []
    for x, length, breadth, depth in ((-.102, .056, .008, .008),
                                     (-.090, .057, .013, .010),
                                     (-.060, .074, .013, .012),
                                     (-.028, .073, .016, .014),
                                     (.028, .073, .016, .014),
                                     (.060, .074, .013, .012),
                                     (.090, .057, .013, .010),
                                     (.102, .056, .008, .008)):
        section = ((-.70, -1), (.70, -1), (1, -.70), (1, .70),
                   (.70, 1), (-.70, 1), (-1, .70), (-1, -.70))
        ring = guard.ring(position(x, u * depth, length + v * breadth)
                          for u, v in section)
        if guard_rings:
            guard.bridge(guard_rings[-1], ring)
        guard_rings.append(ring)
    guard.face(tuple(reversed(guard_rings[0])))
    guard.face(guard_rings[-1])

    grip = _Part("sword_grip", "leather")
    _loft(grip, [position(0, 0, length) for length in (-.072, -.062, -.025, .025, .055)],
          [(.015, .017), (.016, .019), (.016, .018), (.014, .017), (.014, .016)],
          12, preferred=tuple(front))
    # Leather seam follows a continuous shallow helix; its mass is the grip,
    # while the hand is a separate connected surface grown around that grip.
    helix = []
    for index in range(57):
        t = index / 56
        angle = t * TAU * 4.0
        helix.append(position(.0166 * math.cos(angle), .0186 * math.sin(angle),
                              -.062 + .111 * t))
    _loft(grip, helix, [.0009] * len(helix), 4, preferred=tuple(front))

    pommel = _Part("sword_pommel", "steel")
    _loft(pommel, [position(0, 0, length) for length in
                   (-.104, -.101, -.086, -.072, -.066)],
          [(.010, .006), (.023, .011), (.026, .013), (.018, .010), (.015, .008)],
          12, preferred=tuple(width))
    return [blade.finish(armature, materials, collection, "hand_r", "front"),
            guard.finish(armature, materials, collection, "hand_r"),
            grip.finish(armature, materials, collection, "hand_r"),
            pommel.finish(armature, materials, collection, "hand_r")]


def _glove(armature, materials, collection, hand, side):
    """One connected closed palm/four-finger/thumb surface, with rigid skinning.

    Finger roots replace two adjacent palm faces and reuse their six boundary
    vertices. This is connected hand topology, not intersecting torus rings.
    The silver dorsum represents the reference's articulated gauntlet; the
    contact surfaces stay dark flexible leather.
    """
    mirror = -1 if side == "l" else 1
    handle = hand + Vector((-.005 if side == "r" else 0, .025, .033))
    palm_center = handle + Vector((-.022 * mirror, -.040, .005))
    glove = _Part("hand_grip_" + side, "leather")

    def world(x, y, z):
        return palm_center + Vector((x * mirror, y, z))

    profile = [(-.031, -.015), (0, -.020), (.027, -.015), (.036, 0),
               (.027, .017), (0, .022), (-.030, .015), (-.038, 0)]
    levels = [-.047, -.025, -.003, .019, .041, .063]
    rings = []
    for index, level in enumerate(levels):
        scale = (.85, 1, 1, 1, .92, .69)[index]
        ring = glove.ring(world(x * scale, y * scale, level) for x, y in profile)
        rings.append(ring)
    for level in range(len(levels) - 1):
        for edge in range(8):
            if level < 4 and edge in (2, 3):
                continue  # Four integrated finger roots, on the palm's inner edge.
            if level == 3 and edge in (6, 7):
                continue  # Opposing thumb grows from a true opening in the palm.
            glove.face((rings[level][edge], rings[level][(edge + 1) % 8],
                        rings[level + 1][(edge + 1) % 8], rings[level + 1][edge]),
                       "steel" if edge in (0, 1, 7) and level >= 1 else "leather")
    glove.face(tuple(reversed(rings[0])))
    glove.face(rings[-1], "leather")

    def branch(boundary, local_path, widths, heights):
        previous = boundary
        previous_lateral = None
        for index, local in enumerate(local_path):
            center = world(*local)
            old_center = sum((Vector(glove.vertices[v]) for v in previous),
                             Vector()) / len(previous)
            if index + 1 < len(local_path):
                following = world(*local_path[index + 1])
                tangent = (following - old_center).normalized()
            else:
                tangent = (center - old_center).normalized()
            vertical = Vector((0, 0, 1))
            vertical = (vertical - tangent * vertical.dot(tangent)).normalized()
            lateral = vertical.cross(tangent).normalized()
            # Match the palm boundary's direction before growing the first ring.
            if previous_lateral is None:
                probe = Vector(glove.vertices[boundary[2]]) - old_center
                if probe.dot(lateral) < 0:
                    lateral = -lateral
            elif previous_lateral.dot(lateral) < 0:
                lateral = -lateral
            previous_lateral = lateral
            # Twelve deliberately shaped sections round the knuckle silhouette.
            # The initial six root vertices remain shared with the palm; each
            # root edge opens into two section edges without splitting the hand.
            section = [(math.cos(math.radians(-150 + 30 * side)),
                        math.sin(math.radians(-150 + 30 * side)))
                       for side in range(12)]
            ring = glove.ring(center + lateral * (u * widths[index]) +
                              vertical * (v * heights[index]) for u, v in section)
            if index == 0:
                for side in range(6):
                    nxt = (side + 1) % 6
                    glove.face((previous[side], previous[nxt], ring[(2 * nxt) % 12],
                                ring[(2 * side + 1) % 12], ring[2 * side]))
            else:
                glove.bridge(previous, ring)
            previous = ring
        glove.face(previous, smooth=True)

    for finger in range(4):
        boundary = [rings[finger][2], rings[finger][3], rings[finger][4],
                    rings[finger + 1][4], rings[finger + 1][3],
                    rings[finger + 1][2]]
        z = (levels[finger] + levels[finger + 1]) * .5
        reach = (.81, .92, 1.0, .96)[finger]
        curl = (.004, .002, 0, -.001)[finger]
        branch(boundary,
               [(.041, .015, z), (.041, .037, z + curl),
                (.021, .060 * reach, z + curl), (-.003, .063 * reach, z),
                (-.023, .047 * reach, z - .002), (-.022, .030, z - .003)],
               [.015, .0145, .014, .013, .011, .008],
               [.0115, .012, .0118, .0113, .010, .007])
    thumb_boundary = [rings[3][6], rings[3][7], rings[3][0],
                      rings[4][0], rings[4][7], rings[4][6]]
    branch(thumb_boundary,
           [(-.044, .009, .034), (-.044, .025, .047),
            (-.034, .046, .043), (-.017, .064, .028), (.004, .064, .020)],
           [.016, .0155, .014, .012, .008], [.013, .013, .012, .010, .007])
    obj = glove.finish(armature, materials, collection, "hand_" + side)
    obj["aq1_hand_topology"] = "single connected palm, four rooted curled fingers and opposing thumb"
    obj["aq1_fixed_grip"] = True
    return obj


def build_equipment(armature, materials, collection):
    """Return Ada's new source equipment meshes; caller owns scene persistence.

    ``materials`` must contain steel, steel_dark, navy, gold and leather. The
    existing ``hand_r``/``hand_l`` rest bones drive the geometry without changing
    either their matrices or the seven actions. No legacy topology is selected
    or removed. Call only in an isolated, explicitly selected AQ1 candidate.
    """
    required = {"steel", "steel_dark", "navy", "gold", "leather"}
    if missing := required.difference(materials):
        raise ValueError("Missing AQ1 materials: " + ", ".join(sorted(missing)))
    if armature.type != "ARMATURE":
        raise ValueError("AQ1 equipment requires the existing candidate armature")
    for bone in ("hand_r", "hand_l"):
        if bone not in armature.data.bones:
            raise ValueError("Missing required Ada driver: " + bone)
    # World-space rest coordinates also support a translated candidate rig.
    hands = {side: armature.matrix_world @ armature.data.bones[
             "hand_" + side].tail_local for side in ("r", "l")}
    parts = _shield(armature, materials, collection, hands["l"])
    parts += _sword(armature, materials, collection, hands["r"])
    parts += [_glove(armature, materials, collection, hands[side], side)
              for side in ("r", "l")]
    return parts

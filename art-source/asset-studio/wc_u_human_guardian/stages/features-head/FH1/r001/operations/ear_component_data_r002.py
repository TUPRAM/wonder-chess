"""Original editable right-ear cage R002; geometry data only, no Blender dependency.

Coordinates use +X anatomical right, +Y front, +Z up, in meters.
The compact tables use millimeters for X/Y and millimeters above Z=1.674.
Rows are hand shaped anatomical contours, not sampled or projected skin.
The only open border is ROOT, intended for welding into the head.

R002 responds to the actual initial front/profile/three-quarter/underside
clay captures: taper posterior projection, separate the upper Y branches,
reduce cavity depth and lower rim fullness. Topology, Y/Z coordinates and
the exact attachment root are preserved. Revised pixels remain unreviewed.
"""

from collections import Counter, defaultdict
from math import cos, isfinite, pi, sin, sqrt


ROOT_VERTEX_COUNT = 20
Z_ORIGIN = 1.674

# Every row follows the same order: top, posterior, bottom, anterior.
# Each tuple is (X mm, Y mm, Z mm relative to Z_ORIGIN).
# The helix broadens out of the shell, and loses height as it reaches the lobe.
CONTOUR_ROWS_MM = (
    ('back_shell', (
        (82, -17, 27), (83, -24, 26), (84, -30, 22), (84, -35, 16),
        (85, -38, 8), (85, -38, 0), (85, -37, -8), (84, -33, -16),
        (83, -27, -22), (82, -21, -26), (81, -15, -27), (81, -9, -25),
        (81, -4, -22), (81, 0, -16), (81, 3, -9), (82, 4.8, -2),
        (82, 4.8, 6), (82, 2, 14), (82, -3, 20), (82, -10, 24),
    )),
    ('outer_silhouette', (
        (86.5, -18, 30), (88, -26, 29), (89, -33, 25), (90, -39, 18),
        (91, -42, 10), (91, -42, 1), (90.5, -40, -9), (89.5, -35, -18),
        (88, -28, -25), (86.5, -22, -29), (85.5, -15, -30), (84.5, -9, -28),
        (84, -4, -24), (84.5, 0, -18), (85, 3, -11), (85.5, 5, -3),
        (86, 6, 6), (86, 3, 15), (86, -2, 22), (86, -10, 27),
    )),
    ('helix_crest', (
        (90, -18, 28.5), (91.5, -25.5, 27.5), (93, -32, 23.5), (94, -37.5, 17),
        (94.5, -40.5, 9.5), (94.5, -40.5, 1), (94, -38.5, -8.5), (92.5, -33.5, -17),
        (89.5, -27.2, -23.5), (87.5, -21.5, -27), (86.5, -15, -28), (85.5, -9.5, -26),
        (85, -4.8, -22.5), (85.5, -0.8, -17), (86.5, 2, -10.5), (89, 3.5, -3),
        (90, 4.5, 5.5), (89, 1.5, 14), (89, -3, 21), (89, -10.5, 25.5),
    )),
    ('helix_inner_bank', (
        (88, -17.5, 26), (89.5, -24.8, 25.2), (90.5, -30.5, 21.5), (91.5, -35.5, 16),
        (92, -38.5, 9), (92, -38.5, 1), (91.5, -36.5, -8), (90, -32, -15.7),
        (88, -26, -21.5), (86.5, -21, -24.5), (86, -15, -25.5), (85.5, -10, -24),
        (85, -5.6, -20.5), (85.5, -1.7, -15.5), (86.5, 0.8, -10), (90, 2.2, -3.3),
        (90, 3, 5), (88, 0.4, 12.5), (88, -4, 18.8), (88, -11, 23),
    )),
    ('scapha_and_superior_crus', (
        (86, -17, 23), (93.5, -24, 21.5), (94, -28.8, 18.8), (89.5, -33, 14),
        (87.5, -35.5, 8), (87.5, -35, 1), (88, -33.7, -6.8), (88, -30, -13.5),
        (87, -24.7, -18.8), (86, -20, -22), (85.7, -15, -23), (85.5, -10.5, -21.5),
        (85.5, -6.2, -18.5), (86, -2.7, -14), (87, -0.2, -9.5), (91, 1, -4.5),
        (91, 1.5, 3), (87, -0.5, 10), (87, -4.5, 16), (85.5, -11.5, 20),
    )),
    ('antihelix_and_tragus', (
        (84.8, -16, 17), (85.5, -23, 16), (94, -28, 12), (94, -31, 8),
        (93.5, -32, 3), (93.5, -31, -2), (93, -29, -8), (91, -26, -13),
        (88.5, -23, -17), (86.5, -19, -20), (86, -14, -21), (86, -9.5, -19.5),
        (86.5, -5.7, -17), (86.5, -2.8, -13.3), (88, -1.1, -9.3), (92, 0, -6.7),
        (92, 0, -1), (89, -1.5, 5), (91, -5, 10), (92.5, -10, 13),
    )),
    ('concha_wall_and_inferior_crus', (
        (93, -14, 9), (93.5, -19, 8), (94, -24, 6), (89, -27.5, 3),
        (87, -29, 0), (86.5, -28, -3.5), (86.5, -26, -7.5), (87, -23.5, -11),
        (87.5, -21, -14), (86.5, -18, -16), (86, -14, -17), (86, -10.5, -16),
        (88, -7.3, -14), (86.5, -5, -11.5), (85.2, -3.5, -8), (88.5, -2, -5),
        (89.5, -2, -1), (89, -3.5, 3.5), (91, -6.5, 6.5), (92.5, -10, 8.5),
    )),
    ('concha_floor_border', (
        (86, -14, 5.5), (86, -18, 5), (86, -21, 3), (85.5, -22.5, 2),
        (85, -23.5, 0), (85, -24, -2), (85, -24, -5), (85.5, -23.5, -8),
        (86, -22, -11), (86, -19, -13), (85.5, -15, -14), (85.5, -11, -14),
        (86, -7.5, -13), (85.5, -5.2, -11), (85, -3.8, -8.2), (85, -3, -5),
        (85.5, -2.8, -1.5), (86, -3.5, 1.5), (86, -6, 3.8), (86, -10, 5),
    )),
)

# Four short rows across the bowl, posterior to anterior. These cap the last
# contour with quads and retain a broad depression rather than a pole/fan.
CONCHA_INTERIOR_MM = (
    ((85, -19.2, 1), (84.8, -15.5, 1.8), (84.8, -11.4, 1.8), (85.1, -7.1, 0.8)),
    ((84.7, -20, -2.6), (84.4, -16, -2.1), (84.3, -11.7, -2.1), (84.7, -7, -2.8)),
    ((84.8, -20.2, -6.2), (84.4, -16.3, -6), (84.2, -12, -6), (84.6, -7.6, -6.5)),
    ((85.2, -19.6, -9.6), (84.8, -16.2, -10.4), (84.6, -12.4, -10.8), (84.9, -8.7, -10)),
)


def _to_meters(point):
    return (point[0] * 0.001, point[1] * 0.001,
            Z_ORIGIN + point[2] * 0.001)


def build_ear():
    """Return a fresh 196-vertex/185-quad right ear, with ordered root indices.

    Use one Catmull-Clark subdivision for preview, keeping this cage editable.
    Weld ROOT to the head before judging attachment smoothness; an isolated
    subdivision preview may shrink the intended open attachment border.
    """
    vertices = []
    faces = []
    groups = {}
    root = []
    for i in range(ROOT_VERTEX_COUNT):
        angle = 2 * pi * i / ROOT_VERTEX_COUNT
        root.append(len(vertices))
        vertices.append(_to_meters((78, -15 - 19 * sin(angle),
                                   -0.5 + 23.5 * cos(angle))))
    groups["root_attachment"] = root[:]
    previous = root
    rows = {}
    for name, coordinates in CONTOUR_ROWS_MM:
        if len(coordinates) != ROOT_VERTEX_COUNT:
            raise ValueError("Each contour must have exactly 20 points")
        current = list(range(len(vertices), len(vertices) + len(coordinates)))
        vertices.extend(_to_meters(p) for p in coordinates)
        rows[name] = current
        groups[name] = current[:]
        for i in range(ROOT_VERTEX_COUNT):
            j = (i + 1) % ROOT_VERTEX_COUNT
            faces.append([previous[i], previous[j], current[j], current[i]])
        previous = current

    # The 20 boundary points form the perimeter of a 6x6 topological patch.
    # It is only a sparse local bowl cap, not a grid projected over the ear.
    grid = [[None] * 6 for _ in range(6)]
    for c, i in enumerate((2, 1, 0, 19, 18, 17)):
        grid[0][c] = previous[i]
    for r, i in enumerate((16, 15, 14, 13, 12), start=1):
        grid[r][5] = previous[i]
    for c, i in zip(range(4, -1, -1), (11, 10, 9, 8, 7)):
        grid[5][c] = previous[i]
    for r, i in zip(range(4, 0, -1), (6, 5, 4, 3)):
        grid[r][0] = previous[i]
    interior = []
    for r, coordinates in enumerate(CONCHA_INTERIOR_MM, start=1):
        for c, point in enumerate(coordinates, start=1):
            grid[r][c] = len(vertices)
            interior.append(len(vertices))
            vertices.append(_to_meters(point))
    for r in range(5):
        for c in range(5):
            faces.append([grid[r][c], grid[r + 1][c],
                          grid[r + 1][c + 1], grid[r][c + 1]])

    def indices(row_name, slots):
        return [rows[row_name][i] for i in slots]

    groups["concha_floor_interior"] = interior
    groups["antihelix_stem"] = indices("antihelix_and_tragus", (2, 3, 4, 5, 6))
    groups["antihelix_superior_crus"] = (
        indices("antihelix_and_tragus", (2,))
        + indices("scapha_and_superior_crus", (2, 1)))
    groups["antihelix_inferior_crus"] = (
        indices("antihelix_and_tragus", (2,))
        + indices("concha_wall_and_inferior_crus", (2, 1, 0, 19, 18)))
    groups["triangular_fossa"] = indices("antihelix_and_tragus", (0, 1))
    groups["tragus"] = (
        indices("helix_inner_bank", (15, 16))
        + indices("scapha_and_superior_crus", (15, 16))
        + indices("antihelix_and_tragus", (15, 16)))
    groups["intertragic_notch"] = (
        indices("antihelix_and_tragus", (14,))
        + indices("concha_wall_and_inferior_crus", (14,)))
    groups["antitragus"] = indices("concha_wall_and_inferior_crus", (12,))
    groups["lobe"] = [rows[name][i] for name, _ in CONTOUR_ROWS_MM[:6]
                      for i in (9, 10, 11, 12)]

    return {
        "vertices": vertices,
        "faces": faces,
        "root_loop": root[:],
        "named_vertex_groups": groups,
        "design_notes": [
            "Original hand-shaped cage for the portrait's small close adult ear.",
            "R002: posterior helix crest is 6.5 mm closer to the head; "
            "outer edge and inner bank taper toward the lower lobe.",
            "R002: lower adjacent upper-bank points separate the superior "
            "crus; a locally deeper triangular fossa divides the Y branches.",
            "R002: concha-floor minimum x=.0842 reduces the deep cup, while "
            "a reduced tragus and lobe preserve restrained ear proportions.",
            "Initial renders were visually inspected; R002 geometry has "
            "not been executed or visually accepted in Blender.",
            "Exactly 20 ordered open root vertices; planar x=.078, "
            "YZ bounds [-.034,.004] / [1.650,1.697].",
            "Broad connected pinna shell and back; no separate helix tube.",
            "Local raised branches divide the low triangular fossa from the "
            "lower anterior concha; the concha retains a broad quad floor.",
            "The lobe loses rim relief, with a restrained anterior tragus "
            "and lower notch; contours are subtly asymmetric in YZ.",
            "Recommended preview: one unapplied Catmull-Clark subdivision.",
            "Back shape and depth are inferred because the portrait does not "
            "show them. No ear-canal opening or separate internal anatomy.",
            "No Blender execution, deformation test, self-intersection "
            "certification, render inspection, or human art acceptance is "
            "claimed by this data module.",
        ],
    }


def audit_ear(mesh=None):
    """Audit combinatorial manifoldness and winding using pure Python math.

    Newell normals are checked for nonzero area. Shared edges must run in
    opposite directions. Positive closed volume uses a temporary reversed
    ROOT cap for the audit only; no cap is added to the returned cage.
    This does not certify subdivision quality or self-intersection freedom.
    """
    mesh = build_ear() if mesh is None else mesh
    vertices, faces, root = mesh["vertices"], mesh["faces"], mesh["root_loop"]
    edges = defaultdict(list)
    normal_lengths = []
    frontal_nonpositive = []
    diagonal_normal_folds = []
    for face_index, face in enumerate(faces):
        normal = [0.0, 0.0, 0.0]
        for a, b in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((a, b)))].append((a, b))
            p, q = vertices[a], vertices[b]
            normal[0] += (p[1] - q[1]) * (p[2] + q[2])
            normal[1] += (p[2] - q[2]) * (p[0] + q[0])
            normal[2] += (p[0] - q[0]) * (p[1] + q[1])
        normal_lengths.append(sqrt(sum(n * n for n in normal)))
        # Faces 60 onward run from the helix crest toward the bowl center.
        if face_index >= 60 and normal[0] <= 0:
            frontal_nonpositive.append(face_index)
        if len(face) == 4:
            p, q, r, s = [vertices[i] for i in face]
            u = tuple(q[k] - p[k] for k in range(3))
            v = tuple(r[k] - p[k] for k in range(3))
            w = tuple(s[k] - p[k] for k in range(3))
            first = (u[1] * v[2] - u[2] * v[1],
                     u[2] * v[0] - u[0] * v[2],
                     u[0] * v[1] - u[1] * v[0])
            second = (v[1] * w[2] - v[2] * w[1],
                      v[2] * w[0] - v[0] * w[2],
                      v[0] * w[1] - v[1] * w[0])
            if (sum(first[k] * second[k] for k in range(3)) <= 0
                    or (face_index >= 60 and
                        (first[0] <= 0 or second[0] <= 0))):
                diagonal_normal_folds.append(face_index)
    expected_boundary = {tuple(sorted((a, b)))
                         for a, b in zip(root, root[1:] + root[:1])}
    boundary = {edge for edge, uses in edges.items() if len(uses) == 1}
    winding_errors = [edge for edge, uses in edges.items()
                      if len(uses) == 2 and uses[0] != uses[1][::-1]]
    volume = 0.0
    origin = (0.078, -0.015, Z_ORIGIN)
    for face in faces + [list(reversed(root))]:
        a = tuple(vertices[face[0]][k] - origin[k] for k in range(3))
        for j in range(1, len(face) - 1):
            b = tuple(vertices[face[j]][k] - origin[k] for k in range(3))
            c = tuple(vertices[face[j + 1]][k] - origin[k] for k in range(3))
            volume += (a[0] * (b[1] * c[2] - b[2] * c[1])
                       + a[1] * (b[2] * c[0] - b[0] * c[2])
                       + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return {
        "vertex_count": len(vertices),
        "face_count": len(faces),
        "face_sizes": dict(Counter(map(len, faces))),
        "edge_count": len(edges),
        "edge_incidence_histogram": dict(Counter(map(len, edges.values()))),
        "root_count": len(root),
        "boundary_matches_root_exactly": boundary == expected_boundary,
        "nonmanifold_edges_excluding_root": [edge for edge, uses in edges.items()
                                             if edge not in expected_boundary
                                             and len(uses) != 2],
        "shared_edge_winding_errors": winding_errors,
        "degenerate_faces": [i for i, length in enumerate(normal_lengths)
                             if length < 1e-12],
        "front_faces_with_nonpositive_x_normal": frontal_nonpositive,
        "quad_diagonal_normal_fold_faces": diagonal_normal_folds,
        "all_coordinates_finite": all(isfinite(c) for p in vertices for c in p),
        "euler_characteristic": len(vertices) - len(edges) + len(faces),
        "minimum_face_area_m2": min(normal_lengths) * 0.5,
        "root_capped_signed_volume_m3": volume,
        "bounds_m": [[min(p[k] for p in vertices), max(p[k] for p in vertices)]
                     for k in range(3)],
        "root_bounds_m": [[min(vertices[i][k] for i in root),
                           max(vertices[i][k] for i in root)] for k in range(3)],
        "visual_status": "not_executed_or_reviewed_in_Blender",
    }

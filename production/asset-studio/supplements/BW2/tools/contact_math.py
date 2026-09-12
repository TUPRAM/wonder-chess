"""BW2 standalone geometry checks. No bpy, scene mutation, IK, or art approval.

Coordinates are explicitly world-space metres. Synthetic examples are not Ada data.
Rigid-transform helpers intentionally reject reflection, scale and shear.
"""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

Vec3 = tuple[float, float, float]
EPS = 1e-12


def vec(value: Sequence[float]) -> Vec3:
    if len(value) != 3:
        raise ValueError('Expected a three-component vector')
    if any(isinstance(x, bool) for x in value):
        raise ValueError('Boolean coordinates are invalid')
    v = tuple(float(x) for x in value)
    if not all(math.isfinite(x) for x in v):
        raise ValueError('Coordinates must be finite')
    return v  # type: ignore[return-value]


def add(a, b): return tuple(x+y for x, y in zip(a, b))
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def scale(a, s): return tuple(x*s for x in a)
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def norm(a): return math.sqrt(dot(a, a))
def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def unit(a):
    n = norm(a)
    if n <= EPS:
        raise ValueError('Degenerate direction; remeasure landmarks')
    return scale(a, 1/n)


@dataclass(frozen=True)
class HandFrame:
    origin_m: Vec3
    x_transverse: Vec3
    y_distal: Vec3
    z_palmar: Vec3
    x_points_toward_index: bool

    def to_world(self, local_m: Sequence[float]) -> Vec3:
        p = vec(local_m)
        return add(self.origin_m, add(scale(self.x_transverse, p[0]),
                   add(scale(self.y_distal, p[1]), scale(self.z_palmar, p[2]))))

    def to_local(self, world_m: Sequence[float]) -> Vec3:
        d = sub(vec(world_m), self.origin_m)
        return (dot(d, self.x_transverse), dot(d, self.y_distal), dot(d, self.z_palmar))

    def matrix_rows(self):
        # Column-vector convention: columns 0..2 are axes, column 3 is translation.
        return [[self.x_transverse[i], self.y_distal[i], self.z_palmar[i], self.origin_m[i]]
                for i in range(3)] + [[0.0, 0.0, 0.0, 1.0]]


def hand_frame(*, wrist, middle_mcp, index_mcp, little_mcp, middle_tip, palmar_point) -> HandFrame:
    """Build once from a neutral open hand; do not rebuild from curled tips.

    MCP means finger-base joint, not Model Context Protocol. palmar_point is a
    labeled point on the palm-side surface, not another joint in the palm plane.
    X changes anatomical sign between hands as needed to keep a proper rotation.
    """
    w, m, i, l, t, p = map(vec, (wrist, middle_mcp, index_mcp, little_mcp, middle_tip, palmar_point))
    y = unit(sub(m, w))
    finger = unit(sub(t, m))
    if dot(y, finger) < 0.25:
        raise ValueError('Open-hand distal-direction check failed; wrong labels/frame/pose')
    radial = sub(i, l)
    radial_norm = norm(radial)
    transverse = sub(radial, scale(y, dot(radial, y)))
    if radial_norm <= EPS or norm(transverse)/radial_norm < 0.2:
        raise ValueError('Finger-base landmarks nearly collinear with distal axis')
    x = unit(transverse)
    z = unit(cross(x, y))
    palm_hint = sub(p, scale(add(w, m), 0.5))
    if norm(palm_hint) <= EPS or abs(dot(z, unit(palm_hint))) < 0.1:
        raise ValueError('Palm-side marker does not disambiguate palmar/dorsal direction')
    if dot(z, palm_hint) < 0:
        x, z = scale(x, -1), scale(z, -1)
    frame = HandFrame(w, x, y, z, dot(x, radial) > 0)
    validate_rigid(frame.matrix_rows())
    return frame


def validate_rigid(matrix: Sequence[Sequence[float]], tol=1e-7):
    if len(matrix) != 4 or any(len(row) != 4 for row in matrix):
        raise ValueError('Expected 4x4 matrix')
    m = [[float(v) for v in row] for row in matrix]
    if not all(math.isfinite(v) for row in m for v in row):
        raise ValueError('Nonfinite matrix')
    if max(abs(m[3][j] - (1 if j==3 else 0)) for j in range(4)) > tol:
        raise ValueError('Not an affine column-vector transform')
    axes = [tuple(m[i][j] for i in range(3)) for j in range(3)]
    if any(abs(dot(axes[i], axes[j]) - (1 if i==j else 0)) > tol
           for i in range(3) for j in range(3)):
        raise ValueError('Scale/shear present; this helper only supports rigid transforms')
    if abs(dot(axes[0], cross(axes[1], axes[2]))-1) > tol:
        raise ValueError('Reflected or invalid frame; determinant must be +1')
    return m


def apply_point(matrix, point):
    m, p = validate_rigid(matrix), vec(point)
    return tuple(sum(m[i][j]*p[j] for j in range(3))+m[i][3] for i in range(3))


def inverse_rigid(matrix):
    m = validate_rigid(matrix)
    r = [[m[j][i] for j in range(3)] for i in range(3)]
    t = [m[i][3] for i in range(3)]
    return [r[i]+[-sum(r[i][j]*t[j] for j in range(3))] for i in range(3)] + [[0,0,0,1]]


def multiply(a, b):
    a, b = validate_rigid(a), validate_rigid(b)
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def relative_transform(parent_world, child_world):
    return multiply(inverse_rigid(parent_world), child_world)


def cylinder_sample(point, start, end, radius_m):
    """Exact signed distance to a closed finite ideal circular cylinder.

    Negative=inside. side_gap is ONLY radial distance; inspect axial position.
    Does not inspect the rest of a mesh, triangle crossings, or finger contacts.
    """
    p, a, b = map(vec, (point, start, end))
    r = float(radius_m)
    if not math.isfinite(r) or r <= 0:
        raise ValueError('Cylinder radius must be finite and positive')
    direction = sub(b, a); length = norm(direction); u = unit(direction)
    q = sub(p, a); axial = dot(q, u)
    radial = norm(sub(q, scale(u, axial)))
    d0, d1 = radial-r, abs(axial-length/2)-length/2
    sdf = min(max(d0, d1), 0.0) + math.hypot(max(d0, 0.0), max(d1, 0.0))
    return {'signed_distance_m': sdf, 'side_gap_m': d0, 'axial_m': axial,
            'length_m': length, 'within_axial_span': 0 <= axial <= length}


def percentile(values: Sequence[float], fraction: float):
    if not values or not 0 <= fraction <= 1:
        raise ValueError('Nonempty sample and fraction in [0,1] required')
    v = sorted(values)
    pos = (len(v)-1)*fraction; lo = math.floor(pos); hi = math.ceil(pos)
    return v[lo] + (v[hi]-v[lo])*(pos-lo)


def screen_patch(points: Iterable[Sequence[float]], start, end, radius_m,
                 gap_m=0.001, penetration_m=0.0005, min_fraction=0.5, end_margin_m=0.002):
    """Provisional numeric screen only; no visual approval and no mesh certification.

    Supply small, predeclared contact-pad patches, not arbitrary nearest vertices.
    All points must be inside the usable axial range; cap contact is not a grip.
    """
    if any(not math.isfinite(v) for v in [gap_m, penetration_m, min_fraction, end_margin_m]):
        raise ValueError('Finite tolerances required')
    if gap_m < 0 or penetration_m < 0 or not 0 <= min_fraction <= 1 or end_margin_m < 0:
        raise ValueError('Invalid tolerances')
    samples = [cylinder_sample(p, start, end, radius_m) for p in points]
    if not samples:
        raise ValueError('A contact patch must contain samples')
    length = samples[0]['length_m']
    if 2*end_margin_m >= length:
        raise ValueError('Cylinder too short for selected end margin')
    distances = [s['side_gap_m'] for s in samples]
    axial_ok = all(end_margin_m <= s['axial_m'] <= length-end_margin_m for s in samples)
    contact_fraction = sum(-penetration_m <= d <= gap_m for d in distances)/len(distances)
    passed = axial_ok and min(distances) >= -penetration_m and contact_fraction >= min_fraction
    return {
        'status': 'PASS_SAMPLED_NUMERIC_SCREEN' if passed else 'REVISE_NUMERIC_SCREEN',
        'samples': len(samples), 'contact_fraction': contact_fraction, 'axial_region_valid': axial_ok,
        'min_gap_mm': min(distances)*1000, 'median_gap_mm': percentile(distances,0.5)*1000,
        'p95_gap_mm': percentile(distances,0.95)*1000, 'max_gap_mm': max(distances)*1000,
        'max_sampled_penetration_mm': max(0,-min(distances))*1000,
        'visual_approval': False,
        'limits': 'Only supplied points against an ideal cylinder; not continuous mesh collision, gripping-force, motion, or art validation.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('landmarks', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.landmarks.read_text(encoding='utf-8'))
        if payload.get('coordinate_space') != 'WORLD_METERS' or payload.get('pose_kind') != 'OPEN_CALIBRATION':
            raise ValueError('Require WORLD_METERS and OPEN_CALIBRATION declarations')
        frame = hand_frame(**payload['landmarks'])
        result = {'frame': asdict(frame), 'matrix_rows': frame.matrix_rows(),
                  'input_example_only': payload.get('example_only', True),
                  'measured_asset_validation': False, 'art_approval': False}
        if 'cylinder' in payload:
            c = payload['cylinder']
            result['patch_screens'] = {name: screen_patch(points,c['start_m'],c['end_m'],c['radius_m'])
                                      for name,points in payload.get('contact_patches',{}).items()}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf-8') as f:
            json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
        print(f'Wrote numerical diagnostic only: {args.output}')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())

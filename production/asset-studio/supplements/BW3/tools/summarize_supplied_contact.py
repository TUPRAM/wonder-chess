"""Read BW2 JSON measurements. No Blender invocation, geometry test, or art approval.

python tools/summarize_supplied_contact.py evidence/BW2_contact_measurements.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def summarize(data: dict[str, Any], threshold_mm: float = 0.5) -> dict[str, Any]:
    if isinstance(threshold_mm, bool) or not math.isfinite(threshold_mm) or threshold_mm < 0:
        raise ValueError('threshold_mm must be a finite nonnegative number')
    frames = data.get('frames')
    held = data.get('carry_spec', {}).get('held_frames')
    if not isinstance(frames, list) or not frames:
        raise ValueError('Missing nonempty frames array')
    if not isinstance(held, list) or len(held) != 2 or any(type(v) is not int for v in held):
        raise ValueError('carry_spec.held_frames must be [first, last] integers')
    if held[0] < 1 or held[1] < held[0]:
        raise ValueError('Invalid held interval')
    seen: set[int] = set()
    rows = []
    for item in frames:
        f = item.get('frame')
        if type(f) is not int or f < 1 or f in seen:
            raise ValueError('Frame IDs must be unique positive integers')
        seen.add(f)
        s = item.get('whole_right_glove_vertex_screen', {})
        depth = s.get('maximum_sampled_penetration_mm')
        if isinstance(depth, bool) or not isinstance(depth, (float, int)) or not math.isfinite(depth) or depth < 0:
            raise ValueError(f'Frame {f}: missing/invalid measured vertex penetration')
        rows.append({'frame': f, 'max_vertex_penetration_mm': float(depth),
                     'vertices_over_threshold_reported': s.get('sampled_vertices_deeper_than_0_5mm') if threshold_mm == 0.5 else None,
                     'source_phase_label': item.get('phase'),
                     'worst_evaluated_vertex': s.get('worst', {}).get('evaluated_vertex')})
    rows.sort(key=lambda x: x['frame'])
    if seen != set(range(1, len(rows) + 1)) or held[1] > len(rows):
        raise ValueError('This analyzer requires the complete dense timeline starting at frame 1')
    if data.get('frame_count') != len(rows):
        raise ValueError('Declared frame_count differs from measured frames')
    if data.get('held_frame_count') != held[1] - held[0] + 1:
        raise ValueError('Declared held_frame_count differs from held interval')
    def window(a: int, b: int) -> dict[str, Any]:
        selected = [r for r in rows if a <= r['frame'] <= b]
        if not selected:
            return {'frame_start': a, 'frame_end': b, 'frame_count': 0, 'status': 'NOT_PRESENT'}
        failures = [r['frame'] for r in selected if r['max_vertex_penetration_mm'] > threshold_mm]
        worst = max(selected, key=lambda r: r['max_vertex_penetration_mm'])
        return {'frame_start': a, 'frame_end': b, 'frame_count': len(selected),
                'frames_over_threshold': failures, 'count_over_threshold': len(failures),
                'maximum_vertex_penetration_mm': worst['max_vertex_penetration_mm'],
                'maximum_at_frame': worst['frame'],
                'worst_evaluated_vertex_at_maximum': worst['worst_evaluated_vertex'],
                'status': 'FAIL_SAMPLED_PENETRATION_SCREEN' if failures else 'WITHIN_SAMPLED_PENETRATION_SCREEN_ONLY'}
    return {'analysis_type': 'READ_ONLY_SUPPLIED_MEASUREMENTS_NOT_NEW_GEOMETRY_EVALUATION',
            'threshold_mm': threshold_mm,
            'closure': window(1, held[0] - 1),
            'held': window(held[0], held[1]),
            'full_timeline': window(1, len(rows)),
            'closure_rows': [r for r in rows if r['frame'] < held[0]],
            'limitations': ['Vertex-vs-ideal-cylinder samples, not full triangle or continuous-time collision tests.',
                           'This does not compute hand self-intersections or identify which anatomical region contains the worst vertex.',
                           'Contact is not required before closure, but that phase label does not excuse penetration.',
                           'No artistic, runtime, human, or recipe approval can be produced by this analyzer.']}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--threshold-mm', type=float, default=0.5)
    args = p.parse_args()
    try:
        raw = args.source.read_bytes()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError('Root must be a JSON object')
        result = summarize(data, args.threshold_mm)
        result['input_sha256'] = hashlib.sha256(raw).hexdigest()
        print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(2, f'Input error: {exc}\n')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

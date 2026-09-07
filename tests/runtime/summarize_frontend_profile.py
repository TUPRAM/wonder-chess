"""Join actual native profile markers to frame rows, retaining navigation hitches."""
import argparse
from collections import Counter, defaultdict
import csv
import io
import json
import math
from pathlib import Path

from summarize_frame_evidence import TIMINGS, _read, metrics, summarize


def analyze(profile_path, session_path, context_paths=()):
    profile_path, session_path = Path(profile_path), Path(session_path)
    base = summarize(session_path, context_paths)
    inputs = base['inputs']
    profile = json.loads(_read(profile_path, inputs))
    session = json.loads(_read(session_path, inputs))
    if session['match_namespace'] != 0 or profile['pid'] != session['process_id']:
        raise ValueError('Profile must bind the same namespace-zero process')
    frame_path = Path(base['source']['csv_path'])
    if Path(profile['frame_csv']).resolve() != frame_path.resolve():
        raise ValueError('Profile CSV identity differs from the session')
    marker_path = Path(profile['markers_jsonl'])
    if marker_path.resolve().parent != profile_path.resolve().parent:
        raise ValueError('Profile markers must belong to this evidence directory')
    markers = [json.loads(line) for line in _read(marker_path, inputs).splitlines() if line.strip()]
    for before, after in zip(markers, markers[1:]):
        if after['frame_counter'] < before['frame_counter'] or after['wall_seconds'] < before['wall_seconds']:
            raise ValueError('Profile marker clock moved backwards')
    reader = csv.DictReader(io.StringIO(_read(frame_path, inputs)))
    required = {'frame_counter', 'wall_seconds', 'frontend_page', 'phase', 'gpu_available', *TIMINGS}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('Profile CSV lacks explicit frame/page fields')
    rows = []
    for record in reader:
        row = {'frontend_page': record['frontend_page'].strip().lower()}
        for key in required - {'frontend_page'}:
            try:
                row[key] = float(record[key])
            except (TypeError, ValueError):
                row[key] = None
        for key in ('frame_counter', 'wall_seconds', 'phase'):
            if row[key] is None or not math.isfinite(row[key]):
                raise ValueError('Invalid profile frame identity')
        if row['frame_counter'] != int(row['frame_counter']):
            raise ValueError('Noninteger frame counter')
        if rows and (row['frame_counter'] <= rows[-1]['frame_counter'] or row['wall_seconds'] < rows[-1]['wall_seconds']):
            raise ValueError('Duplicate or backwards profile frame')
        rows.append(row)

    def measure(selected):
        result = {'frames': len(selected)}
        for field in TIMINGS:
            values = [row[field] for row in selected if row[field] is not None and math.isfinite(row[field])
                      and (row[field] > 0 if field in ('frame_ms', 'gpu_ms') else row[field] >= 0)
                      and (field != 'gpu_ms' or not base['instrumentation']['null_rhi'] and row['gpu_available'] == 1)]
            result[field] = {**metrics(values), 'unavailable_or_invalid_samples': len(selected) - len(values)}
        return result

    by_stage = defaultdict(dict)
    for marker in markers:
        if 'stage' not in marker:
            continue
        event = marker['event']
        if event not in ('action_begin', 'action_return', 'measure_begin', 'measure_end'):
            raise ValueError('Unknown stage marker event: ' + event)
        if event in by_stage[marker['stage']]:
            raise ValueError('Duplicate stage marker: ' + marker['stage'] + '/' + event)
        by_stage[marker['stage']][event] = marker
    output_stages, steady_ids, boundary_ids, transition_ids = [], set(), set(), set()
    groups = defaultdict(list)
    incomplete = []
    for label, events in by_stage.items():
        if set(events) != {'action_begin', 'action_return', 'measure_begin', 'measure_end'}:
            incomplete.append(label)
            continue
        action, returned, begin, end = (events[key] for key in ('action_begin', 'action_return', 'measure_begin', 'measure_end'))
        identity = ('stage_index', 'stage', 'frontend_page', 'hero_id', 'clip', 'visit', 'requested_dwell_seconds')
        if any(any(marker[key] != action[key] for key in identity) for marker in (returned, begin, end)):
            raise ValueError('Stage identity changed between markers: ' + label)
        if any(marker['actual_frontend_page'] != marker['frontend_page'] for marker in (returned, begin, end)):
            raise ValueError('Actual page differs from expected stage: ' + label)
        if not action['frame_counter'] <= returned['frame_counter'] <= begin['frame_counter'] < end['frame_counter']:
            raise ValueError('Invalid stage marker order: ' + label)
        if end['wall_seconds'] - begin['wall_seconds'] + 1e-6 < begin['requested_dwell_seconds']:
            raise ValueError('Completed stage shorter than declared dwell: ' + label)
        steady = [row for row in rows if begin['frame_counter'] + 1 < row['frame_counter'] <= end['frame_counter']]
        if any(row['frontend_page'] != begin['frontend_page'] or row['phase'] != -1 for row in steady):
            raise ValueError('Settled interval contains another page or a running match: ' + label)
        ids = {row['frame_counter'] for row in steady}
        if steady_ids & ids:
            raise ValueError('Overlapping settled intervals')
        steady_ids.update(ids)
        boundary = [row for row in rows if begin['frame_counter'] < row['frame_counter'] <= begin['frame_counter'] + 1]
        transition = [row for row in rows if action['frame_counter'] < row['frame_counter'] <= begin['frame_counter']]
        boundary_ids.update(row['frame_counter'] for row in boundary)
        transition_ids.update(row['frame_counter'] for row in transition)
        groups[(begin['frontend_page'], begin['visit'])].extend(steady)
        output_stages.append({key: begin[key] for key in identity} | {
            'settling_seconds': begin['wall_seconds'] - returned['wall_seconds'],
            'measured_dwell_seconds': end['wall_seconds'] - begin['wall_seconds'],
            'steady': measure(steady), 'first_post_marker': measure(boundary),
            'navigation_and_settling': measure(transition)})
    if len(output_stages) != profile['completed_stages']:
        raise ValueError('Completed profile count differs from completed marker intervals')
    detail = [stage for stage in output_stages if stage['frontend_page'] == 'detail']
    coverage = Counter((stage['hero_id'], stage['clip'], stage['visit']) for stage in detail)
    heroes = {stage['hero_id'] for stage in detail}
    visits = ('first_detail_presentation', 'warm_revisit')
    pages = Counter(stage['frontend_page'] for stage in output_stages)
    full_coverage = (profile.get('expected_stages') == 103 and len(output_stages) == 103
                     and pages == Counter(detail=96, lobby=4, gallery=3) and len(heroes) == 24 and len(detail) == 96
                     and all(coverage[(hero, clip, visit)] == 1 for hero in heroes for clip in ('Idle', 'Active') for visit in visits))
    route_complete = profile['status'] == 'PASS_ROUTE_EXECUTION_ONLY' and not incomplete and full_coverage
    accounted = steady_ids | boundary_ids | transition_ids
    return {
        'status': 'OBSERVED_COMPLETE_ROUTE' if route_complete else 'OBSERVED_PARTIAL_ROUTE',
        'boundary': 'Measured instrumented first UI/detail presentation and warm revisit; not cold startup, uninstrumented performance, visual approval or manual interaction. Navigation and boundary hitches are retained separately.',
        'profile_status': profile['status'], 'profile_failure': profile.get('failure'),
        'content_digest': profile['content_digest'], 'protocol_version': profile['protocol_version'],
        'animation_workload': profile.get('animation_workload'), 'saved_preferences_unchanged': profile.get('saved_preferences_unchanged'),
        'complete_24_hero_idle_active_twice': full_coverage, 'incomplete_stages': incomplete,
        'hardware_and_settings': base['hardware_and_settings'], 'instrumentation': base['instrumentation'],
        'join_rule': 'steady: begin.frame_counter+1 < row.frame_counter <= end.frame_counter, actual matching page and phase -1',
        'all_recorded_frames': measure(rows), 'all_settled_frames': measure([r for r in rows if r['frame_counter'] in steady_ids]),
        'all_navigation_and_settling': measure([r for r in rows if r['frame_counter'] in transition_ids]),
        'all_first_post_marker': measure([r for r in rows if r['frame_counter'] in boundary_ids]),
        'unassigned_startup_partial_or_tail': measure([r for r in rows if r['frame_counter'] not in accounted]),
        'page_visit_groups': [{'frontend_page': page, 'visit': visit, **measure(selected)} for (page, visit), selected in sorted(groups.items())],
        'stages': output_stages, 'inputs': inputs,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', type=Path)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--context-evidence', type=Path, action='append', default=[])
    args = parser.parse_args()
    result = analyze(args.profile, args.session, args.context_evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'completed_stages': len(result['stages']), 'output': str(args.output)}, indent=2))

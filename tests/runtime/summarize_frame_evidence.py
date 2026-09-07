"""Summarize measured WCVerification frames without inferring unrecorded loads or pages."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

TIMINGS = ('frame_ms', 'game_ms', 'render_ms', 'gpu_ms')
PAGES = {'lobby', 'mode', 'gallery', 'detail', 'settings', 'closed'}


def windows_arguments(command_line):
    """Read a retained Windows command line without executing it or losing quoted paths."""
    arguments, current, quoted, index = [], [], False, 0
    while index < len(command_line):
        char = command_line[index]
        if char.isspace() and not quoted:
            if current:
                arguments.append(''.join(current))
                current = []
            index += 1
            continue
        if char == '\\':
            end = index
            while end < len(command_line) and command_line[end] == '\\':
                end += 1
            count = end - index
            if end < len(command_line) and command_line[end] == '"':
                current.extend('\\' * (count // 2))
                if count % 2:
                    current.append('"')
                else:
                    quoted = not quoted
                index = end + 1
            else:
                current.extend('\\' * count)
                index = end
            continue
        if char == '"':
            quoted = not quoted
        else:
            current.append(char)
        index += 1
    if quoted:
        raise ValueError('Unterminated quote in retained Windows launch arguments')
    if current:
        arguments.append(''.join(current))
    return arguments


def metrics(values):
    values = sorted(value for value in values if value is not None and math.isfinite(value) and value >= 0)
    if not values:
        return {'status': 'NOT_RUN', 'samples': 0, 'p50_ms': None, 'p95_ms': None,
                'p99_ms': None, 'max_ms': None, 'frames_over_33_33ms': None, 'frames_over_100ms': None}
    return {'status': 'OBSERVED', 'samples': len(values),
            **{f'p{p}_ms': values[int((len(values) - 1) * p / 100)] for p in (50, 95, 99)},
            'max_ms': values[-1], 'frames_over_33_33ms': sum(value > 100 / 3 for value in values),
            'frames_over_100ms': sum(value > 100 for value in values)}


def _read(path, inputs):
    before = path.stat()
    content = path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Evidence changed while reading: ' + str(path))
    identity = {'path': str(path.resolve()), 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
    if identity not in inputs:
        inputs.append(identity)
    return content.decode('utf-8-sig')


def summarize(session_path, context_paths=()):
    session_path = Path(session_path)
    inputs = []
    session = json.loads(_read(session_path, inputs))
    namespace = session['match_namespace']
    prefix = f"match-{namespace}-seat-{session['seat']}-pid-{session['process_id']}"
    frame_path = session_path.parent / (prefix + '-frames.csv')
    rows, columns = [], []
    missing_frame_file = not frame_path.is_file()
    if not missing_frame_file:
        reader = csv.DictReader(io.StringIO(_read(frame_path, inputs)))
        columns = reader.fieldnames or []
        required = {'wall_seconds', 'phase', 'visible_alive', 'encounters', *TIMINGS, 'gpu_available'}
        if not required.issubset(columns):
            raise ValueError('Frame CSV lacks required columns: ' + ', '.join(sorted(required - set(columns))))
        for index, record in enumerate(reader, 2):
            if None in record:
                raise ValueError(f'{frame_path}:{index}: extra CSV fields')
            row = {}
            for key, value in record.items():
                if value is None:
                    raise ValueError(f'{frame_path}:{index}: truncated CSV row')
                if key == 'frontend_page':
                    row[key] = value.strip().lower()
                    continue
                try:
                    row[key] = float(value) if value.strip().lower() not in ('', 'null', 'none', 'unavailable') else None
                except ValueError as error:
                    raise ValueError(f'{frame_path}:{index}: nonnumeric {key}') from error
            if any(row.get(key) is None or not math.isfinite(row[key]) for key in ('wall_seconds', 'phase', 'visible_alive', 'encounters')):
                raise ValueError(f'{frame_path}:{index}: missing or invalid load identity')
            rows.append(row)

    launch_path = session_path.parent / 'launch.json'
    launch = json.loads(_read(launch_path, inputs)) if launch_path.is_file() else {}
    arguments = launch.get('arguments', [])
    if isinstance(arguments, str):
        arguments = windows_arguments(arguments)
    options = {value.lower() for value in arguments}
    null_rhi = bool(launch.get('null_rhi')) or '-nullrhi' in options or 'null' in str(session.get('rhi', '')).lower()
    capture_flags = [value for value in arguments if value.lower() in ('-wcshots', '-wcprojectedbounds', '-wcfrontendaudit', '-wcfrontendallheroes')]
    contexts = []
    for path in context_paths:
        path = Path(path)
        content = json.loads(_read(path, inputs))
        contexts.append({'path': str(path.resolve()), **{key: content.get(key) for key in
                        ('boundary', 'status', 'utc', 'started_utc', 'ended_utc', 'process_id', 'pid', 'arguments')}})

    neutral_available = {'neutral_round', 'neutral_live_encounters'}.issubset(columns)
    page_available = 'frontend_page' in columns
    combat = [row for row in rows if row['phase'] == 1]
    neutral = [row for row in combat if row.get('neutral_round') == 1]
    pvp = [row for row in combat if row.get('neutral_round') == 0]
    eight_neutral = [row for row in neutral if row.get('neutral_live_encounters') == 8 and row['encounters'] == 8]
    frontend = [row for row in rows if namespace == 0 and row['phase'] == -1]
    subsets = {
        'all_profiled_frames': rows,
        'frontend_namespace0_frames': frontend,
        'lobby_frames': [row for row in frontend if row.get('frontend_page') == 'lobby'],
        'gallery_list_frames': [row for row in frontend if row.get('frontend_page') == 'gallery'],
        'hero_detail_frames': [row for row in frontend if row.get('frontend_page') == 'detail'],
        'gallery_and_detail_frames': [row for row in frontend if row.get('frontend_page') in ('gallery', 'detail')],
        'mode_or_entry_frames': [row for row in frontend if row.get('frontend_page') == 'mode'],
        'settings_frames': [row for row in frontend if row.get('frontend_page') == 'settings'],
        'active_tournament_frames': [row for row in rows if namespace > 0 and row['phase'] in (0, 1, 2)],
        'combat_frames': combat,
        'neutral_combat_frames': neutral,
        'pvp_combat_frames': pvp,
        'twelve_visible_combatants': [row for row in combat if row['visible_alive'] >= 12],
        'twelve_visible_and_four_live_encounters': [row for row in combat if row['visible_alive'] >= 12 and row['encounters'] == 4],
        'twelve_visible_and_four_live_pvp_encounters': [row for row in pvp if row['visible_alive'] >= 12 and row['encounters'] == 4],
        'eight_live_neutral_encounters': eight_neutral,
        'twelve_visible_and_eight_live_neutral_encounters': [row for row in eight_neutral if row['visible_alive'] >= 12],
    }
    result = {
        'status': 'OBSERVED_PRELIMINARY' if rows else 'NOT_RUN',
        'boundary': 'Actual instrumented samples only; no inferred hardware, FPS, missing load, or final performance acceptance. CPU timings under NullRHI do not represent rendered gameplay.',
        'hardware_and_settings': {key: session.get(key) for key in
                                 ('cpu', 'active_rhi_adapter', 'primary_gpu_reported_by_os', 'engine', 'rhi', 'render_settings',
                                  'resolution_x', 'resolution_y', 'simulation_speed_multiplier', 'peak_process_physical_bytes', 'gpu_timing_source')},
        'source': {'match_namespace': namespace, 'seat': session['seat'], 'process_id': session['process_id'],
                   'csv_path': str(frame_path.resolve()), 'csv_missing': missing_frame_file,
                   'header_only': not missing_frame_file and not rows, 'columns': columns, 'rows': len(rows)},
        'percentile_method': 'Sorted sample at floor((n-1)*percentile/100), without interpolation; compatible with prior reports.',
        'hitch_thresholds': {'frames_over_33_33ms': 'strictly greater than 100/3 ms', 'frames_over_100ms': 'strictly greater than 100 ms'},
        'instrumentation': {'launch_record_present': bool(launch), 'profile_flag_recorded': '-wcprofile' in options,
                            'null_rhi': null_rhi, 'capture_flags': capture_flags,
                            'launch_arguments': arguments, 'launch_boundary': launch.get('boundary'),
                            'launch_arguments_raw': launch.get('arguments'),
                            'ambient_editor_processes': launch.get('ambient_editor_processes', launch.get('ambient_processes')),
                            'declared_confounders': launch.get('profiling_confounders'),
                            'context_evidence': contexts,
                            'gpu_sample_policy': 'Require rendered RHI, gpu_available=1 and a finite positive gpu_ms value. Zero, null, invalid and unavailable samples never become zero-cost GPU observations.',
                            'performance_acceptance': 'NOT_ASSESSED; captures, asset traversal/loading, concurrent workloads and accelerated simulation may affect these samples.'},
        'frontend_page_coverage': {'column_available': page_available,
                                   'combined_namespace0_status': 'OBSERVED' if frontend else 'NOT_RUN',
                                   'lobby_only_status': 'OBSERVED' if subsets['lobby_frames'] else 'NOT_RUN',
                                   'gallery_list_status': 'OBSERVED' if subsets['gallery_list_frames'] else 'NOT_RUN',
                                   'hero_detail_status': 'OBSERVED' if subsets['hero_detail_frames'] else 'NOT_RUN',
                                   'unclassified_frames': sum(row.get('frontend_page') not in PAGES for row in frontend),
                                   'reason': 'Separate pages use only the actual frontend_page column. Older CSVs support combined namespace0/phase-1 only. Mode may include truthful entry transitions; closed frames are not attributed to a visible page.'},
        'subsets': {}, 'inputs': inputs,
    }
    for name, selected in subsets.items():
        measurement = {'frames': len(selected)}
        for field in TIMINGS:
            available = [row[field] for row in selected if row.get(field) is not None and math.isfinite(row[field])
                         and (row[field] > 0 if field in ('frame_ms', 'gpu_ms') else row[field] >= 0)
                         and (field != 'gpu_ms' or not null_rhi and row.get('gpu_available') == 1)]
            measurement[field] = {**metrics(available), 'unavailable_or_invalid_samples': len(selected) - len(available)}
        result['subsets'][name] = measurement
    result['required_busy_load_status'] = 'OBSERVED' if subsets['twelve_visible_and_four_live_encounters'] else 'NOT_RUN'
    result['eight_neutral_encounters_status'] = 'OBSERVED' if eight_neutral else 'NOT_RUN'
    result['eight_neutral_encounters_definition'] = 'Combat phase with neutral_round=1, neutral_live_encounters=8 and total unfinished encounters=8. No inference from a round number or participant count.'
    result['neutral_instrumentation_available'] = neutral_available
    result['combat_kind_unclassified_frames'] = len(combat) - len(neutral) - len(pvp)
    result['viewport_1080p_observed'] = bool(rows) and not null_rhi and session.get('resolution_x') == 1920 and session.get('resolution_y') == 1080
    if not rows:
        result['not_run_reason'] = 'Frame CSV missing.' if missing_frame_file else 'Frame CSV contains a header but no recorded timing rows.'
        if launch and '-wcprofile' not in options:
            result['not_run_reason'] += ' Launch arguments do not enable -WCProfile.'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--context-evidence', type=Path, action='append', default=[], help='Bind a workload/launch JSON as preliminary context; not causal attribution')
    args = parser.parse_args()
    report = summarize(args.session, args.context_evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': report['status'], 'frames': report['source']['rows'],
                      'required_busy_load_status': report['required_busy_load_status'],
                      'eight_neutral_encounters_status': report['eight_neutral_encounters_status'],
                      'viewport_1080p_observed': report['viewport_1080p_observed'], 'output': str(args.output)}, indent=2))

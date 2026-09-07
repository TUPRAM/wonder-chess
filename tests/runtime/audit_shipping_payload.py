"""Read-only current Shipping identity checks shared by network evidence auditors."""
from pathlib import Path
import hashlib
import json


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def payload_checks(trial):
    checks = []

    def check(name, passed, detail):
        checks.append({'check': name, 'status': 'PASS' if passed else 'FAIL', 'detail': detail})

    path = Path(trial['provenance_path'])
    provenance = json.loads(path.read_text(encoding='utf-8-sig'))
    check('manifest_identity_matches_launch', digest(path) == trial.get('provenance_sha256'), str(path))
    root = Path(provenance['package_root']).resolve()
    payload = [row for row in provenance['files'] if row.get('group') == 'packaged_payload']
    check('stable_successful_packaging_provenance', provenance.get('input_files_stable_during_capture') is True
          and provenance.get('package_report', {}).get('exit_code') == 0, provenance.get('configuration'))
    expected = set()
    errors = []
    for row in payload:
        source = Path(row['path']).resolve()
        if not source.is_relative_to(root) or source in expected:
            errors.append({'path': str(source), 'error': 'Outside package or duplicate entry'})
            continue
        expected.add(source)
        if not source.is_file():
            errors.append({'path': str(source), 'error': 'Missing payload'})
            continue
        before = source.stat()
        actual = digest(source)
        after = source.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or actual != row['sha256'] or after.st_size != row['bytes']:
            errors.append({'path': str(source), 'error': 'Payload changed', 'actual_sha256': actual})
    actual_paths = {source.resolve() for source in root.rglob('*') if source.is_file()
                    and 'saved' not in [part.casefold() for part in source.relative_to(root).parts]}
    check('all_packaged_payload_bytes_still_match', bool(payload) and not errors,
          {'file_count': len(payload), 'errors': errors})
    check('packaged_payload_membership_unchanged', bool(payload) and actual_paths == expected,
          {'missing': sorted(map(str, expected - actual_paths)), 'unexpected': sorted(map(str, actual_paths - expected)),
           'excluded': 'Runtime Saved directories'})
    preflight = trial.get('payload_verification') or {}
    recorded = {(str(Path(row['path']).resolve()), row['sha256'], row['bytes']) for row in preflight.get('files', [])}
    required = {(str(Path(row['path']).resolve()), row['sha256'], row['bytes']) for row in payload}
    check('complete_payload_preflight_recorded_before_launch', preflight.get('status') == 'PASS'
          and recorded == required and preflight.get('file_count') == len(payload),
          {'recorded_count': len(recorded), 'required_count': len(required), 'verified_utc': preflight.get('verified_utc')})
    return provenance, checks


def catalog_checks(sessions, provenance):
    checks = []
    for label, session in sessions:
        public = session.get('public_snapshot', {})
        public = json.loads(public) if isinstance(public, str) and public else public
        actual = {key: public.get(key) for key in ('schemaVersion', 'protocolVersion', 'contentDigest')}
        checks.append({'check': label + '_received_current_catalog_protocol',
                       'status': 'PASS' if actual['schemaVersion'] == '3.1.0' and actual['protocolVersion'] == 6
                       and bool(provenance.get('catalog_digest')) and actual['contentDigest'] == provenance['catalog_digest'] else 'FAIL',
                       'detail': {'received': actual, 'provenance_catalog_digest': provenance.get('catalog_digest'),
                                  'boundary': 'Actual received schema/protocol and full catalog digest; not hero art acceptance.'}})
    return checks


def round_kind(public):
    """Report the replicated flag; never infer observed combat from a round number."""
    phase = public.get('phase', -1)
    neutral = public.get('neutralRound')
    return {'phase': phase, 'round': public.get('round'),
            'phase_name': {-1: 'menu_or_entry', 0: 'preparation', 1: 'combat', 2: 'settlement', 3: 'results'}.get(phase, 'unknown'),
            'round_kind': 'neutral' if neutral is True else 'pvp' if neutral is False else 'unknown',
            'source': 'actual replicated neutralRound flag'}

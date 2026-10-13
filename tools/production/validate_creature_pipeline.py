"""Read-only checks for the reusable handbook and unfilled record templates.

This validates documentation integrity, not creature quality, rights or approval.
It never starts a provider job, editor, build, network request or installation.
"""
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'production/creature-pipeline'
SKILL = ROOT / '.agents/skills/wc-creature-production'
RIG_SKILL = ROOT / '.agents/skills/wc-creature-rigging'


def validate():
    errors = []
    paths = sorted([*PACK.rglob('*.md'), *SKILL.rglob('*.md'), *RIG_SKILL.rglob('*.md')])
    required = ['README.md', 'VISUAL_STANDARD.md', 'MESHY.md', 'FOUR_VIEW.md', 'CHARACTER_BRIEFS.md',
                'UNREAL_RIG_AND_VALIDATION.md', 'AUDIO.md', 'ACCEPTANCE.md', 'ENGINEERING.md',
                'TOOLCHAIN.md', 'templates/README.md', 'ANIMATION_READY.md',
                'TEXTURE_DEVELOPMENT.md', 'SKILLS_ROADMAP.md']
    if not (RIG_SKILL / 'SKILL.md').is_file():
        errors.append('Missing creature rigging skill')
    for name in required:
        if not (PACK / name).is_file():
            errors.append(f'Missing manual: {name}')
    checked_links = 0
    for path in paths:
        content = path.read_text(encoding='utf-8')
        for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            target = raw.strip().strip('<>')
            if target.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            target = unquote(target.split('#', 1)[0])
            if not target:
                continue
            destination = (path.parent / target).resolve()
            checked_links += 1
            if not destination.is_relative_to(ROOT):
                errors.append(f'Nonportable local link: {path.relative_to(ROOT)} -> {raw}')
            elif not destination.exists():
                errors.append(f'Broken local link: {path.relative_to(ROOT)} -> {raw}')
    parsed = {}
    for path in sorted((PACK / 'templates').glob('*.json')):
        try:
            parsed[path.name] = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            errors.append(f'Invalid JSON {path.name}: {exc}')
    candidate = parsed.get('candidate.json', {})
    if candidate.get('record_kind') != 'unfilled_template' or candidate.get('complete_for_intended_use') is not False:
        errors.append('Candidate template must remain explicitly incomplete.')
    if set(candidate.get('stages', {})) != {f'G{i}' for i in range(9)}:
        errors.append('Candidate must enumerate G0 through G8.')
    for name, stage in candidate.get('stages', {}).items():
        if stage != {'status': 'not_started', 'evidence': [], 'decision': None}:
            errors.append(f'Template stage {name} must not contain execution/approval evidence.')
    if candidate.get('approvals') or candidate.get('permissions', {}).get('new_credit_authorization_from_template') != 0:
        errors.append('Template must not grant approval or credits.')
    receipt = parsed.get('generation-receipt.json', {})
    if receipt.get('status') != 'not_submitted' or receipt.get('job_id') is not None:
        errors.append('Generation template must not claim a submitted task.')
    for field in ('maximum_jobs', 'maximum_credits', 'maximum_currency_cost'):
        if receipt.get('permission', {}).get(field) != 0:
            errors.append(f'Generation template must not authorize {field}.')
    look = parsed.get('lighting-profile.json', {})
    if look.get('status') != 'not_run' or look.get('owner_approval') is not None:
        errors.append('Lighting template must not imply an approved or implemented profile.')
    view_set = parsed.get('view-set.json', {})
    if (view_set.get('record_kind') != 'unfilled_template'
            or view_set.get('review_status') != 'not_run'
            or view_set.get('owner_approval') is not None
            or view_set.get('ready_for_submission') is not False):
        errors.append('Four-view template must remain unreviewed and not ready for submission.')
    expected_views = [('main', 'Main View', 'front'), ('left', 'Left', 'anatomical_left'),
                      ('back', 'Back', 'rear'), ('right', 'Right', 'anatomical_right')]
    views = view_set.get('views', [])
    if not isinstance(views, list) or any(not isinstance(v, dict) for v in views):
        errors.append('Four-view template views must be a list of records.')
        views = []
    if [(v.get('slot'), v.get('ui_label'), v.get('anatomical_view')) for v in views] != expected_views:
        errors.append('Four-view template must define Main/front, Left, Back and Right exactly once in order.')
    for view in views:
        if (view.get('file') is not None or view.get('sha256') is not None
                or view.get('origin_kind') is not None or view.get('view_review') != 'not_run'):
            errors.append('Four-view template must not contain invented images, origins, hashes or reviews.')
    if candidate.get('fixed_owner_choices', {}).get('new_geometry_input_mode') != 'meshy_four_view':
        errors.append('Candidate template must retain the four-view default for new geometry.')
    expected_checkpoints = {'G3A_construction', 'G3B_deformation', 'G3C_uv_bake',
                            'controlled_revision', 'cold_reopen', 'fresh_recovery'}
    checkpoints = candidate.get('engineering_checkpoints', {})
    if set(checkpoints) != expected_checkpoints or any(
            x != {'status': 'not_run', 'record': None} for x in checkpoints.values()):
        errors.append('Engineering checkpoint templates must exist and remain unexecuted.')
    for name in ('camera-set.json', 'uv-bake.json', 'budget-profile.json', 'revision-recovery.json',
                 'source-preflight.json', 'unreal-contracts.json'):
        if parsed.get(name, {}).get('record_kind') != 'unfilled_template':
            errors.append('Missing or filled engineering template: ' + name)
    cameras = parsed.get('camera-set.json', {})
    if cameras.get('status') != 'not_run' or cameras.get('owner_approval') is not None:
        errors.append('Camera template must not imply executed capture or approval.')
    if [(x.get('slot'), x.get('camera_side')) for x in cameras.get('views', [])] != [
            ('main', '+X'), ('left', '-Y'), ('back', '-X'), ('right', '+Y')]:
        errors.append('Camera template must preserve the four anatomical directions.')
    if any(v is not None for v in parsed.get('budget-profile.json', {}).get('limits', {}).values()):
        errors.append('Budget template must not invent selected/measured limits.')
    if parsed.get('unreal-contracts.json', {}).get('contracts') != {}:
        errors.append('Unreal template must not contain invented live contracts.')
    csv_files = list((PACK / 'templates').glob('*.csv'))
    for path in csv_files:
        rows = list(csv.reader(io.StringIO(path.read_text(encoding='utf-8'))))
        if len(rows) != 1 or not rows[0] or len(rows[0]) != len(set(rows[0])):
            errors.append(f'CSV must have unique header fields and no fabricated rows: {path.name}')
    return {'status': 'PASS_DOCUMENTATION_INTEGRITY' if not errors else 'FAIL',
            'scope': 'Local links, required manuals, parseable unfilled templates and absence of default approvals/spend. External links, art quality and runtime behavior are not certified.',
            'manuals_checked': len(paths), 'local_links_checked': checked_links,
            'json_templates': len(parsed), 'csv_templates': len(csv_files), 'errors': errors,
            'file_hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted([*PACK.rglob('*'), *SKILL.rglob('*'), *RIG_SKILL.rglob('*')]) if p.is_file()}}


if __name__ == '__main__':
    result = validate()
    print(json.dumps(result, indent=2))
    sys.exit(0 if not result['errors'] else 1)

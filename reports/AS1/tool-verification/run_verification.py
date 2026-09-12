"""Local AS1 helper smoke on new fixture data; never opens any Ada source."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BLENDER = Path('C:/Program Files/Blender Foundation/Blender 5.1/blender.exe')
RUNNER = REPO / 'production/asset-studio/tools/asset_studio/run_blender.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def call(args, log_name, expected=0):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True, errors='replace', timeout=240)
    (ROOT / log_name).write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
    if result.returncode != expected:
        raise RuntimeError(f'{log_name}: expected {expected}, got {result.returncode}; inspect log')
    return {'command': [str(x) for x in args], 'exit_code': result.returncode, 'log': log_name}


def helper(source, name, log, arguments, expected=0):
    return call([sys.executable, RUNNER, '--blender', BLENDER, '--source', source,
                 '--tool', name, '--execute', '--timeout', '180', '--log', ROOT / log, '--', *arguments],
                log + '.runner.txt', expected)


def main():
    from PIL import Image, ImageDraw
    assert not (ROOT / 'fixture.blend').exists(), 'Use a fresh fixture destination.'
    image = Image.new('RGB', (320, 512), '#e3e7ec')
    draw = ImageDraw.Draw(image)
    for x in range(0, 320, 32):
        draw.line((x, 0, x, 511), fill='#a9b7c7')
    for y in range(0, 512, 32):
        draw.line((0, y, 319, y), fill='#a9b7c7')
    draw.line((160, 32, 160, 480), fill='#c92124', width=3)
    draw.line((32, 480, 288, 480), fill='#263644', width=3)
    draw.text((14, 12), 'AS1 HELPER FIXTURE / NO CHARACTER', fill='#122535')
    image.save(ROOT / 'reference-fixture.png')
    spec = {'status': 'calibrated_candidate', 'purpose': 'Synthetic tool test, never Ada reference approval',
            'views': [{'path': 'reference-fixture.png', 'image_sha256': sha(ROOT / 'reference-fixture.png'),
                       'part_id': 'tool_fixture', 'view': 'front', 'width_px': 320, 'height_px': 512,
                       'ground_y_px': 480, 'top_y_px': 32, 'center_x_px': 160,
                       'declared_height_m': 1.82, 'display_size_m': 1.82 * 512 / 448,
                       'matrix_world': [[1, 0, 0, 0], [0, 0, -1, 0.5], [0, 1, 0, 0.91], [0, 0, 0, 1]]}]}
    write_json(ROOT / 'reference-calibration.json', spec)
    bad = json.loads(json.dumps(spec))
    bad['views'][0]['image_sha256'] = '0' * 64
    write_json(ROOT / 'reference-bad-hash.json', bad)
    write_json(ROOT / 'review-cameras.json', {
        'engine': 'CYCLES', 'samples': 8, 'resolution': [384, 384], 'center': [0.2, 0, 0.85],
        'height_m': 1.82, 'ortho_scale': 2.6,
        'views': [{'id': 'front', 'location': [0.2, -5, 0.85]},
                  {'id': 'three-quarter', 'location': [3, -5, 2.4]}]})
    creation = call([BLENDER, '--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '23',
                     '--python', ROOT / 'create_fixture.py', '--', ROOT], 'create-fixture.log')
    source = ROOT / 'fixture.blend'
    initial_sha = sha(source)
    commands = [creation]
    commands.append(call([sys.executable, RUNNER, '--blender', BLENDER, '--source', source, '--tool', 'scene_audit',
                          '--', '--collection', 'AS1_FIXTURE', '--output', ROOT / 'dry-run-must-not-exist.json'],
                         'dry-run.json'))
    assert not (ROOT / 'dry-run-must-not-exist.json').exists()
    commands.append(helper(source, 'reference_setup', 'reference-setup.log', [
        '--workspace', ROOT, '--spec', ROOT / 'reference-calibration.json', '--output-blend', ROOT / 'fixture-with-references.blend']))
    commands.append(helper(source, 'reference_setup', 'reference-reject.log', [
        '--workspace', ROOT, '--spec', ROOT / 'reference-bad-hash.json', '--output-blend', ROOT / 'rejected-must-not-exist.blend'], 23))
    assert not (ROOT / 'rejected-must-not-exist.blend').exists()
    references = ROOT / 'fixture-with-references.blend'
    ref_sha = sha(references)
    commands.append(helper(references, 'scene_audit', 'scene-audit.log', ['--collection', 'AS1_FIXTURE', '--output', ROOT / 'scene-audit.json']))
    audit = json.loads((ROOT / 'scene-audit.json').read_text())
    rows = {o['name']: o for o in audit['objects']}
    assert rows['FixtureWeightedBox']['unweighted_vertices'] == 0
    assert rows['FixtureWeightedBox']['non_normalized_vertices'] == 0
    assert rows['FixtureWeightedBox']['max_deform_influences'] == 1
    assert rows['FixtureRig']['deform_bones'] == 1
    assert rows['FixtureSphere']['unweighted_vertices'] is None
    assert rows['FixtureSphere']['triangles_evaluated'] > 0
    assert all(r['degenerate_source_triangles'] == 0 for r in rows.values() if r['type'] == 'MESH')
    assert any(im['size'] == [320, 512] and im['external_file_exists'] for im in audit['file_images'])
    for kind in ('material', 'clay'):
        args = ['--collection', 'AS1_FIXTURE', '--cameras', ROOT / 'review-cameras.json', '--out', ROOT / ('renders-' + kind)]
        if kind == 'clay':
            args.append('--clay')
        commands.append(helper(references, 'render_review', 'render-' + kind + '.log', args))
        for view in ('front', 'three-quarter'):
            with Image.open(ROOT / ('renders-' + kind) / (view + '.png')) as capture:
                assert capture.size == (384, 384)
    assert sha(source) == initial_sha
    assert sha(references) == ref_sha
    helper_sources = sorted((RUNNER.parent / 'blender').glob('*.py')) + [RUNNER]
    write_json(ROOT / 'execution-results.json', {
        'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'New factory-startup calibration fixture only; never Ada or active GUI scene',
        'status': 'helper_execution_smoke_pass_visual_review_recorded_separately',
        'blender': str(BLENDER), 'commands': commands,
        'fixture_sha256': initial_sha, 'reference_fixture_sha256': ref_sha,
        'source_files_unchanged': True,
        'helper_hashes': {str(p.relative_to(REPO)): sha(p) for p in helper_sources},
        'claims_not_made': ['Ada art approval', 'rig quality', 'Unreal import', 'reimport', 'packaged gameplay']})
    print('AS1 fixture smoke completed; actual images still require inspection.')


if __name__ == '__main__':
    main()

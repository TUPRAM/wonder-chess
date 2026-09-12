"""Preserve native r002 pixels and build a new reference-only Blender candidate."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSET = ROOT.parents[2]
REPO = ASSET.parents[2]
BLENDER = Path('C:/Program Files/Blender Foundation/Blender 5.1/blender.exe')
TOOLS = REPO / 'production/asset-studio/tools/asset_studio'
source_image = ROOT.parent / 'ada_construction_r002.png'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(args, logfile, expected=0):
    args = list(map(str, args))
    proc = subprocess.run(args, capture_output=True, text=True, errors='replace', timeout=120)
    (ROOT / logfile).write_text(proc.stdout + '\n' + proc.stderr)
    if proc.returncode != expected:
        raise RuntimeError(f'{logfile}: {proc.returncode}; inspect output before retry')
    return {'command': args, 'exit_code': proc.returncode, 'log': str((ROOT / logfile).relative_to(ASSET))}


def main():
    assert ROOT.name == 'blender_r001' and ASSET.name == 'wc_u_human_guardian'
    assert not (ROOT / 'ada_reference_empty_source_r001.blend').exists()
    with Image.open(source_image) as im:
        assert im.size == (1658, 949)
    choices = [
        ('front', [45, 45, 460, 850], 69, 833, 255, (-1, 0, 0), (0, .75, 0), 'observer +Y looking -Y'),
        ('left', [545, 45, 755, 850], 69, 825, 650, (0, -1, 0), (-.75, 0, 0), 'observer -X looking +X; anatomical left'),
        ('back', [835, 45, 1240, 850], 68, 827, 1035, (1, 0, 0), (0, -.75, 0), 'observer -Y looking +Y'),
        ('right', [1300, 45, 1525, 850], 69, 826, 1404, (0, 1, 0), (.75, 0, 0), 'observer +X looking -X; anatomical right'),
    ]
    boxes = {'crops': [{'id': 'body-' + name, 'box_xyxy': box,
                       'meaning': name + ' construction candidate body panel',
                       'notes': 'Native r002 pixels; no resampling, no orthographic certification; rear split governed separately.'}
                      for name, box, *_ in choices]}
    write_json(ROOT / 'crop_plan_r001.json', boxes)
    operations = [call([sys.executable, TOOLS / 'image_review.py', 'crop', '--image', source_image,
                       '--boxes', ROOT / 'crop_plan_r001.json', '--out', ROOT / 'native-crops'], 'crop.log')]
    views = []
    for name, box, crown, sole, axis, u, offset, direction in choices:
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        mpp = 1.82 / (sole - crown)
        dx = (w / 2 - (axis - x0)) * mpp
        dz = (sole - y0 - h / 2) * mpp
        tx, ty = offset[0] + u[0] * dx, offset[1] + u[1] * dx
        normal = (u[1], -u[0], 0)
        matrix = [[u[0], 0, normal[0], tx], [u[1], 0, normal[1], ty], [0, 1, 0, dz], [0, 0, 0, 1]]
        crop = ROOT / 'native-crops' / ('body-' + name + '.png')
        views.append({
            'path': str(crop.relative_to(ASSET)).replace('\\', '/'), 'image_sha256': sha(crop),
            'part_id': 'body', 'view': name, 'image_dimensions_px': [w, h],
            'source_crop_xyxy': box, 'crown_source_y_px': crown, 'sole_source_y_px': sole,
            'centerline_source_x_px': axis, 'meters_per_pixel': mpp,
            'display_size_m': max(w, h) * mpp, 'matrix_world': matrix, 'view_direction': direction,
            'calibration_method': 'Uniform whole-image scale, manually interpreted centerline; crown/sole dark-pixel extent measured in source body band.',
            'landmark_uncertainty_px': 3})
    spec = {'status': 'calibrated_candidate', 'asset_id': 'wc_u_human_guardian', 'height_m': 1.82,
            'source_image': str(source_image.relative_to(ASSET)).replace('\\', '/'), 'source_image_sha256': sha(source_image),
            'source_image_dimensions_px': [1658, 949], 'source_forward': '+Y', 'source_up': '+Z',
            'anatomical_left': '-X', 'anatomical_right': '+X',
            'projection_status': 'Generated artwork; no mathematical orthographic certification.',
            'landmark_measurement': 'At least 3 body-band pixels with max(R,G,B)<110 per row; crown/sole endpoints visually inspected. Side centerline is a construction choice.',
            'rear_panel_authority': 'r002 is a hem-length candidate; original back reference plus proposed construction decisions control center split.',
            'views': views}
    write_json(ROOT / 'calibration_r001.json', spec)
    operations.append(call([BLENDER, '--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '23',
                            '--python', ROOT / 'create_empty_source.py', '--', ROOT], 'create_empty_source.log'))
    source = ROOT / 'ada_reference_empty_source_r001.blend'
    source_sha = sha(source)
    raw = ROOT / 'ada_reference_import_candidate_r001.blend'
    operations.append(call([sys.executable, TOOLS / 'run_blender.py', '--blender', BLENDER, '--source', source,
                            '--tool', 'reference_setup', '--execute', '--timeout', '120', '--log', ROOT / 'reference_setup.log',
                            '--', '--workspace', ASSET, '--spec', ROOT / 'calibration_r001.json', '--output-blend', raw,
                            '--collection', 'AS1_REFERENCES_R001'], 'reference_setup_runner.log'))
    raw_sha = sha(raw)
    operations.append(call([BLENDER, '--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '23', raw,
                            '--python', ROOT / 'lock_and_inspect_reference_scene.py', '--', ROOT], 'lock_inspect.log'))
    assert sha(source) == source_sha and sha(raw) == raw_sha
    final = ROOT / 'ada_reference_scene_r001.blend'
    operations.append(call([sys.executable, TOOLS / 'run_blender.py', '--blender', BLENDER, '--source', final,
                            '--tool', 'scene_audit', '--execute', '--timeout', '120', '--log', ROOT / 'scene_audit.log',
                            '--', '--collection', 'AS1_REFERENCES_R001', '--output', ROOT / 'as1_reference_audit_r001.json'], 'scene_audit_runner.log'))
    observed = json.loads((ROOT / 'saved_scene_audit_r001.json').read_text())
    assert sha(final) == observed['candidate_sha256']
    assert observed['mesh_objects'] == observed['armature_objects'] == observed['camera_objects'] == 0
    report = {
        'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'executed_reference_placement_owner_approval_pending', 'operations': operations,
        'source': str(source.relative_to(ASSET)).replace('\\', '/'), 'source_sha256': source_sha,
        'import_candidate': str(raw.relative_to(ASSET)).replace('\\', '/'), 'import_candidate_sha256': raw_sha,
        'final': str(final.relative_to(ASSET)).replace('\\', '/'), 'final_sha256': sha(final),
        'source_files_unchanged_after_import_review': True, 'scene_observations': observed,
        'source_image_sha256': sha(source_image), 'calibration_sha256': sha(ROOT / 'calibration_r001.json'),
        'reference_setup_helper_sha256': sha(TOOLS / 'blender/reference_setup.py'),
        'runner_sha256': sha(TOOLS / 'run_blender.py'),
        'human_approval': False, 'orthographic_image_certification': False,
        'modeling_started': False, 'old_ada_source_loaded': False}
    write_json(ASSET / 'reports/reference_scene_execution_r001.json', report)
    print('REFERENCE-ONLY CANDIDATE EXECUTED; ZERO CHARACTER MESHES; OWNER REFERENCE APPROVAL PENDING')


if __name__ == '__main__':
    main()

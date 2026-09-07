"""Render retained Orc candidates at native 60fps using the proven Workbench path."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/blender'))
from refine_update_ada import sha
from refine_update_dwarves import audit_and_record

parser = argparse.ArgumentParser()
parser.add_argument('--unit', choices=('wc_u_orc_warrior', 'wc_u_orc_mage', 'wc_u_orc_rogue'), required=True)
parser.add_argument('--candidate-dir', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
candidate_dir = args.candidate_dir.resolve()
out = candidate_dir / 'workbench-review'
out.mkdir(exist_ok=False)
for name in ('refinement.json', 'before-source.blend', 'before-export-manifest.json',
             'after-front.png', 'after-side.png', 'after-back.png', 'after-three-quarter.png'):
    shutil.copy2(candidate_dir / name, out / name)
refined = json.loads((out / 'refinement.json').read_text())
assert refined['unit_id'] == args.unit and sha(Path(refined['candidate'])) == refined['candidate_sha256']
unit = next(item for item in json.loads((ROOT / 'data/units.json').read_text(encoding='utf-8'))['units'] if item['id'] == args.unit)
shutil.copy2(Path(__file__), out / 'executed-review.py')
shutil.copy2(ROOT / 'tools/blender/refine_update_dwarves.py', out / 'executed-workbench-helper.py')
audit_and_record(unit, out)
assert sha(Path(refined['candidate'])) == refined['candidate_sha256']
print('WC_ORC_NATIVE_FRAME_REVIEW_RENDERED ' + args.unit, flush=True)
